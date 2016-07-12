# -*- coding: utf-8 -*-
import json
import time
from flask import request
from api import API_WX_PREFIX
from app import restful_api, db, logger
from flask.ext.restful import Resource
from cache.weixin import cache_card_adding_tag
from config import WEIXIN_APPID
from models import Order, CustomerCard
from wexin.helper import WeixinHelper

__author__ = 'fengguanhua'


class OAuthDecode(Resource):
    def post(self):
        args = json.loads(request.data)
        code = args['code']
        helper = WeixinHelper()
        ret = helper.oauth_user(code)
        if ret['errcode'] == 0:
            return {'errcode': 0, 'openid': ret['data']['openid']}, 200
        return {'errcode': 255}

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
        helper = WeixinHelper()
        ret = helper.jsapi_sign(url)
        data = {
            "appId": WEIXIN_APPID,
            "timestamp": ret['timestamp'],
            "nonceStr": ret['nonce_str'],
            "signature": ret['hash']
        }
        return data, 200


# wx.chooseCard cardSign
class ApiWxCardChooseSign(Resource):
    def post(self):
        helper = WeixinHelper()
        ret = helper.choose_card_sign()
        print("wx card sign:%s" % ret)
        return ret, 200


# wx.addCard signature
class ApiWxCardsAdd(Resource):
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
