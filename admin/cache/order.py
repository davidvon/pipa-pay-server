# -*- coding: utf-8 -*-
import datetime
import time
from app import redis_client
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
