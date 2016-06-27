# -*- coding: utf-8 -*-
from stringold import strip
from flask import request
import os
import time
import datetime as dt
from datetime import datetime
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy import Sequence
from sqlalchemy.event import listens_for
from app import db, logger
from cache.public import url_from_cache
import config

__author__ = 'feng.guanhua'

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    def __init__(self, name, desc=''):
        self.name = name
        self.desc = desc

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    desc = db.Column(db.String(255))

    def __repr__(self):
        return self.desc


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), default="123456789")
    email = db.Column(db.String(255))
    shop_id = db.Column(db.Integer(), db.ForeignKey('shop.id'))
    shop = db.relationship('Shop')
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'))
    customer = db.relationship('Customer')
    register_time = db.Column(db.DateTime(), default=datetime.now)
    active = db.Column(db.Integer, default=0, nullable=False)
    id_card = db.Column(db.String(20))
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def to_active(self):
        self.active = 1
        self.register_time = datetime.now()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '%r' % self.nickname

    def thumb_image(self):
        return self.customer.thumb_image() if self.customer else '/static/img/avatar_default.jpg'

    def name(self):
        return self.nickname


class City(db.Model):
    id = db.Column(db.Integer(), Sequence('city_id_seq', start=1001, increment=1), primary_key=True)
    city_name = db.Column(db.String(32), unique=True, nullable=False)

    def __repr__(self):
        return self.city_name


class CityZone(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    zone_name = db.Column(db.String(32), unique=True, nullable=False)
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'))
    city = db.relationship(City)

    def __repr__(self):
        return '%s-%s' % (self.city, self.zone_name)


class Shop(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    logo = db.Column(db.String(64))
    longitude = db.Column(db.String(32), nullable=False)
    latitude = db.Column(db.String(32), nullable=False)
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'))
    city = db.relationship(City)

    def __repr__(self):
        return self.name


class ServiceMainCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    thumb_image = db.Column(db.String(256))
    categories = db.relationship('ServiceCategory', backref='categories', lazy='dynamic')

    def __repr__(self):
        return "%s" % self.name


class ServiceCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    main_category_id = db.Column(db.Integer(), db.ForeignKey('service_main_category.id'), nullable=False)
    main_category = db.relationship(ServiceMainCategory)
    thumb_image = db.Column(db.String(256))
    services = db.relationship('Service', backref='services', lazy='dynamic')

    def __repr__(self):
        return "%s %s" % (self.main_category, self.name)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_category_id = db.Column(db.Integer(), db.ForeignKey('service_category.id'))
    service_category = db.relationship(ServiceCategory)
    title = db.Column(db.String(256), nullable=False)
    sub_title = db.Column(db.String(256), nullable=False)
    thumb_image = db.Column(db.String(256), nullable=False)
    detail = db.Column(db.TEXT, nullable=False)
    properties = db.Column(db.TEXT, nullable=False)
    price = db.Column(db.Integer(), nullable=False)  # 价格下限
    flat_price = db.Column(db.Integer(), nullable=False)  # 价格上限
    price_unit = db.Column(db.String(16), default='')  # 单位
    status = db.Column(db.Integer(), nullable=False, default=1)  # 1:销售中 2:已下架
    award_score = db.Column(db.Integer, nullable=False, default=0)
    images = db.relationship('ServiceImages', backref='serivce_images', lazy='dynamic')
    create_time = db.Column(db.DateTime(), default=datetime.now)

    def __repr__(self):
        return '[%s] %s' % (self.service_category, self.title)

    def price_info(self):
        if self.price == self.flat_price:
            if self.price_unit:
                return '¥%s/%s' % (self.price, self.price_unit)
            else:
                return '¥%s' % self.price
        else:
            return '¥%s-%s' % (self.price, self.flat_price)


class ServiceImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'))
    service = db.relationship(Service)
    image = db.Column(db.String(512), nullable=False)

    def __repr__(self):
        return self.image


class CouponBase(object):
    public_date = db.Column(db.DateTime())
    disable_date = db.Column(db.DateTime())
    is_claimed = db.Column(db.Integer(), nullable=False, default=0)
    is_used = db.Column(db.Integer(), nullable=False, default=0)

    def is_enable(self):
        if self.is_used:
            return False
        if not self.disable_date:
            return True
        now = datetime.now()
        ret = now <= self.disable_date
        return ret

    def set_used(self, used=True):
        self.is_used = used

    def unused_try(self):
        if not self.is_enable() or not self.is_claimed:
            return
        if self.is_used:
            self.set_used(False)

    def title(self):
        pass

    def type(self):
        pass


class ShopCouponDiscount(db.Model, CouponBase):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer(), db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship(Shop)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'))
    service = db.relationship(Service)
    discount_percent = db.Column(db.Integer())  # 折扣
    match_amount = db.Column(db.Integer())  # 满足金额

    def __repr__(self):
        shop_service = self.service
        if self.match_amount:
            return '%s %s折满%s' % (shop_service, self.discount_percent, self.match_amount)
        else:
            return '%s %s折' % (shop_service, self.discount_percent)

    def title(self):
        return u"%s折扣券" % self.__repr__()

    def type(self):
        return 1


class ShopCouponDerate(db.Model, CouponBase):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer(), db.ForeignKey('shop.id'), nullable=False)
    shop = db.relationship(Shop)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'))
    service = db.relationship(Service)
    face_amount = db.Column(db.Integer(), nullable=False)  # 面值
    match_amount = db.Column(db.Integer())  # 满足金额

    def __repr__(self):
        shop_service = self.service
        if self.match_amount:
            return '%s 满%s抵%s' % (shop_service, self.match_amount, self.face_amount)
        else:
            return '%s 抵%s' % (shop_service, self.face_amount)

    def title(self):
        return u"满￥%s抵￥%s券" % (self.match_amount, self.face_amount)

    def type(self):
        return 2


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), unique=True)
    backend_name = db.Column(db.String(32))
    backend_password = db.Column(db.String(32))
    name = db.Column(db.String(32))
    nickname = db.Column(db.String(64))
    phone = db.Column(db.String(11))
    province = db.Column(db.String(20))
    city = db.Column(db.String(20))
    active = db.Column(db.BOOLEAN, default=True)
    logined = db.Column(db.BOOLEAN, default=False)
    last_visited = db.Column(db.DateTime(), default=datetime.now)
    sex = db.Column(db.Integer())
    head_image = db.Column(db.String(256))
    register_date = db.Column(db.Date(), default=datetime.now)
    register_time = db.Column(db.DateTime(), default=datetime.now)
    addresses = db.relationship('CustomerAddress', backref='addresses', lazy='dynamic')
    frequent = db.Column(db.BOOLEAN)

    def __repr__(self):
        return self.show_name()

    def show_name(self):
        if self.name and strip(self.name):
            return self.name
        elif self.nickname and strip(self.nickname):
            return self.nickname
        elif self.phone:
            return self.phone
        else:
            return '无姓名'

    def protect_name(self):
        if not self.backend_name:
            return ''
        return self.backend_name[:2] + '***' + self.backend_name[-2:]

    def protect_phone(self):
        if not self.phone:
            return ''
        return self.phone[:3] + '***' + self.phone[-3:]

    def thumb_image(self):
        return self.head_image if self.head_image else '/static/img/avatar_default.jpg'

    def is_shop_clerk(self):
        firm_user = User.query.filter(User.customer_id == self.id, User.active == 1).first()
        return True if firm_user else False

    def to_shop(self):
        clerk = User.query.filter(User.customer_id == self.id, User.active == 1).first()
        return clerk.shop if clerk else None

    def create_timetuple(self):
        return time.mktime(self.register_time.timetuple())

    def frequent_status_check(self):
        if self.frequent is True:
            return False
        count = Order.query.filter_by(customer_id=self.id, status=4).count()
        res = (count >= 2)
        if res:
            self.frequent = True
        return res


class CustomerAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), nullable=False)
    phone = db.Column(db.String(16), nullable=False)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship(Customer)
    province = db.Column(db.String(16), nullable=False)
    city = db.Column(db.String(16), nullable=False)
    zone = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    defaulted = db.Column(db.BOOLEAN, nullable=False, default=0)

    def __repr__(self):
        return "%s-%s %s" % (self.city, self.zone, self.address)


class CustomerCoupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship(Customer)
    shop_coupon_discount_id = db.Column(db.Integer(), db.ForeignKey('shop_coupon_discount.id'))
    shop_coupon_discount = db.relationship(ShopCouponDiscount)
    shop_coupon_derate_id = db.Column(db.Integer(), db.ForeignKey('shop_coupon_derate.id'))
    shop_coupon_derate = db.relationship(ShopCouponDerate)
    claimed_time = db.Column(db.DateTime())
    order_serial = db.Column(db.String(36), db.ForeignKey('order.order_serial'))
    order = db.relationship('Order')

    def __repr__(self):
        return '%s-%s' % (self.coupon_type(), self.get_actual_coupon().id)

    def coupon_type(self):
        # 1:discount; 2:derate
        return 1 if self.shop_coupon_discount else (2 if self.shop_coupon_derate else 0)

    def get_actual_coupon(self):
        return self.shop_coupon_discount if self.shop_coupon_discount else self.shop_coupon_derate


class CustomerScores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship(Customer)
    continue_days = db.Column(db.Integer(), nullable=False, default=0)
    total_scores = db.Column(db.Integer(), nullable=False, default=0)

    def __repr__(self):
        return '%s-%s' % (self.customer_id, self.total_scores)


class CustomerScoresDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship(Customer)
    scores = db.Column(db.Integer(), nullable=False, default=0)
    signin_date = db.Column(db.Date(), default=datetime.now, nullable=False)

    def __repr__(self):
        return '%s-%s' % ( self.customer, self.scores)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_serial = db.Column(db.String(36), unique=True, nullable=False)
    shop_id = db.Column(db.Integer(), db.ForeignKey('shop.id'))
    shop = db.relationship(Shop)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'))
    customer = db.relationship(Customer)
    phone = db.Column(db.String(36))
    create_date = db.Column(db.Date(), default=datetime.now)  # 预约洗衣时间（订单创建时间）
    create_time = db.Column(db.DateTime(), default=datetime.now)  # 预约洗衣时间
    pay_price = db.Column(db.Integer())
    status = db.Column(db.Integer(), default=0)  # 0:订单待确认 1:已上门收衣 2:洗涤中, 3:已派送, 4:订单关闭
    pay_date = db.Column(db.Date())  # 订单支付日期
    pay_time = db.Column(db.DateTime())  # 订单支付时间
    delivery_time = db.Column(db.DateTime())  # 商户取衣时间
    received_time = db.Column(db.DateTime())  # 客户收到衣服时间
    closed_time = db.Column(db.DateTime())  # 订单关闭时间
    washing_time = db.Column(db.DateTime())  # 洗涤时间
    pay_type = db.Column(db.Integer(), default=1)  # 1:现金支付, 2:微信支付
    address_id = db.Column(db.Integer(), db.ForeignKey('customer_address.id'))
    address = db.relationship(CustomerAddress)
    order_items = db.relationship('OrderItems', lazy='dynamic')
    booking_clothes = db.Column(db.Integer(), default=0)
    booking_delivery_date = db.Column(db.Date())
    booking_delivery_time = db.Column(db.Integer())  # 8: 8-9点
    booking_received_date = db.Column(db.Date())
    booking_received_time = db.Column(db.Integer())  # 8: 8-9点
    paid = db.Column(db.BOOLEAN, nullable=False, default=0)
    order_review = db.relationship('CustomerOrderReview', backref='review_order', lazy='dynamic')

    def __repr__(self):
        return self.order_serial

    def create_timetuple(self):
        return time.mktime(self.create_time.timetuple())

    @staticmethod
    def status_list():
        return ['订单待确认', '已上门收衣', '洗涤中', '已派送', '订单关闭']

    @staticmethod
    def status_code_list():
        return ['booking', 'delivery', 'washing', 'received', 'closed']

    def status_desc(self):
        statuses = self.status_list()
        return statuses[int(self.status)]

    def status_detail(self):
        if self.status == 0:
            return self.status_desc()
        if self.paid:
            pay_str = '已现金支付' if self.pay_type == 1 else '已微信支付'
        else:
            pay_str = '暂未支付'
        return "%s，%s" % (self.status_desc(), pay_str)

    @staticmethod
    def status_code_by(status):
        status_list = Order.status_code_list()
        return status_list[int(status)]

    def status_code(self):
        return self.status_code_by(int(self.status))

    def is_payable(self):
        return not self.paid

    def pay_type_desc(self):
        return '现金支付' if self.pay_type == 1 else '微信支付'

    def paid_desc(self):
        return '已支付' if self.paid else '未支付'

    def to_pay(self, pay_type):
        if self.is_payable():
            self.paid = True
            self.pay_type = pay_type
            self.pay_date = dt.date.today()
            self.pay_time = datetime.now()

    def step(self, status):
        if status == 'booking':
            self.status = 0
        elif status == 'delivery':
            self.status = 1
            self.delivery_time = datetime.now()
        elif status == 'washing':
            self.status = 2
            self.washing_time = datetime.now()
        elif status == 'received':
            self.status = 3
            self.received_time = datetime.now()
        elif status == 'closed':
            self.status = 4
            self.closed_time = datetime.now()

    def booking_date_check(self, type, dateid):
        next_day = dt.datetime.now() + dt.timedelta(days=dateid)
        date = self.booking_delivery_date if type == 1 else self.booking_received_date
        if date == next_day.date():
            return True
        else:
            return False

    def booking_datetime(self, tag):
        return '%s %s' % (self.booking_date_format(tag), self.booking_time_format(tag))

    def original_total_price(self):
        price = 0
        for item in self.order_items:
            price += (int(item.service.price) * item.count)
        return price

    def order_items_len(self):
        count = 0
        for item in self.order_items:
            count += item.count
        return count


class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def __repr__(self):
        return "%s" % self.name


class OrderItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_serial = db.Column(db.String(36), db.ForeignKey('order.order_serial', ondelete='CASCADE'), nullable=False)
    order = db.relationship(Order)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.id', ondelete='CASCADE'), nullable=False)
    service = db.relationship(Service)
    brand_id = db.Column(db.Integer(), db.ForeignKey('brand.id'))
    brand = db.relationship(Brand)
    color = db.Column(db.String(16))
    image_path = db.Column(db.String(128))
    count = db.Column(db.Integer(), default=1)

    def __repr__(self):
        return "%s" % self.service

    def img_url(self):
        return self.image_path or '/mobile/static/img/order_def.jpg'


class CustomerOrderReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_serial = db.Column(db.String(36), db.ForeignKey('order.order_serial', ondelete='CASCADE'), nullable=False)
    order = db.relationship(Order)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.id', ondelete='CASCADE'))
    service = db.relationship(Service)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship(Customer)
    review = db.Column(db.Integer, default=1)  # 1: good,2:medium, 3:bad
    message = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime(), default=datetime.now)
    reply = db.Column(db.Text)
    reply_time = db.Column(db.DateTime())

    def __repr__(self):
        return '%s-%s' % (self.order, self.message)


class CustomerFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship(Customer)
    type = db.Column(db.Integer)  # 0: 建议, 1: 投诉
    message = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime(), default=datetime.now)
    reply = db.Column(db.Text)
    reply_time = db.Column(db.DateTime())

    def __repr__(self):
        return '%s-%s' % (self.type, self.datetime)


class StatisticVisitUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship(Customer)
    visit_date = db.Column(db.Date(), default=datetime.now)
    visit_time = db.Column(db.DateTime(), default=datetime.now)

    def __repr__(self):
        return "%s %s" % (self.customer, self.page)


class StatisticVisitPages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(16), nullable=False)
    visit_times = db.Column(db.Integer(), default=0)
    visit_date = db.Column(db.Date(), default=dt.date.today())

    def __repr__(self):
        return "%s" % self.page


class StatisticServiceReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer(), db.ForeignKey('service.id'))
    service = db.relationship(Service)
    good_reviews = db.Column(db.Integer(), default=0)
    medium_reviews = db.Column(db.Integer(), default=0)
    bad_reviews = db.Column(db.Integer(), default=0)
    totals = db.Column(db.Integer(), default=0)

    def __repr__(self):
        return "%s" % self.service


MEDIA_TYPE_TEXT = u'1'
MEDIA_TYPE_NEWS = u'2'
MEDIA_TYPE_URL = u'3'


class WechatMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seqid = db.Column(db.String(5))
    name = db.Column(db.String(32), nullable=False)
    trigger_type = db.Column(db.String(1), default=MEDIA_TYPE_URL)
    message_text = db.Column(db.UnicodeText)
    url = db.Column(db.String(512))
    parent_id = db.Column(db.Integer(), db.ForeignKey('wechat_menu.id'))
    parent = db.relationship('WechatMenu', remote_side=[id], backref='sub_menus')

    def __repr__(self):
        return self.name

    # def sub_menus(self):
    # nodes = []
    # for node in self.parent.all():
    # if node.id == self.id:
    # nodes.append(node)
    # return nodes

    def root_menus(self):
        nodes = []
        for node in self.parent.all():
            if not node.id:
                nodes.append(node)
        return nodes

    def to_dict(self):
        nodes = self.sub_menus
        if not nodes:
            if self.trigger_type == MEDIA_TYPE_URL:
                return {'id': self.seqid, 'type': 'view', 'name': self.name, 'url': self.url}
            else:
                return {'id': self.seqid, 'type': 'click', 'name': self.name, 'key': self.message_text}
        json = {"name": self.name, "sub_button": []}
        sub_nodes = []
        for node in nodes:
            sub_nodes.append(node.to_dict())
        sub_nodes.sort(lambda x, y: cmp(x['id'], y['id']))
        json["sub_button"] = sub_nodes
        return json


class WechatImageNews(db.Model):
    __searchable__ = {'title': 'text', 'description': 'text', 'content': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32))
    title = db.Column(db.String(32), nullable=False)
    image_path = db.Column(db.String(128))
    description = db.Column(db.UnicodeText, nullable=False)
    url = db.Column(db.String(128))
    content = db.Column(db.UnicodeText, nullable=False)
    parent_id = db.Column(db.Integer(), db.ForeignKey('wechat_image_news.id'))
    parent = db.relationship('WechatImageNews', remote_side=[id], backref='sub_image_news')

    def __repr__(self):
        return self.title


LIKE_MATCH = u'1'
TOTAL_MATCH = u'2'


class WechatTextReply(db.Model):
    __searchable__ = {'keyword': 'text', 'text': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(32), nullable=False)
    match_type = db.Column(db.String(1), default=LIKE_MATCH)
    text = db.Column(db.UnicodeText, nullable=False)


class WechatNewsReply(db.Model):
    __searchable__ = {'keyword': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(32), nullable=False)
    match_type = db.Column(db.String(1), default=LIKE_MATCH)
    image_news_id = db.Column(db.Integer(), db.ForeignKey('wechat_image_news.id'))
    image_news = db.relationship(WechatImageNews)


class WechatSystemReply(db.Model):
    __searchable__ = {'keyword': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(32), nullable=False)
    match_type = db.Column(db.String(1), default=LIKE_MATCH)
    menu_id = db.Column(db.Integer(), db.ForeignKey('wechat_menu.id'))
    menu = db.relationship(WechatMenu)


class WechatSubscribeReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    select_type = db.Column(db.String(1), default=MEDIA_TYPE_NEWS)
    text = db.Column(db.UnicodeText)
    image_news_id = db.Column(db.Integer(), db.ForeignKey('wechat_image_news.id'))
    image_news = db.relationship(WechatImageNews)
    menu_id = db.Column(db.Integer(), db.ForeignKey('wechat_menu.id'))
    menu = db.relationship(WechatMenu)


class WechatUselessWordReply(db.Model):
    __searchable__ = {'text': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    select_type = db.Column(db.String(1), default=MEDIA_TYPE_NEWS)
    text = db.Column(db.UnicodeText)
    image_news_id = db.Column(db.Integer(), db.ForeignKey('wechat_image_news.id'))
    image_news = db.relationship(WechatImageNews)
    menu_id = db.Column(db.Integer(), db.ForeignKey('wechat_menu.id'))
    menu = db.relationship(WechatMenu)


def get_order_params(order):
    create_date = str(order.create_date.strftime("%Y-%m-%d"))
    create_time = str(order.create_time.strftime("%Y-%m-%d %H:%M:%S"))
    args = {'customer_id': order.customer.id, 'openid': order.customer.openid, 'name': order.address.name,
            'phone': order.phone, 'address': '%s' % order.address,
            'order_date': create_date, 'order_time': create_time, 'price': str(order.pay_price or ''),
            'order_id': order.id, 'order_serial': order.order_serial,
            'sum': order.booking_clothes,
            'delivery_time': '%s %s' % (order.booking_delivery_date, order.booking_time_format(1)),
            'received_time': '%s %s' % (order.booking_received_date, order.booking_time_format(2)),
            'status': order.status_desc(), 'paid': order.paid,
            'shop_id': order.shop_id}
    return args