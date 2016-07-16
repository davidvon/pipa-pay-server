# -*- coding: utf-8 -*-
import json
import time
from flask import request
from api import API_WX_PREFIX
from app import restful_api, db, logger
from flask.ext.restful import Resource
from cache.weixin import cache_card_adding_tag, cache_code_openid, get_cache_code_openid
from config import WEIXIN_APPID
from models import Order, CustomerCard
from wexin.helper import WeixinHelper

__author__ = 'fengguanhua'


class OAuthDecode(Resource):
    def post(self):
        logger.info('[oauth]: request.data:%s' % request.data)
        args = json.loads(request.data)
        code = args['code']
        openid = get_cache_code_openid(code)
        if openid:
            logger.info('[oauth]: caching openid:%s' % openid)
            return {'errcode': '0-000', 'openid': openid}, 200
        helper = WeixinHelper()
        ret = helper.oauth_user(code)
        if ret['errcode'] == 0:
            cache_code_openid(code, ret['openid'])
            logger.info('[oauth]: openid:%s' % ret['openid'])
            return {'errcode': '0-000', 'openid': ret['openid']}, 200
        return {'errcode': '1-255'}


class ApiQRcode(Resource):
    def get(self):
        id = request.args['id']
        order = Order.query.get(id)
        if not order:
            return '{"error":"1"}'
        try:
            json = {"expire_seconds": 1800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": id}}}
            helper = WeixinHelper()
            resp = helper.create_qrcode(json)
            url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=" + resp["ticket"]
            order.qrcode_make(url)
            now = time.strftime('%Y-%m-%d %H:%M:%S')
        except Exception, e:
            return {'errcode': 255}, 200
        return {'errcode': 0, 'qrcode': url, 'time': now}, 200


class ApiWxJsSign(Resource):
    def post(self):
        args = json.loads(request.data)
        url = args['url']
        logger.info('[ApiWxJsSign] url:%s' % url)
        helper = WeixinHelper()
        ret = helper.jsapi_sign(url)
        data = {
            "appId": WEIXIN_APPID,
            "timestamp": ret['timestamp'],
            "nonceStr": ret['nonce_str'],
            "signature": ret['hash']
        }
        logger.info('[ApiWxJsSign] ack:%s' % data)
        return data


# wx.chooseCard cardSign
class ApiWxCardChooseSign(Resource):
    def post(self):
        helper = WeixinHelper()
        ret = helper.choose_card_sign()
        print("wx card sign:%s" % ret)
        return ret


# buy cards
class ApiWxCardsAdd(Resource):
    def post(self):
        args = json.loads(request.data)
        helper = WeixinHelper()
        order_id = args.get('orderId')
        cards = CustomerCard.query.filter_by(order_id=order_id).all()
        dicts = []
        for card in cards:
            if card.status > 0:
                continue
            # cache_card_adding_tag(card.card_id, card.customer_id, card_global_id)  # TODO
            ret = helper.card_sign(card.card_id)
            dicts.append({"id": card.card_id, "timestamp": ret['timestamp'], "signature": ret['signature']})
        return {'result': 0, "data": dicts}


# wx.addCard signature
class ApiWxCardAdd(Resource):
    def post(self):
        args = json.loads(request.data)
        helper = WeixinHelper()
        card_global_id = args.get('card_global_id')
        card = CustomerCard.query.get(card_global_id)
        cache_card_adding_tag(card.card_id, card.customer_id, card_global_id)
        ret = helper.card_sign(card.card_id)
        dicts = [{"id": card.card_id, "timestamp": ret['timestamp'], "signature": ret['signature']}]
        return {'result': 0, "data": dicts}



restful_api.add_resource(OAuthDecode, API_WX_PREFIX + 'oauth/decode')
restful_api.add_resource(ApiQRcode, API_WX_PREFIX + 'qrcode')
restful_api.add_resource(ApiWxJsSign, API_WX_PREFIX + 'sign/jsapi')
restful_api.add_resource(ApiWxCardChooseSign, API_WX_PREFIX + 'card/choose/sign')
restful_api.add_resource(ApiWxCardsAdd, API_WX_PREFIX + 'cards/add')
restful_api.add_resource(ApiWxCardAdd, API_WX_PREFIX + 'card/add')