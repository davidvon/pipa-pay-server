# -*- coding: utf-8 -*-
import time
from flask import request
from app import restful_api
from flask.ext.restful import Resource
from models import Order
from wexin import WX_API_PREFIX
from wexin.helper import WeixinHelper, Const
from wexin.views import weixin

__author__ = 'fengguanhua'


class ApiQRcode(Resource):
    def get(self):
        id = request.args['id']
        order = Order.query.get(id)
        if not order:
            return '{"error":"1"}'
        try:
            json = {"expire_seconds": 1800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": id}}}
            resp = weixin.weixin_helper.create_qrcode(json)
            url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=" + resp["ticket"]
            order.qrcode_make(url)
            now = time.strftime('%Y-%m-%d %H:%M:%S')
        except Exception, e:
            return {'errcode': 255}, 200
        return {'errcode': 0, 'qrcode': url, 'time': now}, 200


class ApiSign(Resource):
    def get(self):
        url = request.url.split('#')[0]
        helper = WeixinHelper()
        ret = helper.sign(url)
        return {
            "appId": Const.appid,
            "timestamp":ret['timestamp'],
            "nonceStr": ret['nonce_str'],
            "signature": ret['hash']
        }

restful_api.add_resource(ApiQRcode, WX_API_PREFIX +'/qrcode')
restful_api.add_resource(ApiSign, WX_API_PREFIX +'/sign')
