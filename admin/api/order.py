# -*- coding: utf-8 -*-
import random as Random
import string

from flask.ext.restful import Resource
from api import API_PREFIX
from app import restful_api
from cache.order import cache_order
from models import Order, Customer


class ApiOrders(Resource):
    def get(self):
        orders = Order.query.order_by(Order.create_time.desc()).all()
        ret = {"data": [order.get_order_params() for order in orders]}
        return ret, 200


def create_order(card_id, amount, openid, count):
    def _random_digit(length=10):
        val = ''.join(Random.sample(string.digits * 3, length))
        return _random_digit(length) if val[0] == '0' else val

    customer = Customer.query.filter_by(openid=openid).first()
    if not customer:
        return None
    order = Order(order_id=_random_digit(12), card_id=card_id, customer_id=customer.openid,
                  face_amount=amount/count, card_count=count, pay_amount=amount, order_type=1,
                  paid=False)
    cache_order(order)
    return order


restful_api.add_resource(ApiOrders, API_PREFIX + 'orders')
