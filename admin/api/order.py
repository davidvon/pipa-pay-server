# -*- coding: utf-8 -*-
import json
from random import Random
import datetime
from api import API_PREFIX
from app import db, logger, restful_api
from flask import request
from flask.ext.restful import Resource
from models import Order, Customer, Shop
from wexin_pay.views import payable

__author__ = 'fengguanhua'


# def grant_customer_scores(order, customer):
# scores = 0
#     for item in order.order_items.all():
#         scores += item.service.award_score
#     customer_scores = CustomerScores.query.filter_by(customer_id=customer.id).first()
#     if not customer_scores:
#         customer_scores = CustomerScores(customer_id=customer.id, total_scores=scores)
#     else:
#         customer_scores.total_scores += scores
#     db.session.add(customer_scores)
#     logger.info('[grant_customer_scores] grant customer:%s scores:%s' % (customer.id, scores))
#
# def order_closed_process(order):
#     try:
#         customer = order.customer
#         res = customer.frequent_status_check()
#         if res:
#             db.session.add(customer)
#         grant_customer_scores(order, customer)
#         db.session.commit()
#     except Exception, e:
#         logger.error('[order_closed_process] exception:%s' % e.message)
#
#
# class ApiOrderCancel(Resource):
#     def post(self):
#         try:
#             args = request.args
#             orderid = args.get('orderid')
#             order = Order.query.filter_by(order_serial=orderid).first()
#             args = get_order_params(order)
#             db.session.delete(order)
#             signal_order_notify.send(self, args=args, status='cancel')  # notify
#             db.session.commit()
#             return {'result': '0'}, 200
#         except Exception as e:
#             return {'result': '255', 'error': e.message}, 200
#
#
# class ApiOrderBooking(Resource):
#     def post(self):
#         try:
#             uid = request.form.get('uid')
#             tel = request.form.get('tel')
#             address_id = request.form.get('address')
#             sum = request.form.get('sum')
#             delivery_date_num = int(request.form.get('delivery_date'))
#             received_date_num = int(request.form.get('received_date'))
#             booking_delivery_time = int(request.form.get('delivery_time'))
#             booking_delivery_date = dt.datetime.now() + dt.timedelta(days=delivery_date_num)
#             booking_received_time = int(request.form.get('received_time'))
#             booking_received_date = dt.datetime.now() + dt.timedelta(days=received_date_num)
#             customer = Customer.query.filter_by(openid=uid).first()
#             if not customer:
#                 return {'result': 'error', 'msg': 'customer not exist'}, 500
#             order_serial = order_id_increment()
#             address = CustomerAddress.query.filter_by(id=address_id, customer_id=customer.id).first()
#             if not address:
#                 return {'result': 'error', 'msg': 'address not exist'}, 500
#             order = Order(order_serial=order_serial, customer_id=customer.id, address_id=address_id,
#                           booking_clothes=sum, phone=tel, create_date=dt.date.today(), create_time=dt.datetime.now(),
#                           booking_delivery_date=booking_delivery_date, booking_delivery_time=booking_delivery_time,
#                           booking_received_date=booking_received_date, booking_received_time=booking_received_time)
#             db.session.add(order)
#             db.session.commit()
#             args = get_order_params(order)
#             signal_order_notify.send(self, args=args, status='booking')  # notify
#             return {'errcode': '0'}, 200
#         except Exception as e:
#             logger.error('[ApiOrderBooking] exception:%s' % e.message)
#             return {'errcode': '255', 'msg': e.message}, 500
#
#
# class ApiOrderModify(Resource):
#     def post(self, order_serial):
#         try:
#             uid = request.form.get('uid')
#             customer = Customer.query.filter_by(openid=uid).first()
#             if not customer:
#                 return {'result': 'error', 'msg': 'customer not exist'}, 500
#             order = Order.query.filter_by(order_serial=order_serial).first()
#             if not order:
#                 return {'result': 'error', 'msg': 'order not exist'}, 500
#             order.address_id = request.form.get('address')
#             address = CustomerAddress.query.filter_by(id=order.address_id, customer_id=customer.id).first()
#             if not address:
#                 return {'result': 'error', 'msg': 'address not exist'}, 500
#             order.address_id = address.id
#             if request.form.get('sum') != 'undefined':
#                 order.booking_clothes = request.form.get('sum')
#             if request.form.get('delivery_time') != 'undefined':
#                 order.booking_delivery_time = int(request.form.get('delivery_time'))
#             if request.form.get('delivery_date') != 'undefined':
#                 date_num = int(request.form.get('delivery_date'))
#                 order.booking_delivery_date = dt.datetime.now() + dt.timedelta(days=date_num)
#             if request.form.get('received_time') != 'undefined':
#                 order.booking_received_time = int(request.form.get('received_time'))
#             if request.form.get('received_date') != 'undefined':
#                 date_num = int(request.form.get('received_date'))
#                 order.booking_received_date = dt.datetime.now() + dt.timedelta(days=date_num)
#             db.session.add(customer)
#             db.session.add(order)
#             db.session.commit()
#             args = get_order_params(order)
#             signal_order_notify.send(self, args=args, status='update')  # notify
#             return {'errcode': '0'}, 200
#         except Exception as e:
#             return {'errcode': '255', 'msg': e.message}, 500
#
#
# class ApiOrderPayConfirm(Resource):
#     def post(self):
#         orderid = request.args.get('orderid')
#         order = Order.query.filter_by(order_serial=orderid).first()
#         code = order.to_pay(2)  # weixin pay
#         args = get_order_params(order)
#         signal_order_notify.send(self, args=args, status='pay-confirm')  # notify
#         return {'errcode': str(code)}, 200
#
#
# class ApiOrderCommentAndClose(Resource):
#     def post(self):
#         try:
#             dicts = request.form if request.form else request.args
#             order_serial = dicts.get('orderid')
#             uid = dicts.get('uid')
#             order = Order.query.filter_by(order_serial=order_serial).first()
#             comment = CustomerOrderReview.query.filter(CustomerOrderReview.customer_id == uid,
#                                                        CustomerOrderReview.order_serial == order_serial).first()
#             if not comment:
#                 comment = CustomerOrderReview()
#             comment.customer_id = uid
#             comment.order_serial = order_serial
#             comment.message = dicts.get('text')
#             comment.datetime = dt.datetime.now()
#             db.session.add(comment)
#             order.step('closed')  # auto commit: False
#             db.session.commit()
#             order_closed_process(order)
#             return {'errcode': '0'}, 200
#         except Exception, e:
#             logger.error(e)
#             return {'errcode': '255'}, 200
#
#
# class ApiOrderClose(Resource):
#     def post(self):
#         try:
#             orderid = request.args.get('orderid')
#             order = Order.query.filter_by(order_serial=orderid).first()
#             order.step('closed')
#             db.session.add(order)
#             db.session.commit()
#             order_closed_process(order)
#             return {'errcode': '0'}, 200
#         except:
#             return {'errcode': '255'}, 200
#
#
# class ApiTaskOrderMaintain(Resource):
#     def get(self):
#         try:
#             left = dt.datetime.today() - dt.timedelta(30)
#             auto_close_end = dt.datetime.today() - dt.timedelta(2)
#             auto_close = Order.query.filter(Order.paid == True, Order.status == 3,
#                                             Order.create_time.between(left, auto_close_end)).all()
#             for order in auto_close:
#                 logger.info('[TASK] auto close customer[%s] order[%s].' % (order.customer, order.order_serial))
#                 order.step('closed')
#                 db.session.add(order)
#                 db.session.commit()
#                 order_closed_process(order)
#             return {'auto_close': len(auto_close)}, 200
#         except:
#             return {'result': 255}, 200


def random_digit(length=10):
    str = ''
    chars = '0123456789'
    random = Random()
    for i in range(length):
        str += chars[random.randint(0, length)]
    return str


def create_order(shopid, price, openid, count):
    shop = Shop.query.get(shopid)
    customer = Customer.query.filter_by(openid=openid).first()
    serial = random_digit()
    card = random_digit()
    order = Order(order_serial=serial, card=card, shop_id=shop.id, customer_id=customer.id, pay_price=price)
    db.session.add(order)
    db.session.commit()
    return order


class ApiCardBuy(Resource):
    def post(self):
        try:
            args = json.loads(request.data)
            shopid = args.get('merchantId')
            price = args.get('price')
            count = args.get('count')
            openid = args.get('openid')
            order = create_order(shopid, price, openid, count)
            res, outputs = payable(request, order)
            logger.info('[ApiOrderPayable] data=%s' % str(outputs))
            if res == 0:
                outputs['order_id'] = order.order_serial
                return {'result': 0, 'content': outputs}, 200
            return {'result': res}, 200
        except Exception as e:
            print e.message
            return {'result': 254}, 200


restful_api.add_resource(ApiCardBuy, API_PREFIX + 'card/buy')
# restful_api.add_resource(ApiOrderBooking, API_PREFIX + 'order/booking')
# restful_api.add_resource(ApiOrderModify, API_PREFIX + 'order/modify/<string:order_serial>')
# restful_api.add_resource(ApiTaskOrderMaintain, API_PREFIX + 'task/order/maintain')
# restful_api.add_resource(ApiOrderCancel, API_PREFIX + 'order/cancel')
# restful_api.add_resource(ApiOrderClose, API_PREFIX + 'order/close')
# restful_api.add_resource(ApiOrderCommentAndClose, API_PREFIX + 'order/comment_and_close')
# restful_api.add_resource(ApiOrderPayConfirm, API_PREFIX + 'order/pay/confirm')
