# -*- coding: utf-8 -*-
from app import db, logger, restful_api
from models import Order, CustomerOrderReview, CustomerScores
import datetime as dt
from flask import request
from flask.ext.restful import Resource
from wxpay.views import payable

__author__ = 'fengguanhua'


def grant_customer_scores(order, customer):
    scores = 0
    for item in order.order_items.all():
        scores += item.service.award_score
    customer_scores = CustomerScores.query.filter_by(customer_id=customer.id).first()
    if not customer_scores:
        customer_scores = CustomerScores(customer_id=customer.id, total_scores=scores)
    else:
        customer_scores.total_scores += scores
    db.session.add(customer_scores)
    logger.info('[grant_customer_scores] grant customer:%s scores:%s' % (customer.id, scores))


def order_closed_process(order):
    try:
        customer = order.customer
        res = customer.frequent_status_check()
        if res:
            db.session.add(customer)
        grant_customer_scores(order, customer)
        db.session.commit()
    except Exception, e:
        logger.error('[order_closed_process] exception:%s' % e.message)


class ApiFoo(Resource):
    def get(self):
        return {'errcode': '0', 'title': 'welcome'}


class ApiOrderCommentAndClose(Resource):
    def post(self):
        try:
            dicts = request.form if request.form else request.args
            order_serial = dicts.get('orderid')
            uid = dicts.get('uid')
            order = Order.query.filter_by(order_serial=order_serial).first()
            comment = CustomerOrderReview.query.filter(CustomerOrderReview.customer_id == uid,
                                                       CustomerOrderReview.order_serial == order_serial).first()
            if not comment:
                comment = CustomerOrderReview()
            comment.customer_id = uid
            comment.order_serial = order_serial
            comment.message = dicts.get('text')
            comment.datetime = dt.datetime.now()
            db.session.add(comment)
            order.step('closed')  # auto commit: False
            db.session.commit()
            order_closed_process(order)
            return {'errcode': '0'}, 200
        except Exception, e:
            logger.error(e)
            return {'errcode': '255'}, 200


class ApiOrderClose(Resource):
    def post(self):
        try:
            orderid = request.args.get('orderid')
            order = Order.query.filter_by(order_serial=orderid).first()
            order.step('closed')
            db.session.add(order)
            db.session.commit()
            order_closed_process(order)
            return {'errcode': '0'}, 200
        except:
            return {'errcode': '255'}, 200


class ApiTaskOrderMaintain(Resource):
    def get(self):
        try:
            left = dt.datetime.today() - dt.timedelta(30)
            auto_close_end = dt.datetime.today() - dt.timedelta(2)
            auto_close = Order.query.filter(Order.paid == True, Order.status == 3,
                                            Order.create_time.between(left, auto_close_end)).all()
            for order in auto_close:
                logger.info('[TASK] auto close customer[%s] order[%s].' % (order.customer, order.order_serial))
                order.step('closed')
                db.session.add(order)
                db.session.commit()
                order_closed_process(order)
            return {'auto_close': len(auto_close)}, 200
        except:
            return {'result': 255}, 200


class ApiOrderPayable(Resource):
    def post(self):
        try:
            orderid = request.args.get('orderid')
            res, outputs = payable(request, orderid)
            logger.info('[ApiOrderPayable] data=%s' % str(outputs))
            if res == 0:
                return {'result': '0', 'content': outputs}, 200
            return {'result': str(res)}, 200
        except:
            return {'result': '254'}, 200


restful_api.add_resource(ApiFoo, '/foo')
restful_api.add_resource(ApiOrderPayable, '/api/order/payable')
restful_api.add_resource(ApiTaskOrderMaintain, '/api/task/order/maintain')
restful_api.add_resource(ApiOrderClose, '/api/order/close')
restful_api.add_resource(ApiOrderCommentAndClose, '/api/order/comment_and_close')
