# -*- coding: utf-8 -*-
import json
import datetime
import time
import traceback

from flask import request
from flask.ext.restful import Resource

from api import API_PREFIX
from api.order import create_order
from app import restful_api, db, logger
from cache.order import cache_qrcode_code, get_cache_order
from models import Customer, CustomerCard, CustomerTradeRecords, CustomerCardShare, Order
from utils.util import nonce_str
from wexin.helper import WeixinHelper
from wexin_pay.views import payable


__author__ = 'fengguanhua'


class ApiCardMembers(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardMembers] in: args[%s]' % args)

        openid = args.get("openid")
        share = args.get("share")
        customer_cards = CustomerCard.query.filter(CustomerCard.customer_id == openid) \
            .order_by(CustomerCard.status.asc()).all()
        data = [
            {'globalId': item.id,
             'cardId': item.card_id,
             'merchantId': item.card.merchant.id,
             'cardCode': item.card_code,
             'amount': item.amount,
             'title': item.card.title,
             'logo': item.card.merchant.logo,
             'img': item.img or 'http://wx.cdn.pipapay.com/static/images/card_blue.png',
             'status': item.status,
             'expireDate': str(item.expire_date)} for item in customer_cards if
            (not share) or (share and item.status < 3)]
        logger.debug('[ApiCardMembers] out: result[0], data[%s]' % data)
        return {"result": 0, "data": data}


class ApiCardDispatch(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardDispatch] in: args[%s]' % args)

        order_id = args.get('order_id')
        try:
            order = Order.query.filter_by(order_id=order_id).first()
            if not order:
                logger.warn('[ApiCardDispatch] order[%s] not exist' % order_id)
                return {"result": 254}

            expire_date = datetime.date.today() + datetime.timedelta(365 * 3)  # TODO
            count = CustomerCard.query.filter_by(order_id=order_id).count()
            if count < order.card_count:
                for i in range(count, order.card_count):
                    card = CustomerCard(customer_id=order.customer.openid, order_id=order_id, card_id=order.card_id,
                                        amount=order.face_amount, expire_date=expire_date, status=0)
                    db.session.add(card)
                db.session.commit()

            output = {"result": 0, "data": {"count": order.card_count, "amount": order.face_amount}}
            logger.debug('[ApiCardDispatch] out: return [%s]' % output)
            return output
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('[ApiCardDispatch] order[%s] card dispatch exception:[%s]' % (order_id, e.message))
            return {'result': 255, 'data': e.message}


class ApiWxCardStatusUpdate(Resource):
    def post(self):
        openid = args = None
        try:
            args = json.loads(request.data)
            logger.debug('[ApiWxCardStatusUpdate] in: args[%s]' % args)

            openid = args['openid']
            card_global_id = args['cardGlobalId']
            card = CustomerCard.query.get(card_global_id)
            card.status = 1
            db.session.add(card)
            db.session.commit()
            logger.info('[ApiWxCardStatusUpdate] customer[%s] arg[%s] card[code:%s] status update success' %
                        (openid, args, card.card_code))
            return {'result': 0, 'data': card.card_code}
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('[ApiWxCardStatusUpdate] customer[%s] arg[%s] card status update error:[%s]' %
                         (openid, args, e.message))
            return {'result': 255, 'data': e.message}


class ApiCardPayCode(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardPayCode] in: args[%s]' % args)

        card_id = args['cardId']
        card_code = args['cardCode']
        card = CustomerCard.query.filter_by(card_id=card_id, card_code=card_code).first()
        if not card:
            logger.warn('[ApiCardPayCode] card[id:%s,code:%s] not exist' % (card_id, card_code))
            return {'result': 255}
        data = {
            'status': card.status,
            'merchantName': card.card.merchant.name,
            'cardName': card.card.title,
            'amount': card.amount,
            'qrcode': cache_qrcode_code(card_id, card_code)
        }
        logger.debug('[ApiCardPayCode] out: result[0] data[%s]' % data)
        return {'result': 0, 'data': data}


class ApiCardPayRecords(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardPayRecords] in: args[%s]' % args)

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
        logger.debug('[ApiCardPayRecords] out: result[0] data[%s]' % args)
        return {'result': 0, 'data': data}


class ApiCardShareCheck(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardShareCheck] in: args[%s]' % args)

        card_id = args['cardId']
        open_id = args['openId']
        card_code = args['cardCode']
        customer_card = CustomerCard.query.filter_by(customer_id=open_id, card_id=card_id, card_code=card_code).first()
        if not customer_card:
            logger.warn('[ApiCardShareCheck] openid:%s card[id:%s code:%s] not exist' % (open_id, card_id, card_code))
            return {'result': 255}

        if customer_card.status >= 3:
            logger.debug('[ApiCardShareCheck] out: result[0] status[%s]' % customer_card.status)
            return {'result': 0, 'status': customer_card.status}  # 转赠中或已转赠

        data = {'result': 0,
                'status': customer_card.status,
                'card': {
                    'sign': nonce_str(12),
                    'cardId': customer_card.card_id,
                    'cardCode': customer_card.card_code,
                    'cardName': customer_card.card.title,
                    'timestamp': str(int(time.time())),
                    'logo': customer_card.card.merchant.logo}
                }
        logger.debug('[ApiCardShareCheck] out: return[%s]' % data)
        return data


class ApiCardShare(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardShare] in: args[%s]' % args)

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
            logger.info('[ApiCardShare] customer[%s] result[0] card[%s] share ok' % (open_id, card_id))
            return {'result': 0}
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('[ApiCardShare] customer[%s] card[%s] share error:%s' % (open_id, card_id, e.message))
            return {'result': 255, 'data': e.message}


class ApiCardShareInfo(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardShareInfo] in: args[%s]' % args)

        open_id = args['openId']
        card_id = args['cardId']
        card_code = args['cardCode']
        card = CustomerCard.query.filter_by(card_id=card_id, card_code=card_code).first()
        if not card:
            logger.warn('[ApiCardShareInfo] openid:%s card[id:%s code:%s] not exist' % (open_id, card_id, card_code))
            return {'result': 254}

        share = CustomerCardShare.query.filter_by(share_customer_id=open_id, customer_card_id=card.id).first()
        acquire_customer = None
        if share and share.acquire_customer_id:
            acquire_customer = Customer.query.filter_by(openid=share.acquire_customer_id).first()
        data = {'result': 0,
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
        logger.debug('[ApiCardShareInfo] out: return[%s]' % data)
        return data


class ApiCardReceiveCheck(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardReceiveCheck] in: args[%s]' % args)

        sign = args['sign']
        info = CustomerCardShare.query.filter_by(sign=sign).first()
        if not info:
            logger.warn('[ApiCardReceiveCheck] sign[%s] not exist' % sign)
            return {'result': 255}  # sign不存在

        card = info.customer_card
        data = {'result': 0,
                'data': {
                    'giveUserHeadImg': info.share_customer.head_image,
                    'giveUsername': info.share_customer.show_name(),
                    'shareContent': info.content,
                    'cardStatus': card.status,
                    'giveStatus': info.status,
                    'acquireUserOpenId': info.acquire_customer_id}
                }
        logger.debug('[ApiCardReceiveCheck] out: return[%s]' % data)
        return data


class ApiCardReceive(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardReceive] in: args[%s]' % args)

        sign = args['sign']
        openid = args['openId']
        need_commit = False
        try:
            info = CustomerCardShare.query.filter_by(sign=sign).first()
            if not info:
                logger.error('[ApiCardReceive] customer[%s] card[%s] not sharing' %
                             (openid, info.customer_card.card_code))
                return {'result': 255}  # sign不存在

            new_card = CustomerCard.query.filter_by(customer_id=openid, card_code=info.customer_card.card_code,
                                                    card_id=info.customer_card.card_id).first()
            if new_card:
                if info.share_customer.openid == openid:
                    new_card.status = 0
                    db.session.add(new_card)
                    need_commit = True
            else:
                logger.info('[ApiCardReceive] customer[%s] card[%s] not exist' % (openid, info.customer_card_id))
                old_card = CustomerCard.query.filter_by(customer_id=info.share_customer.openid,
                                                        card_id=info.customer_card.card_id,
                                                        card_code=info.customer_card.card_code).first()
                new_card = CustomerCard(customer_id=openid, card_id=info.customer_card.card_id, img=old_card.img,
                                        amount=old_card.amount, card_code=old_card.card_code,
                                        expire_date=old_card.expire_date, status=0)
                old_card.status = 5
                db.session.add(old_card)
                db.session.add(new_card)
                need_commit = True
            if info.status != 1:
                info.acquire_customer_id = openid
                info.status = 1
                db.session.add(info)
                need_commit = True
            if need_commit:
                db.session.commit()
                logger.info('[ApiCardReceive] customer[%s] card[%s] received success' % (openid, new_card.card_code))
            data = {'result': 0,
                    'data': {
                        'status': new_card.status,
                        "cardGlobalId": new_card.id,
                        'wxCardId': new_card.card.wx_card_id,  # 微信卡券ID，可以chooseCard获取
                        'code': info.customer_card.card_code  # 指定的卡券code码，只能被领一次。use_custom_code字段为true的卡券必须填写，
                        # 非自定义code不必填写。
                    }}
            logger.debug('[ApiCardReceive] out: return[%s]' % data)
            return data
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('[ApiCardReceive] customer[%s] receive card[%s] error:%s' % (openid, sign, e.message))
            return {'result': 255, 'data': e.message}


class ApiCardBuy(Resource):
    def post(self):
        try:
            args = json.loads(request.data)
            logger.info('[ApiCardBuy] args:%s' % args)

            card_id = args.get('cardId')
            price = args.get('price')
            count = args.get('count')
            openid = args.get('openId')
            order = create_order(card_id, price, openid, count)
            res, outputs = payable(request, openid, order)
            logger.info('[ApiCardBuy] data:%s' % str(outputs))

            if res == 0:
                outputs['orderId'] = order.order_id
                logger.info('[ApiCardBuy] create temp order success:%s' % order.order_id)
                return {'result': 0, 'content': outputs}

            logger.warn('[ApiCardBuy] order:%s pre-pay failed:%d' % (order.order_id, res))
            return {'result': res}
        except Exception as e:
            logger.error(traceback.print_exc())
            logger.error('[ApiCardBuy] except:%s' % e.message)
            return {'result': 254}


class ApiCardBuyCommit(Resource):
    def post(self):
        args = json.loads(request.data)
        logger.debug('[ApiCardBuyCommit] in: args[%s]' % args)

        order_id = args.get('orderId')
        order = get_cache_order(order_id)
        if not order:
            logger.warn('[ApiCardBuyCommit] order:%s not exist' % order_id)
            return {'result': 254}

        try:
            order.paid = True
            db.session.add(order)
            db.session.commit()
            logger.info('[ApiCardBuyCommit] order:%s create success' % order_id)
            return {'result': 0}
        except Exception as e:
            logger.error('[ApiCardBuyCommit] order:%s create error:%s' % (order_id, e.message))
            return {'result': 255}


class ApiCardActive(Resource):
    def post(self):
        open_id = card_id = code = None
        args = json.loads(request.data)
        logger.debug('[ApiCardActive] in: args[%s]' % args)

        try:
            card_id = args.get('card_id')
            encrypt_code = args.get('encrypt_code')
            open_id = args.get('openid')
            logger.info('[ApiCardActive] data=%s' % str(args))

            helper = WeixinHelper()
            code = helper.decrypt_card_code(encrypt_code)
            if not code:
                logger.error('[ApiCardActive] decrypt card code[%s,%s] error' % (open_id, card_id))
                return {'result': 255}

            card = CustomerCard.query.filter_by(customer_id=open_id, card_id=card_id, card_code=code).first()
            active = helper.active_card(card.amount * 100, code, card_id, 0)
            if not active:
                logger.error('[ApiCardActive] active card[%s,%s,%s] error' % (open_id, card_id, code))
                return {'result': 255}

            card.status = 2
            db.session.add(card)
            db.session.commit()
            logger.debug('[ApiCardActive] out: result[0]')
            return {'result': 0}
        except Exception as e:
            logger.error('[ApiCardActive] active card[%s,%s,%s] exception:%s' % (open_id, card_id, code, e.message))
            return {'result': 255}


restful_api.add_resource(ApiCardBuy, API_PREFIX + 'card/buy')
restful_api.add_resource(ApiCardBuyCommit, API_PREFIX + 'card/buy/commit')
restful_api.add_resource(ApiCardActive, API_PREFIX + 'card/active')

restful_api.add_resource(ApiCardMembers, API_PREFIX + 'cards')
restful_api.add_resource(ApiCardDispatch, API_PREFIX + 'card/dispatch')
restful_api.add_resource(ApiWxCardStatusUpdate, API_PREFIX + 'card/add/status/update')
restful_api.add_resource(ApiCardPayCode, API_PREFIX + 'card/pay/code')
restful_api.add_resource(ApiCardPayRecords, API_PREFIX + 'card/pay/records')

restful_api.add_resource(ApiCardShareCheck, API_PREFIX + 'card/share/check')
restful_api.add_resource(ApiCardShare, API_PREFIX + 'card/share')
restful_api.add_resource(ApiCardShareInfo, API_PREFIX + 'card/share/info')
restful_api.add_resource(ApiCardReceiveCheck, API_PREFIX + 'card/receive/check')
restful_api.add_resource(ApiCardReceive, API_PREFIX + 'card/receive')

