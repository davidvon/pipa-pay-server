# -*- coding: utf-8 -*-
from flask import render_template, request
from flask.ext.login import login_required
from flask.ext.restful import abort
from wtforms import SelectField
from app import db, app
from app.view import BaseModelView, admin
from models import City, Card, User


class ShopView(BaseModelView):
    column_filters = ('city.city_name', 'phone', 'name', 'phone')
    column_labels = {'city': u'城市', 'city.city_name': '城市名称', 'name': u'洗衣店名称', 'zone': '区域',
                     'address': u'地址', 'longitude': '经度', 'latitude': '纬度', 'phone': '联系电话',
                     'logo': '商标'}


class UserView(BaseModelView):
    column_list = ('city.city_name', 'customer', 'nickname', 'roles', 'active')
    column_exclude_list = ('register_time', 'password')
    form_excluded_columns = ('register_time', 'password')
    column_labels = {'city': u'城市', 'city.city_name': u'城市', 'customer': u'会员账号', 'register_time': u'认证时间',
                     'nickname': u'用户名', 'email': u'邮箱', 'active': u'状态',
                     'roles': u'角色'}
    form_overrides = dict(active=SelectField)
    form_args = dict(
            active=dict(choices=[('0', u'未激活'), ('1', u'已激活')])
    )

    def column_status_fmt(self, context, model, name):
        return '未激活' if model.active == 0 else '已激活'

    column_formatters = dict({"active": column_status_fmt})


class CityView(BaseModelView):
    column_filters = ('city_name',)
    column_labels = {'city_name': u'城市'}


class CardView(BaseModelView):
    can_delete = False
    column_labels = {'title': u'卡名称', 'sub_title': u'卡标签', 'card_id': u'微信卡号',
                     'merchant': u'商户', 'type': u'卡类型'}
    form_excluded_columns = ('card_id', 'type')
    list_template = './models/merchant_card_list.html'


admin.add_view(UserView(User, db.session, tagid='system-menu', icon='fa-gear', name=u"管理用户", category=u"基本设置"))
admin.add_view(CityView(City, db.session, tagid='system-menu', icon='fa-gear', name=u"服务城市", category=u"基本设置"))
admin.add_view(CardView(Card, db.session, tagid='system-menu', icon='fa-gear', name=u"会员卡信息", category=u"基本设置"))


@app.route('/merchant/weixin/card/<string:card_id>/<string:action>', methods=['GET'])
@login_required
def merchant_card_info(card_id, action):
    card = Card.query.filter_by(id=card_id).first()
    back_url = request.args.get('url') or '/admin/card'
    template_html = 'models/merchant_card_%s.html' % action
    return render_template(template_html, card=card, url=back_url, admin_base_template='base/_layout.html',
                           admin_view=admin.index_view), 200
