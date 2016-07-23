# -*- coding: utf-8 -*-
import time
from flask import request
from flask.ext.restful import Resource

from api import API_WX_PREFIX
from app import restful_api, logger
from cache.weixin import cache_code_openid, get_cache_code_openid, push_cache_card_id
from config import WEIXIN_APPID
from models import Order, CustomerCard
from wexin.helper import WeixinHelper


__author__ = 'fengguanhua'


class OAuthDecode(Resource):
    def post(self):
        args = request.values
        logger.info('[oauth] in: args[%s]' % args)

        code = args['code']
        openid = get_cache_code_openid(code)
        if openid:
            logger.info('[oauth] caching openid[%s]' % openid)
            return {'result': 0, 'openid': openid}, 200

        helper = WeixinHelper()
        ret = helper.oauth_user(code)
        if ret['errcode'] == 0:
            cache_code_openid(code, ret['openid'])
            logger.info('[oauth] openid[%s]' % ret['openid'])
            return {'result': 0, 'openid': ret['openid']}, 200

        logger.debug('[oauth] out: result[255]')
        return {'result': 255}


class ApiQRcode(Resource):
    def get(self):
        id = request.args['id']
        order = Order.query.get(id)
        if not order:
            return {"result": 254}
        try:
            json = {"expire_seconds": 1800, "action_name": "QR_SCENE", "action_info": {"scene": {"scene_id": id}}}
            helper = WeixinHelper()
            resp = helper.create_qrcode(json)
            url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket=" + resp["ticket"]
            order.qrcode_make(url)
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            return {'result': 0, 'qrcode': url, 'time': now}
        except Exception, e:
            return {'result': 255}


class ApiWxJsSign(Resource):
    def post(self):
        args = request.values
        logger.info('[ApiWxJsSign] in: args[%s]' % args)

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
        logger.info('[ApiWxJsSign] return:[%s]' % data)
        return data


# wx.chooseCard cardSign
class ApiWxCardChooseSign(Resource):
    def post(self):
        helper = WeixinHelper()
        ret = helper.choose_card_sign()
        logger.info("[ApiWxCardChooseSign] wx card sign:%s" % ret)
        return ret


# buy cards
class ApiWxCardsAdd(Resource):
    def post(self):
        args = request.values
        logger.info('[ApiWxCardsAdd] in: args[%s]' % args)

        helper = WeixinHelper()
        order_id = args.get('orderId')
        cards = CustomerCard.query.filter_by(order_id=order_id).all()
        dicts = []
        for card in cards:
            if card.status > 0:
                continue
            ret = helper.card_sign(card.card_id)
            dicts.append({"id": card.card_id, "timestamp": ret['timestamp'], "signature": ret['signature']})
            push_cache_card_id(card.card_id, card.customer_id, card.id)  # TODO
        logger.info('[ApiWxCardsAdd] out: result[0] data[%s]' % dicts)
        return {'result': 0, "data": dicts}


# wx.addCard signature
class ApiWxCardAdd(Resource):
    def post(self):
        args = request.values
        logger.info('[ApiWxCardAdd] in: args[%s]' % args)

        helper = WeixinHelper()
        card_gid = args.get('card_global_id')
        card = CustomerCard.query.get(card_gid)
        push_cache_card_id(card.card_id, card.customer_id, card_gid)
        ret = helper.card_sign(card.card_id)
        dicts = {"id": card.card_id, "timestamp": ret['timestamp'], "signature": ret['signature']}

        logger.info('[ApiWxCardAdd] out: result[0] data[%s]' % dicts)
        return {'result': 0, "data": dicts}


restful_api.add_resource(OAuthDecode, API_WX_PREFIX + 'oauth/decode')
restful_api.add_resource(ApiQRcode, API_WX_PREFIX + 'qrcode')
restful_api.add_resource(ApiWxJsSign, API_WX_PREFIX + 'sign/jsapi')
restful_api.add_resource(ApiWxCardChooseSign, API_WX_PREFIX + 'card/choose/sign')
restful_api.add_resource(ApiWxCardsAdd, API_WX_PREFIX + 'cards/add')
restful_api.add_resource(ApiWxCardAdd, API_WX_PREFIX + 'card/add')
