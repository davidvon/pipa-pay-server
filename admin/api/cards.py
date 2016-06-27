# -*- coding: utf-8 -*-
from api import API_PREFIX
from app import restful_api
from flask.ext.restful import Resource

__author__ = 'fengguanhua'


class ApiCards(Resource):
    def get(self):
        return [dict(price=500, title='沃尔玛GIFT卡', logo="/static/demo/card_logo.png",
                     img='/static/demo/card_blue.png', expireDate='2018-05'),
                dict(price=3000, title='沃尔玛VIP至尊卡', logo="/static/demo/card_logo.png",
                     img='/static/demo/card_green.png', expireDate='2016-10'),
                dict(price=1200, title='沃尔玛洗车卡', logo="/static/demo/card_logo.png",
                     img='/static/demo/card_red.png', expireDate='2019-12')]


restful_api.add_resource(ApiCards, API_PREFIX + 'cards')
