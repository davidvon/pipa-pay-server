#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import xml.etree.ElementTree as ET
from config import WEIXIN_APPID, WEIXIN_SECRET, WEIXIN_TOKEN
import hashlib
import time
from app import logger
from cache.weixin import access_token_from_cache, cache_access_token


class WeixinException(Exception):
    def __init__(self, errcode, errmsg):
        self.errcode = errcode
        self.errmsg = errmsg
        self.message = errmsg

    def __str__(self):
        return '%s-%s' % (self.errcode, self.errmsg)


class Const(object):
    api_host = "https://api.weixin.qq.com"
    media_host = "http://file.api.weixin.qq.com"
    qrcode_host = "https://mp.weixin.qq.com"
    appid = WEIXIN_APPID
    secret = WEIXIN_SECRET
    token = WEIXIN_TOKEN


class Request(object):
    def __init__(self, token, host):
        self.host = host
        self.token = token
        self.errcode = 0
        self.errmsg = ''

    def get_host(self):
        return self.host

    def get_token(self):
        return self.token

    def get_tokenid(self):
        return self.token.get()

    def request(self, url, params, data=None, method='GET', headers=None, times=2, sleep_second=1):
        if not headers:
            headers = {'Content-Type': 'application/json'}
        if not data:
            data = {}
        while times:
            try:
                response = self._request(url, params, data, method, headers)
                if "errcode" in response and response["errcode"] != 0:
                    logger.error('[WEIXIN] request error[%d], detail:%s' % (response["errcode"], response["errmsg"]))
                    if response["errcode"] not in [42001, 40001]:
                        times = 1
                    else:
                        params['access_token'] = self.token.refresh()
                    self.errcode = response["errcode"]
                    self.errmsg = response["errmsg"]
                else:
                    return response
            except Exception, e:
                self.errmsg = e.message
            time.sleep(sleep_second)
            times -= 1
        raise WeixinException(self.errcode, self.errmsg)

    def _request(self, url, params, data, method, headers):
        url = '%s%s?%s' % (self.host, url, urllib.urlencode(params))
        response = None
        if method == 'GET':
            response = urllib2.urlopen(url).read()
        elif method == 'POST':
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req).read()
        return response


"""
class MediaRequest(Request):
    def __init__(self,token,host=Const.media_host):
        super(MediaRequest,self).__init__(token,host)

    def _request(self,url,params,data,method,headers):
        url = '%s%s?%s' % (self.host,url,urllib.urlencode(params))
        if method == 'GET':
            f = urllib2.urlopen(url)
            with open(data["filepath"], "wb") as local_file:
                local_file.write(f.read())
            return {"status":"success"}
        elif method == 'POST':
            datagen, headers = multipart_encode({params["type"]: open(data["filepath"], "rb")})
            request = urllib2.Request(url, datagen, headers)
            response = urllib2.urlopen(request).read()
            response = json.loads(response)
            return response

class QrcodeRequest(MediaRequest):
    def __init__(self,token,host=Const.qrcode_host):
        super(QrcodeRequest,self).__init__(token,host)
"""


class APIRequest(Request):
    def __init__(self, token, host=Const.api_host):
        super(APIRequest, self).__init__(token, host)

    def _request(self, url, params, data, method, headers):
        data = json.dumps(data, ensure_ascii=False)
        data = data.encode('UTF-8')
        response = super(APIRequest, self)._request(url, params, data, method, headers)
        response = json.loads(response)
        return response


class TokenRequest(APIRequest):
    def __init__(self, host=Const.api_host):
        super(TokenRequest, self).__init__(None, host)

    def request(self, url, params, data=None, method='GET', headers=None, times=2, sleep_second=1):
        if not headers:
            headers = {'Content-Type': 'application/json'}
        if not data:
            data = {}
        while times:
            try:
                response = self._request(url, params, data, method, headers)
                if "access_token" in response:
                    return response
                self.errcode = response["errcode"]
                self.errmsg = response["errmsg"]
            except Exception, e:
                self.errmsg = e.message
            time.sleep(sleep_second)
            times -= 1
        raise WeixinException(self.errcode, self.errmsg)


class Token(object):
    def __init__(self, request, appid=Const.appid, secret=Const.secret):
        self.request = request
        self.appid = appid
        self.secret = secret
        logger.info('[WEIXIN] appid=%s, secret=%s' % (self.appid, self.secret))

    def get(self):
        tokenid = access_token_from_cache()
        if tokenid is None:
            tokenid = self._create()
        logger.info('[WEIXIN] token=%s' % tokenid)
        return tokenid

    def refresh(self):
        tokenid = self._create()
        logger.info('[WEIXIN] refresh token id:%s' % tokenid)
        return tokenid

    def _create(self):
        """
        https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
        """
        params = {
            "grant_type": "client_credential",
            "appid": self.appid,
            "secret": self.secret
        }
        response = self.request.request("/cgi-bin/token", params)
        cache_access_token(response["access_token"], response["expires_in"])
        logger.info('[WEIXIN] appid=%s, secret=%s, new token=%s, expires=%s' % (
            self.appid, self.secret, response["access_token"], response["expires_in"]))
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


class WeixinMedia(object):
    def __init__(self, request):
        self.request = request

    def upload_media(self, media_type, media):
        """
        http://file.api.weixin.qq.com/cgi-bin/media/upload?access_token=ACCESS_TOKEN&type=TYPE
        """
        url = "/cgi-bin/media/upload"
        params = {
            "access_token": self.request.get_tokenid(),
            "type": media_type
        }
        data = {
            "filepath": media
        }
        r = self.request.request(url, params, data, method='POST')
        return r

    def get_media(self, media_id, file_path):
        """
        http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=ACCESS_TOKEN&media_id=MEDIA_ID
        """
        url = "/cgi-bin/media/get"
        params = {
            "access_token": self.request.get_tokenid(),
            "media_id": media_id
        }
        data = {
            "filepath": file_path
        }
        r = self.request.request(url, params, data, method='GET')
        print(r)


class WeixinHelper(object):
    def __init__(self, request):
        self.request = request

    @staticmethod
    def check_signature(signature, timestamp, nonce):
        tmplist = [Const.token, timestamp, nonce]
        tmplist.sort()
        sha1 = hashlib.sha1()
        map(sha1.update, tmplist)
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return
        raise WeixinException(0, "check_signature failed")

    @staticmethod
    def to_json(message):
        """
        http://docs.python.org/2/library/xml.etree.elementtree.html#xml.etree.ElementTree.XML
        """
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
    def _to_tag(k):
        return ''.join([w.capitalize() for w in k.split('_')])

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
            tag = self._to_tag(k)
            xml += '<%s>%s</%s>' % (tag, self._cdata(v), tag)
        xml += '</xml>'
        return xml

    def send_custom_message(self, message):
        """
        {
            "touser":"OPENID",
            "msgtype":"text",
            "text":
            {
                 "content":"Hello World"
            }
        }
        """
        url = "/cgi-bin/message/custom/send"
        params = {"access_token": self.request.get_tokenid()}
        try:
            response = self.request.request(url, params, message, 'POST')
            logger.info(str(response))
            return response
        except WeixinException as e:
            logger.error(e)
            return {'errcode': e.errcode, 'message': e.errmsg or e.message}

    def push_template_message(self, openid, template_id, push_data, push_url):
        url = '/cgi-bin/message/template/send'
        params = {"access_token": self.request.get_tokenid()}
        post_contents = {
            "touser": openid,
            "template_id": template_id,
            "url": push_url,
            "topcolor": "#7B68EE",
            "data": push_data
        }
        try:
            response = self.request.request(url, params, post_contents, 'POST')
            logger.info(str(response))
        except WeixinException as e:
            logger.error(e)

    def create_group(self, group):
        """
        {"group":{"name":"test"}}
        """
        url = "/cgi-bin/groups/create"
        params = {"access_token": self.request.get_tokenid()}
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
        params = {"access_token": self.request.get_tokenid()}
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
            "access_token": self.request.get_tokenid(),
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
            "access_token": self.request.get_tokenid(),
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
        params = {"access_token": self.request.get_tokenid()}
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
        params = {"access_token": self.request.get_tokenid()}
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
        params = {"access_token": self.request.get_tokenid()}
        response = self.request.request(url, params, member, 'POST')
        if response['errcode'] == 0:
            return response
        errcode = response["errcode"]
        errmsg = response["errmsg"]
        raise WeixinException(errcode, errmsg)

    def create_menu(self, menu):
        """
        # https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN
        {
         "button":[
         {
              "type":"click",
              "name":"今日歌曲",
              "key":"V1001_TODAY_MUSIC"
          },
          {
               "type":"click",
               "name":"歌手简介",
               "key":"V1001_TODAY_SINGER"
          },
          {
               "name":"菜单",
               "sub_button":[
               {
                   "type":"view",
                   "name":"搜索",
                   "url":"http://www.soso.com/"
                },
                {
                   "type":"view",
                   "name":"视频",
                   "url":"http://v.qq.com/"
                },
                {
                   "type":"click",
                   "name":"赞一下我们",
                   "key":"V1001_GOOD"
                }]
           }]
        }
        """
        url = "/cgi-bin/menu/create"
        params = {"access_token": self.request.get_tokenid()}
        response = self.request.request(url, params, menu, 'POST')
        return response

    def get_menu(self):
        """
        https://api.weixin.qq.com/cgi-bin/menu/get?access_token=ACCESS_TOKEN
        """
        url = "/cgi-bin/menu/get"
        params = {"access_token": self.request.get_tokenid()}
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
        params = {"access_token": self.request.get_tokenid()}
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
        params = {"access_token": self.request.get_tokenid()}
        resp = self.request.request(url, params, json, 'POST')
        if "ticket" in resp:
            return resp
        else:
            raise 401

    def oauth(self, code):
        token_url = "/sns/oauth2/access_token"
        token_params = {
            "appid": Const.appid,
            "secret": Const.secret,
            "code": code,
            "grant_type": "authorization_code",
        }
        resp = self.request.request(token_url, token_params)
        # access_token = resp["access_token"]
        # openid = resp["openid"]
        return resp

    def oauth_userinfo(self, code):
        resp = self.oauth(code)
        access_token = resp["access_token"]
        openid = resp["openid"]
        userinfo_url = "/sns/userinfo"
        user_params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN",
        }
        response = self.request.request(userinfo_url, user_params)
        if "errcode" in response:
            errcode = response["errcode"]
            errmsg = response["errmsg"]
            raise WeixinException(errcode, errmsg)
        return response
