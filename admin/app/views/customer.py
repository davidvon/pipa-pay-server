# -*- coding: utf-8 -*-
from os import abort
from flask import request, render_template
from flask.ext.login import login_required
from markupsafe import Markup
from wtforms import SelectField
from flask.ext.admin.contrib.sqla import ModelView
from app import db, app
from app.view import admin, BaseModelView
from models import Customer, Order, CustomerCard, CustomerCardShare


class CustomerView(BaseModelView):
    can_create = False
    can_delete = False
    column_filters = ('nickname', 'name', 'openid', 'phone')
    form_excluded_columns = ('register_date', 'register_time', 'city', 'head_image', 'sex',
                             'active', 'province', 'last_visited', 'openid', 'cards', 'name')
    column_list = ('name', 'nickname', 'phone', 'city', 'cards', 'active')
    column_searchable_list = ('nickname', 'name', 'openid', 'phone')
    form_overrides = dict(sex=SelectField, active=SelectField)
    form_args = dict(
            sex=dict(choices=[(u'0', u''), (u'1', u'男'), (u'2', u'女')]),
            active=dict(choices=[(u'1', u'已激活'), (u'2', u'已注销')])
    )
    column_labels = {'name': '客户', 'openid': u'微信ID', 'nickname': u'微信名',
                     'active': u'已注册', 'last_visited': u'上次访问时间',
                     'sex': u'性别', 'phone': u'电话', 'head_image': '头像',
                     'register_date': '注册时间', 'city': '城市', 'cards': '会员卡'}
    form_widget_args = {
        'nickname': {'readonly': True},
    }

    def is_action_allowed(self, name):
        if name == 'push' and not self.can_push:
            return False
        if name == 'delete' and not self.can_delete:
            return False
        return super(ModelView, self).is_action_allowed(name)

    def image_fmt(self, context, model, name):
        return Markup('<img style="width:30px;margin-right:10px;" src=%s>%s</img>' %
                      (model.head_image, model.show_name()))

    def card_fmt(self, context, model, name):
        card = model.cards.first()
        return Markup('<a href="/admin/customercard/?search=%s">%s</a>' %
                      (card.card_code, card.card_code))

    column_formatters = dict({'name': image_fmt, 'cards': card_fmt})


class CustomerCardView(BaseModelView):
    can_edit = False
    can_delete = False
    column_filters = ('customer.nickname', 'card_code', 'order.order_id')
    column_default_sort = ('customer.nickname', True)
    form_excluded_columns = ('card',)
    column_exclude_list = ('img', 'cards', 'claimed_time', 'expire_date', 'order')
    column_searchable_list = ('card_code', 'order.order_id')
    column_labels = {'customer': '客户', 'customer.nickname': '客户', 'order': u'订单',
                     'order.order_id': u'订单', 'card': u'会员卡', 'card_code': u'卡号',
                     'amount': u'金额', 'wx_amount': u'微信金额',
                     'claimed_time': u'认领时间', 'wx_binding_time': u'微信绑定时间',
                     'expire_date': u'过期日期', 'status': '状态', 'credit':'积分'}

    def status_format(self, context, model, name):
        return model.status_str()

    def card_format(self, context, model, name):
        return model.card.title

    column_formatters = dict(dict(status=status_format, card=card_format))
    list_template = './models/customer_card_list.html'

class CustomerCardShareView(BaseModelView):
    column_filters = ('share_customer.nickname', 'customer_card.card_code', 'acquire_customer_id')
    column_default_sort = ('share_customer.nickname', True)
    # form_excluded_columns = ('card',)
    column_exclude_list = ('content', 'timestamp', 'sign')
    column_searchable_list = ('customer_card.card_code',)
    column_labels = {'share_customer': '分享客户', 'share_customer.nickname': '分享客户',
                     'customer_card': u'会员卡', 'customer_card.card_code': u'卡号',
                     'content': u'分享语', 'datetime': u'分享时间', 'status': u'状态',
                     'new_card_id': '新卡ID', 'acquire_customer_id': '受赠客户'}

    def share_customer_fmt(self, context, model, name):
        return model.share_customer.show_name()

    def share_card_code_fmt(self, context, model, name):
        card = model.share_customer.cards.first()
        return card.card_code

    def acquire_customer_format(self, context, model, name):
        customer = Customer.query.filter_by(openid=model.acquire_customer_id).first()
        return customer.show_name()

    def status_format(self, context, model, name):
        return model.status_str()

    column_formatters = dict({'share_customer': share_customer_fmt,
                              'acquire_customer_id': acquire_customer_format,
                              'customer_card': share_card_code_fmt,
                              'status': status_format})


admin.add_view(CustomerView(Customer, db.session, tagid='customer-menu', icon='fa-group', name=u"会员",
                            category=u"会员管理"))
admin.add_view(CustomerCardView(CustomerCard, db.session, tagid='customer-menu', icon='fa-group', name=u"会员卡",
                                category=u"会员管理"))
admin.add_view(CustomerCardShareView(CustomerCardShare, db.session, tagid='customer-menu', icon='fa-group',
                                     name=u"卡赠送", category=u"会员管理"))


@app.route('/customer/<string:customer_id>', methods=['GET', 'POST'])
@login_required
def customer_info(customer_id):
    customer = Customer.query.filter_by(id=customer_id).first()
    back_url = request.args.get('url')
    if not customer:
        abort(404)
    if request.method == 'GET':
        orders = Order.query.filter_by(customer_id=customer.id).order_by(Order.create_time.desc()).all()
        return render_template('models/customer_info.html', customer=customer, address_list=customer.addresses.all(),
                               orders=orders, url=back_url, admin_base_template='base/_layout.html',
                               admin_view=admin.index_view), 200


@app.route('/customer/card/<string:card_id>', methods=['GET'])
@login_required
def customer_card_info(card_id):
    card = CustomerCard.query.filter_by(card_id=card_id).first()
    back_url = request.args.get('url')
    return render_template('models/customer_card_info.html', card=card, url=back_url,
                           admin_base_template='base/_layout.html',
                           admin_view=admin.index_view), 200