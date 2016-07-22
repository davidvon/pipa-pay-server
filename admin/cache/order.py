# -*- coding: utf-8 -*-
from json import JSONEncoder, JSONDecoder
import time

from app import redis_client
from models import Order
from utils.util import random_digit


__author__ = 'fengguanhua'


def order_id_increment(max_len=5):
    global_order_id = redis_client.get('order_max_id')
    global_order_current_date = redis_client.get('order_current_date')
    if global_order_id:
        global_order_id = int(global_order_id)
    now_date = time.strftime('%Y%m%d')
    if global_order_current_date != now_date:
        global_order_id = 1
        global_order_current_date = now_date
        redis_client.set('order_current_date', global_order_current_date)
    else:
        global_order_id += 1
    redis_client.set('order_max_id', global_order_id)

    format_str = '{:0>%s}' % max_len
    val = format_str.format(str(global_order_id))
    result = '%s%s' % (now_date, val)
    return result


def cache_qrcode_code(card_id, card_code):
    val = '%s-%s' % (card_id, card_code)
    old_code = redis_client.get(val)
    old_code and redis_client.delete(old_code)
    code = random_digit(20)
    redis_client.set(code, val, 70)  # 每分钟刷新
    redis_client.set(val, code, 70)  # 每分钟刷新
    return code


def cache_order(order, expire_seconds=100):
    order_json = {'order_id': order.order_id, 'card_id': order.card_id, 'customer_id': order.customer_id,
                  'face_amount': order.face_amount, 'card_count': order.card_count, 'pay_amount': order.pay_amount,
                  'order_type': order.order_type, 'paid': order.paid}
    order_str = JSONEncoder().encode(order_json)
    redis_client.set('order-%s' % order.order_id, order_str, expire_seconds)


def get_cache_order(order_id):
    val = redis_client.get('order-%s' % order_id)
    if not val:
        return None
    tmp = JSONDecoder().decode(val)
    order = Order(order_id=tmp['order_id'], card_id=tmp['card_id'], customer_id=tmp['customer_id'],
                  face_amount=tmp['face_amount'], card_count=tmp['card_count'], pay_amount=tmp['pay_amount'],
                  order_type=tmp['order_type'], paid=tmp['paid'])
    return order
