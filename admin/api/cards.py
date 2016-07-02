# -*- coding: utf-8 -*-
import json
from flask import request
from api import API_PREFIX
from app import restful_api, db
from flask.ext.restful import Resource
from cache.order import cache_qrcode_code
from models import Customer, CustomerCard

__author__ = 'fengguanhua'


class ApiCardMembers(Resource):
    def post(self):
        args = json.loads(request.data)
        openid = args.get("openid")
        customer = Customer.query.filter_by(openid=openid).first()
        customer_cards = CustomerCard.query.filter_by(customer_id=customer.id).all()
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


class ApiCardConsumeCode(Resource):
    def post(self):
        args = json.loads(request.data)
        card_id = args['cardId']
        card = CustomerCard.query.filter_by(card_code=card_id).first()

        data = {
            'status': card.status,
            'merchantName': card.card.merchant.name,
            'cardName': card.card.name,
            'balance': card.balance,
            'qrcode': cache_qrcode_code(card_id)
        }
        return {'result': 0, 'data': data}


restful_api.add_resource(ApiCardMembers, API_PREFIX + 'cards')
restful_api.add_resource(ApiCardBuyQuery, API_PREFIX + 'card/buy/query')
restful_api.add_resource(ApiWxCardStatusUpdate, API_PREFIX + 'card/status/update')
restful_api.add_resource(ApiCardConsumeCode, API_PREFIX + 'card/consume/code')
