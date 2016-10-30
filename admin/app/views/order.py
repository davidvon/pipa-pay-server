# -*- coding: utf-8 -*-
from flask import abort, redirect, current_app, flash, request
from flask import render_template
from flask.ext.login import login_required, current_user
from markupsafe import Markup
from wtforms import SelectField
from flask.ext.admin import form, expose
from flask.ext.admin.contrib.sqla import filters

import config
from app import app, db
from app.view import admin, BaseModelView, BaseAdminView, StaffModelView
from models import Customer, Order
from signals import signal_order_notify


# class OrderView(StaffModelView):
#     # can_create = False
#     column_list = ('address.name', 'address.phone', 'create_time', 'pay_price', 'status', 'pay_type',
#                    'booking_clothes', 'paid')
#     form_excluded_columns = ('create_date', 'order_items', 'items')
#     column_searchable_list = ('address.name', 'address.phone', 'create_date')
#     column_filters = ('address.name', 'address.phone', 'create_date', 'pay_date',
#                       filters.FilterEqual(
#                           Order.order_type, '订单状态',
#                           options=(('0', u'已下单'), ('1', u'已上门收衣'), ('2', u'洗涤中'), ('3', u'已派送'), ('4', u'订单关闭')))
#                       )
#     column_labels = {'customer': u'客户', 'pay_price': '金额',
#                      'create_time': u'订单时间', 'status': '状态',
#                      'pay_type': '支付方式', 'order_items': '订单明细', 'phone': '电话',
#                      'delivery_time': '客服取衣时间', 'received_time': '客服送衣时间', 'shop': '洗衣店',
#                      'closed_time': '订单关闭时间', 'address': '收货地址', 'booking_clothes': '件数/㎡',
#                      'booking_delivery_date': '预约取衣日期', 'booking_delivery_time': '预约取衣时间',
#                      'booking_received_date': '预约送衣日期', 'booking_received_time': '预约送衣时间',
#                      'order_items.service': '服务', 'paid': '是否支付', 'pay_date': '支付日期',
#                      'customer.phone': '客户手机', 'customer.name': '客户姓名', 'washing_time': '开始洗涤时间',
#                      'create_date': '下单日期', 'address.name': '联系人姓名', 'address.phone': '联系人电话'
#                      }
#     column_sortable_list = (('customer', Customer.nickname), 'create_time',
#                             'pay_price', 'status', 'pay_type')
#     edit_template = 'models/order_create.html'
#     list_template = 'models/order_list.html'
#     column_default_sort = ('create_time', True)
#
#     form_overrides = dict(status=SelectField, pay_type=SelectField, booking_time=SelectField, paid=SelectField)
#     booking_choices = []
#     for i in range(7, 21):
#         booking_choices.append((str(i), '%s:00-%s:00' % (i, i + 1)))
#
#     form_args = dict(
#         status=dict(
#             choices=[('0', u'已下单'), ('1', u'已上门收衣'), ('2', u'洗涤中'), ('3', u'已派送'), ('4', u'订单关闭')]),
#         pay_type=dict(choices=[('1', u'现金'), ('2', u'微信')]),
#         paid=dict(choices=[('0', u'未支付'), ('1', u'已支付')]),
#         booking_time=dict(choices=booking_choices),
#     )
#
#     def name_format(self, context, model, name):
#         return Markup('<a href=/customer/info/%s>%s</a>' % (model.customer.id, model.address.name))
#
#     @staticmethod
#     def pay_status_fmt(context, model, name):
#         return model.status_desc()
#
#     @staticmethod
#     def pay_type_fmt(context, model, name):
#         return '现金' if model.pay_type == 1 else '微信'
#
#     @staticmethod
#     def pay_price_format(context, model, name):
#         return '¥%s' % model.pay_price if model.pay_price else ''
#
#     def booking_time_format(self, context, model, name):
#         booking = {7: '7:00-8:00', 8: '8:00-9:00', 9: '9:00-10:00', 10: '10:00-11:00', 11: '11:00-12:00',
#                    12: '12:00-13:00', 13: '13:00-14:00', 14: '14:00-15:00', 15: '15:00-16:00',
#                    16: '16:00-17:00', 17: '17:00-18:00', 18: '18:00-19:00', 19: '19:00-20:00',
#                    20: '20:00-21:00'}
#         if name == 'booking_delivery_time':
#             return booking[model.booking_delivery_time]
#         else:
#             return booking[model.booking_received_time]
#
#     column_formatters = dict({"status": pay_status_fmt, "pay_type": pay_type_fmt,
#                               'booking_delivery_time': booking_time_format,
#                               'booking_received_time': booking_time_format,
#                               'pay_price': pay_price_format,
#                               'address.name': name_format
#                               })
#
#     def get_query(self):
#         if current_user.is_admin():
#             return super(OrderView, self).get_query()
#         return super(OrderView, self).get_query().filter_by(shop_id=current_user.shop_id)
#
#     def get_count_query(self):
#         if current_user.is_admin():
#             return super(OrderView, self).get_count_query()
#         return super(OrderView, self).get_count_query().filter_by(shop_id=current_user.shop_id)
#


class CustomerOrderReviewView(BaseModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_exclude_list = ('reply', 'reply_time', 'review', 'service')
    column_filters = ('customer.name', )
    column_labels = {'order': u'订单', 'service': u'服务', 'customer': '客户',
                     'customer.name': '客户', 'message': '评价', 'publish_time': '发布时间'}


# class UndoOrderView(UserRoleBaseModelView):
# can_create = False
# column_exclude_list = ('shop', 'create_date', 'delivery_time', 'received_time', 'closed_time', 'address')
# form_excluded_columns = ('create_date',)
# column_filters = ('shop.name', 'customer', 'order_serial', 'status', 'pay_time')
# column_labels = {'order_serial': u'单号', 'customer': u'客户', 'pay_price': '金额',
# 'create_time': u'订单时间', 'status': '状态', 'pay_time': '支付时间',
# 'pay_type': '支付方式', 'coupon': '优惠券', 'coupons': '优惠券', 'order_items': '订单明细',
# 'delivery_time': '派发时间', 'received_time': '收货时间', 'shop': '洗衣店',
# 'closed_time': '订单关闭时间', 'address': '收货地址'}
# column_sortable_list = (('customer', Customer.nickname), 'order_serial', 'create_time', 'pay_time',
# 'pay_price', 'status', 'pay_type')
# form_overrides = dict(status=SelectField, pay_type=SelectField)
# form_args = dict(
# status=dict(choices=[('0', u'未支付'), ('1', u'已支付'), ('2', u'待收货'), ('3', u'已收货'), ('4', u'已关闭')]),
# pay_type=dict(choices=[('1', u'现金'), ('2', u'微信'), ('3', u'优惠券')]),
#     )
#     form_widget_args = {
#         'order_serial': {'readonly': True},
#         'customer': {'disabled': True}
#     }
#
#     def pay_status_fmt(self, context, model, name):
#         return model.status_desc()
#
#     def pay_type_fmt(self, context, model, name):
#         return '现金' if model.pay_type == 1 else ('微信' if model.pay_type == 2 else '优惠券')
#
#     column_formatters = dict({"status": pay_status_fmt, "pay_type": pay_type_fmt})
#
#     def get_query(self):
#         if current_user.is_admin():
#             return super(OrderView, self).get_query()
#         return super(OrderView, self).get_query().filter(self.model.shop_id == current_user.shop_id)
#
#     def get_count_query(self):
#         if current_user.is_admin():
#             return super(OrderView, self).get_count_query()
#         return super(OrderView, self).get_count_query().filter(self.model.shop_id == current_user.shop_id)

# class CustomerOrderReviewView(BaseModelView):
#     column_filters = (
#         'order', 'customer.name', 'customer.nickname', 'customer.phone', 'publish_time', 'message', 'reply' )
#     column_labels = {'order': u'订单', 'customer': u'客户', 'message': u'内容', 'publish_time': '发布时间',
#                      'reply': '回复', 'reply_time': '回复时间', 'customer.name': '客户姓名',
#                      'customer.nickname': '客户昵称', 'customer.phone': '客户电话', 'stars': '评价分'}


# class CustomerFeedbackView(BaseModelView):
#     # can_create = False
#     can_delete = False
#     form_overrides = dict(type=SelectField)
#     form_args = dict(
#         type=dict(choices=[('0', u'建议'), ('1', u'投诉')])
#     )
#     column_labels = {'customer': u'客户', 'type': u'类型', 'message': u'内容', 'publish_time': '发布时间',
#                      'reply': '回复', 'reply_time': '回复时间', 'customer.name': '客户姓名',
#                      'customer.nickname': '客户昵称', 'customer.phone': '客户电话'}
#
#     def type_fmt(self, context, model, name):
#         return '建议' if 0 == model.type else '投诉'
#
#     column_formatters = dict({"type": type_fmt})


# class StatisticVisitPagesView(BaseModelView):
#     column_labels = {'page': u'页面', 'visit_times': u'访问次数', 'visit_date': u'访问日期'}
#
#
# class StatisticVisitUsersView(BaseModelView):
#     column_exclude_list = ('visit_date',)
#     form_excluded_columns = ('visit_date',)
#     column_labels = {'customer': u'客户', 'visit_time': u'访问时间'}


class NewOrderListView(BaseAdminView):
    @expose('/')
    def index(self):
        return render_template('models/order_new_list.html', admin_view=self)


class DeliveryOrderListView(BaseAdminView):
    @expose('/')
    def index(self):
        return render_template('models/order_delivery_list.html', admin_view=self)

    def is_accessible(self):
        res = current_user.has_role(config.ROLE_SHOP_STAFF) or \
              current_user.has_role(config.ROLE_SHOP_STAFF_READONLY) or \
              current_user.has_role(config.ROLE_ADMIN) or \
              current_user.has_role(config.ROLE_FETCH_STEWARD) or \
              current_user.has_role(config.ROLE_POST_STEWARD)
        return res


class ReceivedOrderListView(BaseAdminView):
    @expose('/')
    def index(self):
        return render_template('models/order_received_list.html', admin_view=self)

    def is_accessible(self):
        res = current_user.has_role(config.ROLE_SHOP_STAFF) or \
              current_user.has_role(config.ROLE_SHOP_STAFF_READONLY) or \
              current_user.has_role(config.ROLE_ADMIN) or \
              current_user.has_role(config.ROLE_FETCH_STEWARD) or \
              current_user.has_role(config.ROLE_POST_STEWARD)
        return res


@app.route('/order/info/<string:order_id>', methods=['GET', 'POST'])
@app.route('/order/info/<string:order_id>/<int:tab_index>')
@login_required
def order_info(order_id, tab_index=1):
    order = Order.query.filter_by(order_id=order_id).first()
    back_url = request.args.get('url') or '/order/info/%s' % order.order_id
    if not order:
        abort(404)
    if request.method == 'GET':
        return render_template('models/order_info.html', order=order, tab=tab_index,
                               url=request.url, admin_base_template='base/_layout.html',
                               admin_view=admin.index_view), 200
    elif request.method == 'POST':
        order.city_id = request.form['city_id']
        order.pay_price = request.form['pay_price']
        order.pay_type = int(request.form['pay_type'])
        paid = int(request.form['paid'])
        if not order.address_id:
            flash('上门地址必须输入')
            return redirect(request.referrer)
        if not order.pay_price:
            flash('订单金额必须输入')
            return redirect(request.referrer)
        if not order.booking_clothes:
            flash('衣服件数必须输入')
            return redirect(request.referrer)
        status = int(request.form['status'])
        if status > order.status:
            status_notify_tag = True
        status_info = Order.status_code_by(status)
        order.step(status_info)
        if paid:
            order.to_pay(order.pay_type)
        db.session.add(order)
        db.session.commit()
        return redirect(back_url)


admin.add_view(NewOrderListView(tagid='custom-menu', icon='fa-shopping-cart', name=u"订单", category=u"会员管理"))
