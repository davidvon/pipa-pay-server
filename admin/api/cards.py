# -*- coding: utf-8 -*-
import hashlib
import json
import datetime
import time
import traceback
from flask import request
from api import API_PREFIX
from app import restful_api, db, logger
from flask.ext.restful import Resource
from cache.order import cache_qrcode_code
from models import Customer, CustomerCard, CustomerTradeRecords, CustomerCardShare

__author__ = 'fengguanhua'


class ApiCardMembers(Resource):
    def post(self):
        args = json.loads(request.data)
        openid = args.get("openid")
        customer_cards = CustomerCard.query.filter(CustomerCard.customer_id == openid, CustomerCard.status < 2).all()
        data = [
            {'cardId': item.card_id,
             'merchantId': item.card.merchant.id,
             'cardCode': item.card_code,
             'amount': item.amount,
             'balance': item.balance,
             'title': item.card.title,
             'logo': item.card.merchant.logo,
             'img': item.img or '/static/demo/card_blue.png',
             'status': item.status,
             'expireDate': str(item.expire_date)} for item in customer_cards]
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
        args = json.loads(request.data)
        openid = args['openid']
        for item in args['cards']:
            CustomerCard.query.filter_by(openid=openid, card_id=item.card_id).update({CustomerCard.status: 1})
        db.session.commit()
        return {'result': 0}


class ApiCardPayCode(Resource):
    def post(self):
        args = json.loads(request.data)
        card_id = args['cardId']
        card = CustomerCard.query.filter_by(card_id=card_id).first()
        if not card:
            return {'result': 255}
        data = {
            'status': card.status,
            'merchantName': card.card.merchant.name,
            'cardName': card.card.title,
            'balance': card.balance,
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
        customer_card = CustomerCard.query.filter_by(customer_id=open_id, card_id=card_id).first()  # TODO
        if customer_card:
            if customer_card.status == 2:
                return {'result': 0, 'data': {'status': 2, 'card': {}}}  # 已转赠
            timestamp = str(int(time.time()))
            sign = 'cardid=%s,openid=%s,timestamp=%s' % (card_id, open_id, timestamp)
            sha1obj = hashlib.sha1()
            sha1obj.update(sign)
            hash = sha1obj.hexdigest()
            return {'result': 0, 'data': {'status': customer_card.status,
                                          'card': {
                                              'sign': hash,
                                              'cardId': customer_card.card_id,
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
        sign = args['sign']
        timestamp = args['timestamp']
        content = args['content']
        try:
            card = CustomerCard.query.filter_by(customer_id=open_id, card_id=card_id).first()
            card.status = 2  # 卡表状态更新为 2:已转赠
            record = CustomerCardShare(share_customer_id=open_id, card_id=card_id,
                                       timestamp=timestamp, shareContent=content, sign=sign, status=0)
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
        share = CustomerCardShare.query.filter_by(share_customer_id=open_id, customer_card_id=card_id).first()
        acquire_customer = None
        if share:
            if share.acquire_customer_id:
                acquire_customer = Customer.query.filter_by(openid=share.acquire_customer_id).first()
            return {'result': 0,
                    'data': {'status': '已领取' if share.status == 1 else '未领取',
                             'cardLogo': share.customer_card.card.merchant.logo,
                             'cardId': share.customer_card_id,
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
        card = CustomerCard.query.filter_by(customer_id=info.share_customer.openid).first()
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
                return {'result': 255}  # sign不存在
            new_card = CustomerCard.query.filter_by(customer_id=openid, card_id=info.card_id).first()
            if not new_card:
                old_card = CustomerCard.query.filter_by(customer_id=info.share_customer.openid).first()
                new_card = CustomerCard(customer_id=openid, card_id=info.card_id, img=old_card.img,
                                        amount=old_card.amount,
                                        balance=old_card.balance, card_code=old_card.card_code,
                                        expire_date=old_card.expire_date,
                                        status=0)
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
                        'wxCardId': new_card.card.wx_card_id,  # 微信卡券ID，可以chooseCard获取
                        'code': info.card.card_code  # 指定的卡券code码，只能被领一次。use_custom_code字段为true的卡券必须填写，
                        # 非自定义code不必填写。
                    }
                    }
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('customer[%s] receive card[%s] error:%s' % (openid, sign, e.message))
            return {'result': 255, 'data': e.message}


restful_api.add_resource(ApiCardMembers, API_PREFIX + 'cards')
restful_api.add_resource(ApiCardBuyQuery, API_PREFIX + 'card/buy/query')
restful_api.add_resource(ApiWxCardStatusUpdate, API_PREFIX + 'card/status/update')
restful_api.add_resource(ApiCardPayCode, API_PREFIX + 'card/pay/code')
restful_api.add_resource(ApiCardPayRecords, API_PREFIX + 'card/pay/records')

restful_api.add_resource(ApiCardShareCheck, API_PREFIX + 'card/share/check')
restful_api.add_resource(ApiCardShare, API_PREFIX + 'card/share')
restful_api.add_resource(ApiCardShareInfo, API_PREFIX + 'card/share/info')
restful_api.add_resource(ApiCardReceiveCheck, API_PREFIX + 'card/receive/check')
restful_api.add_resource(ApiCardReceive, API_PREFIX + 'card/receive')

