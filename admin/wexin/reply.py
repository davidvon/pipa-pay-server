# coding: utf-8
import time
import traceback
from datetime import datetime
from flask import Response
from cache.weixin import pop_cache_card_id
from models import WechatSubscribeReply, WechatUselessWordReply, WechatTextReply, WechatNewsReply, \
    WechatSystemReply,  WechatImageNews, CustomerCardShare, CustomerCard, Customer
from config import LIKE_MATCH
from wexin import util
from app import logger, db

# from cache.public import cache_url
# from signals import signal_customer_message_cached_notify
CACHE_OPENID_STR = "WEIXIN_OPENID"
REPLY_NONE = '0'
REPLY_TEXT = '1'
REPLY_NEWS = '2'
REPLY_SYSTEM = '3'


class ReplyKeyWords(object):
    def __init__(self, weixin):
        self._weixin = weixin
        self.username = ''
        self.sender = ''
        self.event = ''
        self.content = ''

    def msg_reply(self, args):
        msg_type = args.get('msgtype')
        logger.info('[WEIXIN] msg=%s,event=%s' % (msg_type, self.event))
        self.username = args.get('tousername')
        self.sender = args.get('fromusername')
        self.content = args.get('content', msg_type)
        if msg_type == 'event':
            self.event = args.get('event')
            if self.event == 'subscribe':
                util.create_customer_try(self.sender)
                util.update_customer_info(self.sender)
                return self.event_reply()
            elif self.event == 'unsubscribe':
                util.unsubscribe_customer(self.sender)
                return self.__response('')
            elif self.event == 'CLICK':
                return self.auto_news_reply()
            elif self.event == 'LOCATION':
                location_x = args.get('latitude')
                location_y = args.get('longitude')
                scale = args.get('precision')
                return self.location_report(location_x, location_y, scale)
            elif self.event == 'SCAN':
                self.content = args.get('eventkey')
                return self.qrcode(self.content)
            elif self.event == 'user_get_card':  # 领取卡券
                return self.card_give(args)
            elif self.event == 'user_pay_from_pay_cell':  # 买单卡券
                return self.card_pay_event_notify(args)
            elif self.event == 'user_del_card':  # 删除卡券
                return ''
            elif self.event == 'user_consume_card':  # 核销卡券
                return ''
            else:
                return ''
        elif msg_type == 'text':
            return self.auto_news_reply()
        # signal_customer_message_cached_notify.send(self, openid=self.sender)
        return ''

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

    @staticmethod
    def system_reply():
        return ''

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
        return ''

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

    @staticmethod
    def location_report(location_x, location_y, scale):
        logger.info('[WEIXIN] location: %s-%s-%s' % (location_x, location_y, scale))
        return ''

    @staticmethod
    def qrcode(content):
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

    @staticmethod
    def __shared_reply(username, sender, type):
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
        return self.__response(str({'success': success, 'error': errors, 'total': total}))

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
        return self.__response(str({'success': success, 'error': errors, 'total': total}))

    def batch_push_text_notify(self, notify_list):
        for notify in notify_list:
            self.push_text_notify(notify['text'], notify['openid'])
            time.sleep(0.1)
        return self.__response('')

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
        return self.__response(content)

    def card_give(self, args):
        logger.info('[card_give] customer[%s] card give event[%s] received' % (self.sender, args))
        is_gived = args.get('isgivebyfriend')
        share_openid = args.get('friendusername')
        cardid = args.get('cardid')
        card_code = args.get('usercardcode')
        old_card_code = args.get('oldusercardcode')
        try:
            if is_gived == 1:
                card_share = CustomerCardShare.query.filter_by(share_customer_id=share_openid,
                                                               customer_card_id=cardid).first()
                old_card = CustomerCard.query.filter_by(customer_id=share_openid, card_id=cardid,
                                                        card_code=old_card_code).first()
                new_card = CustomerCard.query.filter_by(customer_id=self.sender, card_id=cardid,
                                                        card_code=card_code).first()
                if not new_card:
                    new_card = CustomerCard(customer_id=self.sender, card_id=cardid, card_code=card_code, status=0,
                                            img=old_card.img, balance=old_card.balance, expire_date=old_card.expire_date)
                old_card.status = 4
                card_share.acquire_customer_id = self.sender
                db.session.add(card_share)
                db.session.add(old_card)
                db.session.add(new_card)
            else:
                card_gid = pop_cache_card_id(cardid, self.sender)
                if not card_gid:
                    logger.error('[card_give] customer[%s] card[%s] pop is empty' % (self.sender, cardid))
                    return self.__response(str({'result': 'error'}))
                logger.debug('[card_give] customer[%s] card[%s] popped' % (self.sender, card_gid))
                card = CustomerCard.query.get(card_gid)
                card.wx_binding_time = datetime.now()
                card.card_code = card_code
                db.session.add(card)
            db.session.commit()
            logger.info('[card_give] customer[%s] card banding success' % self.sender)
            return self.__response(str({'result': 'ok'}))
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('[card_give] customer[%s] card banding event[%s] error:%s' % (self.sender, args, e.message))
            return self.__response(str({'result': 'error'}))


    def card_pay_event_notify(self, args):
        logger.info('customer[%s] card pay event[%s] received' % (self.sender, args))
        share_openid = args.get('friendusername')
        cardid = args.get('cardid')
        card_code = args.get('usercardcode')
        trans_id = args.get('transid')
        trans_id = args.get('fee')
        # TODO
        return self.__response(str({'result': 'ok'}))
