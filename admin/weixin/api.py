# -*- coding: utf-8 -*-
import time
import json
from flask import jsonify, session, request
from app import app, db, redis_client, restful_api, logger
from flask.ext.restful import Resource
from models import Order
from weixin.views import weixin

__author__ = 'fengguanhua'


class ApiQrcode(Resource):
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


class WeixinTemplateNotify(Resource):
    def post(self):
        # cache_url(request.host_url)
        # data = json.loads(request.data)
        # car_groupon_id = data.get('car_groupon_id')
        # car_groupon = Car_groupon.query.filter_by(id=car_groupon_id).first()
        # if not car_groupon:
        #     return {'errcode': 255, 'return':'没有找到团购信息' }, 200
        # start_date_str = str(car_groupon.groupon_date_start)
        # end_date_str = str(car_groupon.groupon_date_end)
        # start_end_date = "%s 到 %s" % (start_date_str, end_date_str)
        # data['start_end_date'] = start_end_date
        # data['car_brand'] = car_groupon.__repr__()
        # from weixin.notify import CarGrouponInfoNotify
        # customer_names = ''
        # customers = []
        # for groupon_customer in car_groupon.customers:
        #     groupon_notify = CarGrouponInfoNotify()
        #     data['url'] = "%smobile/groupon/%s?uid=%s" % (url_from_cache(), car_groupon_id,
        #                                                   groupon_customer.customer.openid)
        #     groupon_notify.notify(data, groupon_customer.customer.openid)
        #     customer_names = '%s,%s' % (customer_names, str(groupon_customer.customer))
        #     customers.append(groupon_customer.customer)
        # ret = '推送：%s人\n推送人员列表：%s' % (len(customers), customer_names[1:])
        # return {'errcode': 0, 'return': ret}, 200
        pass

restful_api.add_resource(ApiQrcode, '/weixin/qrcode')
restful_api.add_resource(WeixinTemplateNotify, '/weixin/template/notify')