# -*- coding: utf-8 -*-
import json
import random as Random
import datetime
import string
from api import API_PREFIX
from app import db, logger, restful_api
from flask import request
from flask.ext.restful import Resource
from models import Order, Customer, Merchant
from wexin_pay.views import payable

__author__ = 'fengguanhua'


# def grant_customer_scores(order, customer):
# scores = 0
#     for item in order.order_items.all():
#         scores += item.service.award_score
#     customer_scores = CustomerScores.query.filter_by(customer_openid=customer.id).first()
#     if not customer_scores:
#         customer_scores = CustomerScores(customer_openid=customer.id, total_scores=scores)
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
#             order = Order.query.filter_by(order_id=orderid).first()
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
#             order_id = order_id_increment()
#             address = CustomerAddress.query.filter_by(id=address_id, customer_openid=customer.id).first()
#             if not address:
#                 return {'result': 'error', 'msg': 'address not exist'}, 500
#             order = Order(order_id=order_id, customer_openid=customer.id, address_id=address_id,
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
#     def post(self, order_id):
#         try:
#             uid = request.form.get('uid')
#             customer = Customer.query.filter_by(openid=uid).first()
#             if not customer:
#                 return {'result': 'error', 'msg': 'customer not exist'}, 500
#             order = Order.query.filter_by(order_id=order_id).first()
#             if not order:
#                 return {'result': 'error', 'msg': 'order not exist'}, 500
#             order.address_id = request.form.get('address')
#             address = CustomerAddress.query.filter_by(id=order.address_id, customer_openid=customer.id).first()
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
#         order = Order.query.filter_by(order_id=orderid).first()
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
#             order_id = dicts.get('orderid')
#             uid = dicts.get('uid')
#             order = Order.query.filter_by(order_id=order_id).first()
#             comment = CustomerOrderReview.query.filter(CustomerOrderReview.customer_openid == uid,
#                                                        CustomerOrderReview.order_id == order_id).first()
#             if not comment:
#                 comment = CustomerOrderReview()
#             comment.customer_openid = uid
#             comment.order_id = order_id
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
#             order = Order.query.filter_by(order_id=orderid).first()
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
#                 logger.info('[TASK] auto close customer[%s] order[%s].' % (order.customer, order.order_id))
#                 order.step('closed')
#                 db.session.add(order)
#                 db.session.commit()
#                 order_closed_process(order)
#             return {'auto_close': len(auto_close)}, 200
#         except:
#             return {'result': 255}, 200


def random_digit(length=10):
    return ''.join(Random.sample(string.digits, length))


def create_order(card_id, amount, openid, count):
    customer = Customer.query.filter_by(openid=openid).first()
    serial = random_digit()
    pay_amount = int(count*0.99)
    order = Order(order_id=serial, card_id=card_id, customer_id=customer.id, face_amount=amount,
                  card_count=count, pay_amount=pay_amount, order_type=1, paid=False)
    return order


# restful_api.add_resource(ApiOrderBooking, API_PREFIX + 'order/booking')
# restful_api.add_resource(ApiOrderModify, API_PREFIX + 'order/modify/<string:order_id>')
# restful_api.add_resource(ApiTaskOrderMaintain, API_PREFIX + 'task/order/maintain')
# restful_api.add_resource(ApiOrderCancel, API_PREFIX + 'order/cancel')
# restful_api.add_resource(ApiOrderClose, API_PREFIX + 'order/close')
# restful_api.add_resource(ApiOrderCommentAndClose, API_PREFIX + 'order/comment_and_close')
# restful_api.add_resource(ApiOrderPayConfirm, API_PREFIX + 'order/pay/confirm')
