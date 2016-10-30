#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import xml.etree.ElementTree as ET
import hashlib
import time

import requests

from config import WEIXIN_APPID, WEIXIN_SECRET, WEIXIN_TOKEN
from app import logger
from cache.weixin import get_cache_access_token, cache_access_token, cache_ticket, get_cache_ticket
from wexin.util import nonce_str


api_host = "https://api.weixin.qq.com"
qrcode_host = "https://mp.weixin.qq.com"


class WeixinException(Exception):
    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg
        self.message = errmsg

    def __str__(self):
        return '%s-%s' % (self.errcode, self.errmsg)


class Request(object):
    def __init__(self, token, host):
        self.host = host
        self.token = token
        self.errcode = 0
        self.errmsg = ''

    def get_access_token(self):
        return self.token.get()

    def request(self, url, params, data=None, method='GET', headers=None, times=2, sleep_second=0.5):
        if not headers:
            headers = {'Content-Type': 'application/json'}
        if not data:
            data = {}
        while times:
            try:
                response = self._request(url, params, data, method, headers)
                times -= 1
                if "errcode" not in response or response["errcode"] == 0:
                    return response
                self.errcode = response["errcode"]
                self.errmsg = response["errmsg"]
                logger.error('[WEIXIN] request error[%d], detail:%s' % (self.errcode, self.errmsg))
                if response["errcode"] in [42001, 40001]:
                    params['access_token'] = self.token.refresh()
                    time.sleep(sleep_second)
                else:
                    break
            except Exception, e:
                self.errcode = 255
                self.errmsg = e.message
                logger.error('[WEIXIN] request error[%s]' % e.message)
        return {"errcode":self.errcode, "errmsg":self.errmsg}
        # raise WeixinException(self.errcode, self.errmsg)

    def _request(self, url, params, data, method, headers):
        url = '%s%s?%s' % (self.host, url, urllib.urlencode(params))
        response = None
        if method == 'GET':
            response = urllib2.urlopen(url).read()
        elif method == 'POST':
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req).read()
        return response


class APIRequest(Request):
    def __init__(self, token, host=api_host):
        super(APIRequest, self).__init__(token, host)

    def _request(self, url, params, data, method, headers):
        data = json.dumps(data, ensure_ascii=False)
        data = data.encode('UTF-8')
        response = super(APIRequest, self)._request(url, params, data, method, headers)
        response = json.loads(response)
        return response


class Token(object):
    def get(self):
        return get_cache_access_token() or self._create()

    def refresh(self):
        return self._create()

    def _create(self):
        r = requests.get("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" +
                         WEIXIN_APPID + "&secret=" + WEIXIN_SECRET, verify=False)
        response = r.json()
        cache_access_token(response["access_token"], response["expires_in"])
        logger.info('[WEIXIN][Token_create] appid=%s, secret=%s, new token=%s, expires=%s' % (
            WEIXIN_APPID, WEIXIN_SECRET, response["access_token"], response["expires_in"]))
        return response["access_token"]


class Qrcode(object):
    def __init__(self, request):
        self.request = request

    def show(self, ticket):
        url = "/cgi-bin/showqrcode"
        params = {"ticket": ticket}
        # data = {"filepath":filepath}
        # r = self.request.request(url,params,data)
        img = self.request.request(url, params)
        return img


class WeixinHelper(object):
    def __init__(self):
        self.token = Token()
        self.request = APIRequest(self.token)

    @staticmethod
    def check_signature(signature, timestamp, nonce):
        tmplist = [WEIXIN_TOKEN, timestamp, nonce]
        tmplist.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, tmplist)
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return
        raise WeixinException(0, "check_signature failed")

    @staticmethod
    def to_json(message):
        j = {}
        root = ET.fromstring(message)
        for child in root:
            if child.tag == 'CreateTime':
                value = long(child.text)
            else:
                value = child.text
            j[child.tag.lower()] = value
        return j

    @staticmethod
    def _cdata(data):
        """
        http://stackoverflow.com/questions/174890/how-to-output-cdata-using-elementtree
        """
        if type(data) is str:
            return '<![CDATA[%s]]>' % data.replace(']]>', ']]]]><![CDATA[>')
        return data

    def to_xml(self, message):
        xml = '<xml>'

        def cmp(x, y):
            """
            WeiXin need ordered elements?
            """
            orderd = ['to_user_name', 'from_user_name', 'create_time', 'msg_type', 'content', 'func_flag']
            try:
                ix = orderd.index(x)
            except ValueError:
                return 1
            try:
                iy = orderd.index(y)
            except ValueError:
                return -1
            return ix - iy

        for k in sorted(message.iterkeys(), cmp):
            v = message[k]
            tag = ''.join([w.capitalize() for w in k.split('_')])
            xml += '<%s>%s</%s>' % (tag, self._cdata(v), tag)
        xml += '</xml>'
        return xml

    def send_custom_message(self, message):
        url = "/cgi-bin/message/custom/send"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params, message, 'POST')
        logger.info(str(response))
        return response

    def push_template_message(self, openid, template_id, push_data, push_url):
        url = '/cgi-bin/message/template/send'
        params = {"access_token": self.request.get_access_token()}
        post_contents = {
            "touser": openid,
            "template_id": template_id,
            "url": push_url,
            "topcolor": "#7B68EE",
            "data": push_data
        }
        response = self.request.request(url, params, post_contents, 'POST')
        logger.info(str(response))


    def create_group(self, group):
        """
        {"group":{"name":"test"}}
        """
        url = "/cgi-bin/groups/create"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params, group, 'POST')
        if "group" in response:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def get_group(self):
        """
        https://api.weixin.qq.com/cgi-bin/groups/get?access_token=ACCESS_TOKEN
        """
        url = "/cgi-bin/groups/get"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params)
        if "groups" in response:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def get_user_info(self, openid, lang="zh_CN"):
        """
        https://api.weixin.qq.com/cgi-bin/user/info?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
        """
        url = "/cgi-bin/user/info"
        params = {
            "access_token": self.request.get_access_token(),
            "openid": openid,
            "lang": lang
        }
        response = self.request.request(url, params)
        if "errcode" in response:
            errcode = response["errcode"]
            errmsg = response["errmsg"]
            raise WeixinException(errcode, errmsg)
        else:
            return response

    def get_follow_users(self, next_openid=""):
        """
        https://api.weixin.qq.com/cgi-bin/user/get?access_token=ACCESS_TOKEN&next_openid=NEXT_OPENID
        """
        url = "/cgi-bin/user/get"
        params = {
            "access_token": self.request.get_access_token(),
            "next_openid": next_openid
        }
        response = self.request.request(url, params)
        if "errcode" in response:
            errcode = response["errcode"]
            errmsg = response["errmsg"]
            raise WeixinException(errcode, errmsg)
        return response

    def get_groupid_by_openid(self, openid):
        """
        {"openid":"od8XIjsmk6QdVTETa9jLtGWA6KBc"}
        """
        url = "/cgi-bin/groups/getid"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params, openid, 'POST')
        if 'groupid' in response:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def update_group(self, group):
        """
        https://api.weixin.qq.com/cgi-bin/groups/update?access_token=ACCESS_TOKEN
        {"group":{"id":108,"name":"test2_modify2"}}
        """
        url = "/cgi-bin/groups/update"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params, group, 'POST')
        if response['errcode'] == 0:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def update_group_member(self, member):
        """
         https://api.weixin.qq.com/cgi-bin/groups/members/update?access_token=ACCESS_TOKEN
         {"openid":"oDF3iYx0ro3_7jD4HFRDfrjdCM58","to_groupid":108}
        """
        url = "/cgi-bin/groups/members/update"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params, member, 'POST')
        if response['errcode'] == 0:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def create_menu(self, menu):
        url = "/cgi-bin/menu/create"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params, menu, 'POST')
        return response

    def get_menu(self):
        """
        https://api.weixin.qq.com/cgi-bin/menu/get?access_token=ACCESS_TOKEN
        """
        url = "/cgi-bin/menu/get"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params)
        if "menu" in response:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def delete_menu(self):
        """
        https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=ACCESS_TOKEN
        """
        url = "/cgi-bin/menu/delete"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params)
        if response['errcode'] == 0:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def create_qrcode(self, json):
        """ https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=TOKEN
        # {"expire_seconds": 1800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": 123}}}
        # {"action_name": "QR_LIMIT_SCENE", "action_info": {"scene": {"scene_id": 123}}} """
        url = "/cgi-bin/qrcode/create"
        params = {"access_token": self.request.get_access_token()}
        resp = self.request.request(url, params, json, 'POST')
        if "ticket" in resp:
            return resp
        raise 401

    def oauth(self, code):
        token_url = "/sns/oauth2/access_token"
        token_params = {
            "appid": WEIXIN_APPID,
            "secret": WEIXIN_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        }
        return self.request.request(token_url, token_params)

    def oauth_user(self, code):
        resp = self.oauth(code)
        openid = resp["openid"]
        if openid:
            return {'errcode': 0, 'openid': openid}
        return {'errcode': '255', 'error': 'oauth exception'}

    # type= jsapi, wx_card
    def get_ticket(self, type='jsapi'):
        token = get_cache_ticket(type)
        if not token:
            access_token = self.token.get()
            r = requests.get("https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=" +
                             access_token + "&type=" + type, verify=False)
            res = r.json()
            if res['errcode'] != 0:
                access_token = self.token.refresh()
                r = requests.get("https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=" +
                                 access_token + "&type=jsapi", verify=False)
                res = r.json()
                logger.info('[get_ticket] token=%s, new ticket=%s' % (access_token, res['ticket']))
                cache_ticket(type, res['ticket'], res['expires_in'])
                return res['ticket']
            else:
                logger.info('[get_ticket] token=%s, ticket=%s' % (access_token, res['ticket']))
                cache_ticket(type, res['ticket'], res['expires_in'])
                return res['ticket']
        logger.info('[get_ticket] ticket=%s' % token)
        return token

    def jsapi_sign(self, url):
        s = nonce_str()
        timestamp = int(time.time())
        js_ticket = self.get_ticket('jsapi')
        full_url = "jsapi_ticket=" + js_ticket + "&noncestr=" + s + "&timestamp=" + str(timestamp) + "&url=" + url
        sha1obj = hashlib.sha1()
        sha1obj.update(full_url)
        hash = sha1obj.hexdigest()
        return {
            "nonce_str": s,
            "hash": hash,
            "timestamp": timestamp,
            "ticket": js_ticket
        }

    # add card
    def card_sign(self, card_id=None, code=None, openid=None):
        # nonce = nonce_str()
        timestamp = str(int(time.time()))
        card_ticket = self.get_ticket('wx_card')
        items = [card_id, timestamp, card_ticket]
        code and items.append(code)
        openid and items.append(openid)
        items_str = ''.join(sorted(items))
        sha1obj = hashlib.sha1()
        sha1obj.update(items_str)
        signature = sha1obj.hexdigest()
        return {
            # "nonce_str": nonce,
            "signature": signature,
            "timestamp": timestamp,
            "ticket": card_ticket
        }

    # choose card
    def choose_card_sign(self):
        nonce = nonce_str()
        timestamp = str(int(time.time()))
        card_ticket = self.get_ticket('wx_card')
        items = [WEIXIN_APPID, nonce, timestamp, card_ticket]
        items_str = ''.join(sorted(items))
        sha1obj = hashlib.sha1()
        sha1obj.update(items_str)
        signature = sha1obj.hexdigest()
        return {
            "nonceStr": nonce,
            "cardSign": signature,
            "timestamp": timestamp,
        }

    def decrypt_card_code(self, encry_code):
        url = "/card/code/decrypt"
        params = {"access_token": self.request.get_access_token()}
        json = {"encrypt_code": encry_code}
        response = self.request.request(url, params, json, 'POST')
        if "code" in response:
            return response['code']
        return None

    def active_card(self, init_amount, card_code, card_id, init_bonus=0):
        url = "/card/membercard/activate"
        params = {"access_token": self.request.get_access_token()}
        json = {
            "init_balance": init_amount,
            "init_bonus": init_bonus,
            "membership_number": card_code,
            "code": card_code,
            "card_id": card_id
        }
        response = self.request.request(url, params, json, 'POST')
        if response["errcode"] == 0:
            return True
        return False

    def card_info(self, card_id):
        url = "/card/get"
        params = {"access_token": self.request.get_access_token()}
        json = {"card_id": card_id}
        response = self.request.request(url, params, json, 'POST')
        if response["errcode"] == 0:
            return {'card': response['card']}
        return None

    def card_info_update(self, json_data):
        url = "/card/update"
        params = {"access_token": self.request.get_access_token()}
        response = self.request.request(url, params, json_data, 'POST')
        return response
logger.info("======= Weixin Helper End =======")