# -*- coding: utf-8 -*-
import hashlib
import json
import datetime
import time
import traceback
from flask import request
from api import API_PREFIX
from api.order import create_order
from app import restful_api, db, logger
from flask.ext.restful import Resource
from cache.order import cache_qrcode_code
from models import Customer, CustomerCard, CustomerTradeRecords, CustomerCardShare
from utils.util import nonce_str
from wexin.helper import WeixinHelper
from wexin_pay.views import payable

__author__ = 'fengguanhua'


class ApiCardMembers(Resource):
    def post(self):
        args = json.loads(request.data)
        openid = args.get("openid")
        share = args.get("share")
        customer_cards = CustomerCard.query.filter(CustomerCard.customer_id == openid)\
            .order_by(CustomerCard.status.asc()).all()
        data = [
            {'globalId': item.id,
             'cardId': item.card_id,
             'merchantId': item.card.merchant.id,
             'cardCode': item.card_code,
             'amount': item.amount,
             'title': item.card.title,
             'logo': item.card.merchant.logo,
             'img': item.img or '/static/card_blue.png',
             'status': item.status,
             'expireDate': str(item.expire_date)} for item in customer_cards if
            (not share) or (share and item.status < 3)]
        return {"result": 0, "data": data}, 200


class ApiCardBuyQuery(Resource):
    def post(self):
        args = json.loads(request.data)
        order_no = args.get('order_no')
        data = {
            "buy_status": 0,  # 1:等待;0:成功;255:失败
            "cards": {
                "number": 0,
                "money": 0,
                "list": [
                    {
                        "receive_status": 0,
                        "id": '',
                        "code": ''
                    }
                ]
            }
        }
        return {"result": 0, "data": data}, 200


class ApiWxCardStatusUpdate(Resource):
    def post(self):
        openid = args = None
        try:
            args = json.loads(request.data)
            openid = args['openid']
            card_global_id = args['cardGlobalId']
            card = CustomerCard.query.get(card_global_id)
            card.status = 1
            db.session.add(card)
            db.session.commit()
            logger.info('[ApiWxCardStatusUpdate] customer[%s] arg[%s] card status update success' % (openid, args))
            return {'result': 0, 'data': card.card_code}
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('[ApiWxCardStatusUpdate] customer[%s] arg[%s] card status update error:[%s]' %
                         (openid, args, e.message))
            return {'result': 255, 'data': e.message}


class ApiCardPayCode(Resource):
    def post(self):
        args = json.loads(request.data)
        card_id = args['cardId']
        card_code = args['cardCode']
        card = CustomerCard.query.filter_by(card_id=card_id, card_code=card_code).first()
        if not card:
            return {'result': 255}
        data = {
            'status': card.status,
            'merchantName': card.card.merchant.name,
            'cardName': card.card.title,
            'amount': card.amount,
            'qrcode': cache_qrcode_code(card_id)
        }
        return {'result': 0, 'data': data}


class ApiCardPayRecords(Resource):
    def post(self):
        args = json.loads(request.data)
        card_id = args['cardId']
        left = datetime.date.today()
        right = datetime.date.today() - datetime.timedelta(30)
        records = CustomerTradeRecords.query.filter(CustomerTradeRecords.card_id == card_id,
                                                    CustomerTradeRecords.time.between(left, right)).all()
        recharge_total = 0
        expend_total = 0
        for item in records:
            if item.type == 0:
                recharge_total += item.amount
            else:
                expend_total += item.amount
        data = {
            'rechargeTotal': recharge_total,
            'expendTotal': expend_total,
            'records': [{'merchantName': item.card.merchant.name,
                         'date': str(item.time),
                         'amount': item.amount} for item in records]
        }
        return {'result': 0, 'data': data}


class ApiCardShareCheck(Resource):
    def post(self):
        args = json.loads(request.data)
        card_id = args['cardId']
        open_id = args['openId']
        card_code = args['cardCode']
        customer_card = CustomerCard.query.filter_by(customer_id=open_id, card_id=card_id, card_code=card_code).first()
        if customer_card:
            if customer_card.status >= 3:
                return {'result': 0, 'data': {'status': customer_card.status, 'card': {}}}  # 转赠中或已转赠
            timestamp = str(int(time.time()))
            hash = nonce_str(12)
            return {'result': 0,
                    'data': {'status': customer_card.status,
                             'card': {
                                 'sign': hash,
                                 'cardId': customer_card.card_id,
                                 'cardCode': customer_card.card_code,
                                 'cardName': customer_card.card.title,
                                 'timestamp': timestamp,
                                 'logo': customer_card.card.merchant.logo
                             }}}
        return {'result': 255}


class ApiCardShare(Resource):
    def post(self):
        args = json.loads(request.data)
        open_id = args['openId']
        card_id = args['cardId']
        card_code = args['cardCode']
        sign = args['sign']
        timestamp = args['timestamp']
        content = args['content']
        try:
            card = CustomerCard.query.filter_by(customer_id=open_id, card_id=card_id, card_code=card_code).first()
            card.status = 4  # 卡表状态更新为 4:转赠中
            record = CustomerCardShare(share_customer_id=open_id, customer_card_id=card.id,
                                       timestamp=timestamp, content=content, sign=sign, status=0)
            db.session.add(card)
            db.session.add(record)
            db.session.commit()
            logger.info('customer[%s] card[%s] share ok' % (open_id, card_id))
            return {'result': 0}
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('customer[%s] card[%s] share error:%s' % (open_id, card_id, e.message))
            return {'result': 255, 'data': e.message}


class ApiCardShareInfo(Resource):
    def post(self):
        args = json.loads(request.data)
        open_id = args['openId']
        card_id = args['cardId']
        card_code = args['cardCode']
        card = CustomerCard.query.filter_by(card_id=card_id, card_code=card_code).first()
        if not card:
            return {'result': 254}
        share = CustomerCardShare.query.filter_by(share_customer_id=open_id, customer_card_id=card.id).first()
        acquire_customer = None
        if share:
            if share.acquire_customer_id:
                acquire_customer = Customer.query.filter_by(openid=share.acquire_customer_id).first()
            return {'result': 0,
                    'data': {'status': '已领取' if share.status == 2 else '未领取',
                             'cardLogo': share.customer_card.card.merchant.logo,
                             'cardCode': card_code,
                             'cardName': share.customer_card.card.title,
                             'datetime': str(share.datetime),
                             'content': share.content,
                             'acquireUserImg': acquire_customer.head_image if acquire_customer else '',
                             'acquireUserName': acquire_customer.show_name() if acquire_customer else '',
                             }
                    }
        return {'result': 255}


class ApiCardReceiveCheck(Resource):
    def post(self):
        args = json.loads(request.data)
        sign = args['sign']
        info = CustomerCardShare.query.filter_by(sign=sign).first()
        if not info:
            return {'result': 255}  # sign不存在
        card = info.customer_card
        return {'result': 0,
                'data': {
                    'giveUserHeadImg': info.share_customer.head_image,
                    'giveUsername': info.share_customer.show_name(),
                    'shareContent': info.content,
                    'cardStatus': card.status,
                    'giveStatus': info.status,
                    'acquireUserOpenId': info.acquire_customer_id
                }
                }


class ApiCardReceive(Resource):
    def post(self):
        args = json.loads(request.data)
        sign = args['sign']
        openid = args['openId']
        need_commit = False
        try:
            info = CustomerCardShare.query.filter_by(sign=sign).first()
            if not info:
                logger.error('customer[%s] card[%s] not sharing' % (openid, info.customer_card.card_code))
                return {'result': 255}  # sign不存在
            new_card = CustomerCard.query.filter_by(customer_id=openid, card_id=info.customer_card_id).first()
            if not new_card:
                old_card = CustomerCard.query.filter_by(customer_id=info.share_customer.openid).first()
                new_card = CustomerCard(customer_id=openid, card_id=info.customer_card.card_id, img=old_card.img,
                                        amount=old_card.amount, card_code=old_card.card_code,
                                        expire_date=old_card.expire_date,
                                        status=0)
                old_card.status = 5
                db.session.add(new_card)
                need_commit = True
            if info.status != 1:
                info.acquire_customer_id = openid
                info.status = 1
                db.session.add(info)
                need_commit = True
            if need_commit:
                db.session.commit()
                logger.info('customer[%s] card[%s] receive ok' % (openid, new_card.card_code))
            return {'result': 0,
                    'data': {
                        'status': new_card.status,
                        "cardGlobalId": new_card.id,
                        'wxCardId': new_card.card.wx_card_id,  # 微信卡券ID，可以chooseCard获取
                        'code': info.customer_card.card_code  # 指定的卡券code码，只能被领一次。use_custom_code字段为true的卡券必须填写，
                        # 非自定义code不必填写。
                    }
                    }
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('customer[%s] receive card[%s] error:%s' % (openid, sign, e.message))
            return {'result': 255, 'data': e.message}


class ApiCardBuy(Resource):
    def post(self):
        try:
            args = json.loads(request.data)
            cardid = args.get('cardId')
            price = args.get('price')
            count = args.get('count')
            openid = args.get('openId')
            order = create_order(cardid, price, openid, count)
            res, outputs = payable(request, openid, order)
            logger.info('[ApiOrderPayable] data=%s' % str(outputs))
            if res == 0:
                outputs['orderId'] = order.order_id
                db.session.add(order)
                db.session.commit()
                return {'result': 0, 'content': outputs}, 200
            return {'result': res}, 200
        except Exception as e:
            print e.message
            return {'result': 254}, 200


class ApiCardActive(Resource):
    def post(self):
        openid = cardid = code = None
        try:
            args = json.loads(request.data)
            logger.info('[ApiCardActive] data=%s' % str(args))
            cardid = args.get('card_id')
            encrypt_code = args.get('encrypt_code')
            openid = args.get('openid')
            helper = WeixinHelper()
            code = helper.decrypt_card_code(encrypt_code)
            if not code:
                logger.error('[ApiCardActive] decrypt card code[%s,%s] error' % (openid, cardid))
                return {'result': 255}, 200
            card = CustomerCard.query.filter_by(customer_id=openid, card_id=cardid, card_code=code).first()
            active = helper.active_card(card.amount * 100, code, cardid, 0)
            if not active:
                logger.error('[ApiCardActive] active card[%s,%s,%s] error' % (openid, cardid, code))
                return {'result': 255}, 200
            card.status = 2
            db.session.add(card)
            db.session.commit()
            return {'result': 0}, 200
        except Exception as e:
            logger.error('[ApiCardActive] active card[%s,%s,%s] exception' % (openid, cardid, code))
            return {'result': 255}, 200


restful_api.add_resource(ApiCardMembers, API_PREFIX + 'cards')
restful_api.add_resource(ApiCardBuyQuery, API_PREFIX + 'card/buy/query')
restful_api.add_resource(ApiWxCardStatusUpdate, API_PREFIX + 'card/add/status/update')
restful_api.add_resource(ApiCardPayCode, API_PREFIX + 'card/pay/code')
restful_api.add_resource(ApiCardPayRecords, API_PREFIX + 'card/pay/records')

restful_api.add_resource(ApiCardShareCheck, API_PREFIX + 'card/share/check')
restful_api.add_resource(ApiCardShare, API_PREFIX + 'card/share')
restful_api.add_resource(ApiCardShareInfo, API_PREFIX + 'card/share/info')
restful_api.add_resource(ApiCardReceiveCheck, API_PREFIX + 'card/receive/check')
restful_api.add_resource(ApiCardReceive, API_PREFIX + 'card/receive')

restful_api.add_resource(ApiCardBuy, API_PREFIX + 'card/buy')
restful_api.add_resource(ApiCardActive, API_PREFIX + 'card/active')