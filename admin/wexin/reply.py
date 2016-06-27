# coding: utf-8
import time
from flask import Response, request, session
from models import WechatSubscribeReply, WechatUselessWordReply, WechatTextReply, WechatNewsReply, \
    WechatSystemReply, LIKE_MATCH, WechatImageNews
from wexin.util import *
from cache.public import cache_url
# from signals import signal_customer_message_cached_notify

CACHE_DB_NEWS = 'DB_TABLE_NEWS'
CACHE_DB_TEXT = 'DB_TABLE_TXT'
CACHE_OPENID_STR = "WEIXIN_OPENID"
CACHE_BACKEND_USER = "BACKEND_USER"

REPLY_NONE = '0'
REPLY_TEXT = '1'
REPLY_NEWS = '2'
REPLY_SYSTEM = '3'


class ReplyKeyWords(object):
    def __init__(self, weixin):
        self._weixin = weixin
        self.msg_type = ''
        self.username = ''
        self.sender = ''
        self.content = ''
        self.event = ''
        self.event = ''
        self.content = ''
        self.location_x = ''
        self.location_y = ''
        self.scale = ''
        self.event_key = ''

    def msg_request(self, args):
        self.msg_type = args.get('msgtype')
        self.username = args.get('tousername')
        self.sender = args.get('fromusername')
        self.content = args.get('content', self.msg_type)
        self.event = None
        if self.msg_type == 'event':
            self.event = args.get('event')
            self.content = args.get('eventkey')
            if self.event == 'LOCATION':
                self.location_x = args.get('latitude')
                self.location_y = args.get('longitude')
                self.scale = args.get('precision')
            elif self.event == 'SCAN':
                self.event_key = self.content
            logger.info('[WEIXIN] event=%s, key=%s' % (self.event, self.content))

        cache_url(request.host_url)
        session[CACHE_OPENID_STR] = self.sender
        logger.info("[WEIXIN] cache openid: %s" % self.sender)

    def msg_reply(self):
        logger.info('[WEIXIN] msg=%s,event=%s' % (self.msg_type, self.event))
        result = None
        if self.msg_type == 'event':
            if self.event == 'subscribe':
                create_customer_try(self.sender)
                update_customer_info(self.sender)
                result = self.event_reply()
            elif self.event == 'unsubscribe':
                async_unsubscribe_customer(self.sender)
                return self.__response('')
            elif self.event == 'CLICK':
                result = self.auto_news_reply()
            elif self.event == 'LOCATION':
                return self.location_report()
            elif self.event == 'SCAN':
                result = self.qrcode()
            else:
                result = ''
        elif self.msg_type == 'text':
            result = self.auto_news_reply()
        # signal_customer_message_cached_notify.send(self, openid=self.sender)
        return result

    def auto_news_reply(self):
        reply = self.get_reply_news()
        if not reply:
            return self.useless_reply()
        return self.all_reply(reply)

    def event_reply(self):
        reply_list = db.session.query(WechatSubscribeReply).all()
        reply = reply_list[0] if reply_list else None
        return self.all_reply(reply)

    def useless_reply(self):
        reply_list = db.session.query(WechatUselessWordReply).all()
        reply = reply_list[0] if reply_list else None
        return self.all_reply(reply)

    def all_reply(self, reply):
        if not reply:
            return self.__custom_text_reply(self.sender, sender=self.username)
        if reply.select_type == REPLY_TEXT:
            text = self.__text_reply(self.sender, type='text', sender=self.username, content=reply.text)
            logger.info('[WEIXIN] reply text:%s' % text)
            return self.__response(text)
        elif reply.select_type == REPLY_NEWS:
            items = self.model_to_dict(reply.image_news_id)
            text = self.__news_reply(self.sender, type='news', sender=self.username, articles=items)
            logger.info('[WEIXIN] reply image text:%s' % text)
            return self.__response(text)
        elif reply.select_type == REPLY_SYSTEM:
            return self.system_reply()
        else:
            return self.useless_reply()

    def system_reply(self):
        pass

    def get_reply_news(self):
        keyword = self.content.lower()
        logger.info('[WEIXIN] get_reply_news: keyword:%s' % keyword)
        model_dict = {REPLY_TEXT: WechatTextReply, REPLY_NEWS: WechatNewsReply, REPLY_SYSTEM: WechatSystemReply}
        for model in model_dict.items():
            reply_list = db.session.query(model[1]).all()
            for reply in reply_list:
                if reply.match_type == LIKE_MATCH:
                    if keyword in reply.keyword.lower():
                        reply.select_type = model[0]
                        logger.info('[WEIXIN] LIKE_MATCH, keyword=%s, select_type=%s' % (keyword, model[0]))
                        return reply
                else:
                    if keyword == reply.keyword.lower():
                        reply.select_type = model[0]
                        logger.info('[WEIXIN] ALL_MATCH, keyword=%s, select_type=%s' % (keyword, model[0]))
                        return reply
        logger.info('[WEIXIN] none, keyword=%s' % keyword)
        return None

    def model_to_dict(self, modelid, sender=None):
        jsons = []
        news = db.session.query(WechatImageNews).get(modelid)
        if news is None:
            return []
        else:
            if sender is None:
                sender = self.sender
            json = news.to_dict(sender)
            jsons.append(json)
            for subitem in news.sub_image_news:
                json = subitem.to_dict(sender)
                jsons.append(json)
        return jsons

    def location_report(self):
        logger.info('[WEIXIN] location: %s-%s-%s' % (self.location_x, self.location_y, self.scale))

    def qrcode(self):
        return ''

    def __custom_text_reply(self, username, sender, **kwargs):
        shared = self.__shared_reply(username, sender, 'transfer_customer_service')
        template = '<xml>%s<Content><![CDATA[%s]]></Content></xml>'
        text = template % (shared, '您好，请问有什么可以帮到您的呢')
        return text

    def __text_reply(self, username, sender, **kwargs):
        content = kwargs.get('content', '')
        shared = self.__shared_reply(username, sender, 'text')
        template = '<xml>%s<Content><![CDATA[%s]]></Content></xml>'
        text = template % (shared, content)
        return text

    def __news_reply(self, username, sender, **kwargs):
        items = kwargs.get('articles', [])
        item_template = (
            '<item>'
            '<Title><![CDATA[%(title)s]]></Title>'
            '<Description><![CDATA[%(description)s]]></Description>'
            '<PicUrl><![CDATA[%(picurl)s]]></PicUrl>'
            '<Url><![CDATA[%(url)s]]></Url>'
            '</item>'
        )
        articles = map(lambda o: item_template % o, items)
        template = (
            '<xml>'
            '%(shared)s'
            '<ArticleCount>%(count)d</ArticleCount>'
            '<Articles>%(articles)s</Articles>'
            '</xml>'
        )
        dct = {
            'shared': self.__shared_reply(username, sender, 'news'),
            'count': len(items),
            'articles': ''.join(articles)
        }
        text = template % dct
        return text

    def __shared_reply(self, username, sender, type):
        dct = {
            'username': username,
            'sender': sender,
            'type': type,
            'timestamp': int(time.time()),
        }
        template = (
            '<ToUserName><![CDATA[%(username)s]]></ToUserName>'
            '<FromUserName><![CDATA[%(sender)s]]></FromUserName>'
            '<CreateTime>%(timestamp)d</CreateTime>'
            '<MsgType><![CDATA[%(type)s]]></MsgType>'
        )
        text = template % dct
        return text

    def __response(self, text):
        # print('send response:%s' % text)
        return Response(text, content_type='text/xml; charset=utf-8')

    def push_news_reply(self, helper, image_news_id, receivers):
        currentid = 0
        total = len(receivers)
        errors = 0
        success = 0
        for userid in receivers:
            customer = Customer.query.get(userid)
            if not customer: continue
            articles = self.model_to_dict(image_news_id, customer.openid)
            message = {
                "touser": customer.openid,
                "msgtype": "news",
                "news": {"articles": articles}
            }
            ret = helper.send_custom_message(message)
            time.sleep(1)
            currentid += 1
            if ret.get('errcode') == 0:
                success += 1
            else:
                errors += 1
            logger.info("[WEIXIN] push message to user[%d/%d]: %s" % (currentid, total, ret.get('message')))
        return {'success': success, 'error': errors, 'total': total}

    def push_text_reply(self, helper, text_id, receivers):
        text_reply = WechatTextReply.query.get(text_id)
        currentid = 0
        errors = 0
        success = 0
        total = len(receivers)
        for userid in receivers:
            customer = Customer.query.get(userid)
            if not customer: continue
            message = {
                "touser": customer.openid,
                "msgtype": "text",
                "text": {
                    "content": text_reply.text
                }
            }
            ret = helper.send_custom_message(message)
            currentid += 1
            if ret.get('errcode') == 0:
                success += 1
            else:
                errors += 1
            logger.info("push message to user[%d/%d]: %s" % (currentid, total, ret.get('message')))
        return {'success': success, 'error': errors, 'total': total}

    def batch_push_text_notify(self, notify_list):
        for notify in notify_list:
            self.push_text_notify(notify['text'], notify['openid'])
            time.sleep(0.1)
        return ''

    def push_text_notify(self, text, openid):
        message = {
            "touser": openid,
            "msgtype": "text",
            "text": {
                "content": text
            }
        }
        ret = self._weixin.weixin_helper.send_custom_message(message)
        content = ret.get('message')
        logger.info("push message to user[%s]: %s" % (openid, content))
        return content

