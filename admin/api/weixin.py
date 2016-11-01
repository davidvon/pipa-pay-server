# -*- coding: utf-8 -*-
import json
import time
from flask import request
from flask.ext.restful import Resource

from api import API_WX_PREFIX
from app import restful_api, logger, db
from cache.weixin import cache_code_openid, get_cache_code_openid, push_cache_card_id
from config import WEIXIN_APPID
from models import Order, CustomerCard
from wexin.helper import WeixinHelper
from wexin.util import create_customer_try, update_customer_info

__author__ = 'fengguanhua'


class OAuthDecode(Resource):
  def post(self):
    args = request.values
    logger.info('[oauth] in: args[%s]' % args)

    code = args['code']
    helper = WeixinHelper()
    ret = helper.oauth_user(code)
    if ret['errcode'] == 0:
      openid = ret['openid']
      create_customer_try(openid)
      update_customer_info(openid)
      logger.info('[oauth] customer[%s] created' % ret['openid'])
      return {'result': 0, 'openid': ret['openid']}

    logger.debug('[oauth] out: result[254]')
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


class ApiWxCardCreate(Resource):
  def post(self):
    logger.info('[ApiWxCardCreate] in: args[%s]' % request.data)
    data = json.JSONDecoder().decode(request.data)
    helper = WeixinHelper()
    ret = helper.create_card(data)
    logger.info('[ApiWxCardCreate] out: result[%s]' % ret)
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


class ApiWxCardInfo(Resource):
  def get(self, card_id):
    logger.info('[ApiWxCardInfo] in: card_id[%s]' % card_id)
    helper = WeixinHelper()
    ret = helper.card_info(card_id)
    logger.info('[ApiWxCardInfo] out: result[0] data[%s]' % ret)
    if not ret:
      return {'result': 255}
    return {'result': 0, "data": ret}


class ApiWxCardInfoUpdate(Resource):
  def post(self, card_id):
    data = json.JSONDecoder().decode(request.data)
    logger.info('[ApiWxCardInfoUpdate] in: card_id[%s]' % card_id)
    helper = WeixinHelper()
    ret = helper.card_info_update(data)
    return ret


class ApiWxCardRecharge(Resource):
  def post(self, id, code):
    args = request.values
    balance = args['balance']
    logger.info('[ApiWxCardRecharge] in: card.id[%s] card.code[%s], balance[%s]' % (id, code, balance))
    helper = WeixinHelper()
    ret = helper.card_recharge(id, code, balance)
    logger.info('[ApiWxCardRecharge] out: ret[%s]' % ret)
    return ret


class ApiWxCardInfoSync(Resource):
  def post(self, id):
    logger.info('[ApiWxCardBalance] in: card.id[%s]' % id)
    card = CustomerCard.query.filter_by(id=id).first()
    helper = WeixinHelper()
    ret = helper.card_balance(card.card_id, card.card_code)
    if ret['errcode'] == 0:
      try:
        card.wx_balance = ret['balance']
        card.credit = ret['bonus']
        db.session.add(card)
        db.session.commit()
        logger.info('[ApiWxCardBalance] sync success')
      except Exception as e:
        logger.error('[ApiWxCardBalance] sync failed:%s' % e.message)
    logger.info('[ApiWxCardBalance] out: ret[%s]' % ret)
    return ret


class ApiWxCardCode(Resource):
  def post(self, card_id, openid):
    logger.info('[ApiWxCardCode] in: card_id[%s]' % card_id)
    cards = CustomerCard.query.filter_by(card_id=card_id, customer_id=openid).all()
    helper = WeixinHelper()
    ret = helper.card_code_list(openid, card_id)
    if ret['errcode'] == 0:
      try:
        for item in ret['card_list']:
          is_exist = False
          for card in cards:
            if item['card_id'] == card.card_id and item['code'] == card.card_code and card.status > 0:
              is_exist = True
              break
            if card.status == 0:
              card.card_code = item['code']
              db.session.add(card)
              db.session.commit()
              logger.info('[ApiWxCardCode] sync success')
              is_exist = True
          if is_exist:
            continue
      except Exception as e:
        logger.error('[ApiWxCardCode] sync failed:%s' % e.message)
    logger.info('[ApiWxCardCode] out: ret[%s]' % ret)
    return ret


class ApiWxCardConsumeCheck(Resource):
  def post(self, uuid):
    logger.info('[ApiWxCardConsumeCheck] in: card.id[%s]' % uuid)
    card = CustomerCard.query.filter_by(id=uuid).first()
    helper = WeixinHelper()
    ret = helper.card_status(card.card_id, card.card_code)
    if ret['errcode'] == 0:
      logger.error('[ApiWxCardConsumeCheck] out: not pass:[%s]' % ret)
    else:
      logger.info('[ApiWxCardConsumeCheck] out: pass')
    return True if ret['errcode'] == 0 else False


restful_api.add_resource(ApiWxCardCreate, API_WX_PREFIX + 'card/create')
restful_api.add_resource(OAuthDecode, API_WX_PREFIX + 'oauth/decode')
restful_api.add_resource(ApiQRcode, API_WX_PREFIX + 'qrcode')
restful_api.add_resource(ApiWxJsSign, API_WX_PREFIX + 'sign/jsapi')
restful_api.add_resource(ApiWxCardChooseSign, API_WX_PREFIX + 'card/choose/sign')
restful_api.add_resource(ApiWxCardsAdd, API_WX_PREFIX + 'cards/add')
restful_api.add_resource(ApiWxCardAdd, API_WX_PREFIX + 'card/add')
restful_api.add_resource(ApiWxCardInfo, API_WX_PREFIX + 'card/<string:card_id>')
restful_api.add_resource(ApiWxCardInfoUpdate, API_WX_PREFIX + 'card/<string:card_id>/update')
restful_api.add_resource(ApiWxCardRecharge, API_WX_PREFIX + 'card/<string:card_id>/<string:code>/recharge')
restful_api.add_resource(ApiWxCardInfoSync, API_WX_PREFIX + 'card/<string:id>/sync')
restful_api.add_resource(ApiWxCardCode, API_WX_PREFIX + 'card/<string:card_id>/<string:openid>/code')
restful_api.add_resource(ApiWxCardConsumeCheck, API_WX_PREFIX + 'card/<string:uuid>/consume/check')
