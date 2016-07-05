# -*- coding: utf-8 -*-
import json
import time
from flask import request
from api import API_WX_PREFIX
from app import restful_api, db
from flask.ext.restful import Resource
from config import WEIXIN_APPID
from models import Order, CustomerCard, Customer, Card
from wexin.helper import WeixinHelper

__author__ = 'fengguanhua'


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
        print("url:%s, ret:%s" % (url, data))
        return data, 200


class ApiWxCardSign(Resource):
    def get(self):
        helper = WeixinHelper()
        ret = helper.card_sign()
        return {
            "timestamp": ret['timestamp'],
            "nonceStr": ret['nonce_str'],
            "cardSign": ret['hash'],
            "signType": 'SHA1',
            'shopId': '',
            'carType': '',
            'carId': ''
        }


class ApiWxCards(Resource):
    def post(self):
        args = json.loads(request.data)
        helper = WeixinHelper()
        openid = args.get('openid')
        cards = CustomerCard.query.filter_by(customer_id=openid).all()
        dicts = []
        for card in cards:
            ret = helper.card_sign()
            dicts.append({
                "id": card.card_id,
                "code": card.card_code,
                "timestamp": ret['timestamp'],
                "nonce_str": ret['nonce_str'],
                "signature": ret['hash']
            })
        return {'result': 0, "data": dicts}




restful_api.add_resource(ApiQRcode, API_WX_PREFIX + 'qrcode')
restful_api.add_resource(ApiWxJsSign, API_WX_PREFIX + 'jsapi_sign')
restful_api.add_resource(ApiWxCardSign, API_WX_PREFIX + 'card_sign')
restful_api.add_resource(ApiWxCards, API_WX_PREFIX + 'cards')
