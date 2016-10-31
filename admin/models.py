# -*- coding: utf-8 -*-
from stringold import strip
from datetime import datetime
from flask.ext.security import UserMixin, RoleMixin
from sqlalchemy import Sequence

import config
from app import db

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
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'))
    city = db.relationship('City')
    customer_id = db.Column(db.Integer(), db.ForeignKey('customer.id'))
    customer = db.relationship('Customer')
    register_time = db.Column(db.DateTime(), default=datetime.now)
    active = db.Column(db.Integer, default=0, nullable=False)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def to_active(self):
        self.active = 1
        self.register_time = datetime.now()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '%r' % self.nickname

    def is_admin(self):
        return self.is_authenticated() and self.has_role(config.ROLE_ADMIN)

    def thumb_image(self):
        return self.customer.thumb_image() if self.customer else '/static/img/avatar_default.jpg'

    def name(self):
        return self.nickname

    def shop_name(self):
        if self.has_role(config.ROLE_ADMIN):
            return '%s 管理员' % self.city.city_name if self.city else '管理员'
        elif self.has_role(config.ROLE_SHOP_STAFF):
            return '%s 店员' % self.city.city_name if self.city else '店员'
        else:
            return '无权限'


class City(db.Model):
    id = db.Column(db.Integer(), Sequence('city_id_seq', start=1001, increment=1), primary_key=True)
    city_name = db.Column(db.String(32), unique=True, nullable=False)

    def __repr__(self):
        return self.city_name


class Merchant(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    logo = db.Column(db.String(64))
    lon_lat = db.Column(db.String(32), nullable=False)
    city_id = db.Column(db.Integer(), db.ForeignKey('city.id'))
    city = db.relationship(City)

    def __repr__(self):
        return self.name


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(32), unique=True, nullable=False)  # 服务器内部卡券号
    merchant_id = db.Column(db.Integer(), db.ForeignKey('merchant.id'), nullable=False)
    merchant = db.relationship(Merchant)
    title = db.Column(db.String(32), nullable=False)
    sub_title = db.Column(db.String(128))
    type = db.Column(db.Integer())  # 卡类型
    card_key = db.Column(db.String(32), unique=True, nullable=False)  # 前后台关联使用


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(32))
    nickname = db.Column(db.String(64))
    phone = db.Column(db.String(11))
    province = db.Column(db.String(20))
    city = db.Column(db.String(20))
    active = db.Column(db.BOOLEAN, default=True)
    last_visited = db.Column(db.DateTime(), default=datetime.now)
    sex = db.Column(db.Integer())
    head_image = db.Column(db.String(256))
    register_time = db.Column(db.DateTime(), default=datetime.now)
    cards = db.relationship('CustomerCard', backref='cards', lazy='dynamic')

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

    def thumb_image(self):
        return self.head_image if self.head_image else '/static/img/avatar_default.jpg'


class CustomerCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(64), db.ForeignKey('customer.openid'), nullable=False)
    customer = db.relationship(Customer)
    order_id = db.Column(db.String(32), db.ForeignKey('order.order_id'))
    order = db.relationship('Order')
    card_id = db.Column(db.String(32), db.ForeignKey('card.card_id'))  # 服务器内部卡券ID
    card = db.relationship(Card)
    card_code = db.Column(db.String(32))  # 动态分配的卡号
    img = db.Column(db.String(36))
    balance = db.Column(db.Float())
    wx_balance = db.Column(db.Float())
    bonus = db.Column(db.Float())
    claimed_time = db.Column(db.DateTime(), default=datetime.now)
    wx_binding_time = db.Column(db.DateTime())
    expire_date = db.Column(db.Date())
    status = db.Column(db.Integer())
    # 0:已购买未放入微信卡包 1: 已放入微信卡包未激活  2: 已放入微信卡包已激活 3:已过期 4: 赠送中 5:已成功赠送

    def __repr__(self):
        return "%s-%s" % (self.customer, self.card_code)

    def status_str(self):
        return ['已购买未入卡包',
                '已入卡包未激活',
                '已入卡包已激活',
                '已过期',
                '赠送中',
                '已赠送'][self.status]


class CustomerCardShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    share_customer_id = db.Column(db.String(64), db.ForeignKey('customer.openid'))
    share_customer = db.relationship(Customer)
    customer_card_id = db.Column(db.Integer(), db.ForeignKey('customer_card.id'))
    customer_card = db.relationship(CustomerCard)
    acquire_customer_id = db.Column(db.String(64))
    timestamp = db.Column(db.Integer())
    datetime = db.Column(db.DateTime(), default=datetime.now)
    content = db.Column(db.String(32))
    sign = db.Column(db.String(64), nullable=False)
    status = db.Column(db.Integer(), default=0)  # 0:转赠中未接收 1: 已被对方接收
    new_card_id = db.Column(db.Integer())  # TODO 需与老卡ID关联

    def status_str(self):
        return self.customer_card.status_str()


class CustomerTradeRecords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(64), db.ForeignKey('customer.openid'))
    customer = db.relationship(Customer)
    card_id = db.Column(db.String(32), db.ForeignKey('card.card_id'))
    card = db.relationship(Card)
    balance = db.Column(db.Integer())
    time = db.Column(db.DateTime())
    expire_date = db.Column(db.DateTime(), default=datetime.now)
    type = db.Column(db.Integer())  # 0:消费 1: 充值


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(32), unique=True, nullable=False)
    customer_id = db.Column(db.String(64), db.ForeignKey('customer.openid'), nullable=False)
    customer = db.relationship(Customer)
    card_id = db.Column(db.String(32), db.ForeignKey('card.card_id'), nullable=False)
    card = db.relationship(Card)
    face_amount = db.Column(db.Float, nullable=False)
    pay_amount = db.Column(db.Float, nullable=False)
    create_time = db.Column(db.DateTime(), default=datetime.now)
    paid = db.Column(db.BOOLEAN, nullable=False, default=0)
    order_type = db.Column(db.Integer, nullable=False, default=0)  # 1: 购卡, 2:充值
    card_count = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return self.order_id

    def is_payable(self):
        return not self.paid

    def paid_str(self):
        return ['', '购卡', '充值'][self.order_type]

    def order_type_str(self):
        return ['未支付', '已支付'][int(self.paid)]

    def get_order_params(self):
        args = {'customer': self.customer.show_name(), 'order_id': self.order_id, 'card_id': self.card_id,
                'order_time': str(self.create_time), 'face_amount': str(self.face_amount),
                'pay_amount': str(self.pay_amount), 'paid': self.paid,
                'order_type': self.order_type, 'order_type_str': self.order_type_str(),
                'card_count': self.card_count, 'paid_str': self.paid_str()}
        return args


class WechatMenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seqid = db.Column(db.String(5))
    name = db.Column(db.String(32), nullable=False)
    trigger_type = db.Column(db.String(1), default=config.MEDIA_TYPE_URL)
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
            if self.trigger_type == config.MEDIA_TYPE_URL:
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


class WechatTextReply(db.Model):
    __searchable__ = {'keyword': 'text', 'text': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(32), nullable=False)
    match_type = db.Column(db.String(1), default=config.LIKE_MATCH)
    text = db.Column(db.UnicodeText, nullable=False)


class WechatNewsReply(db.Model):
    __searchable__ = {'keyword': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(32), nullable=False)
    match_type = db.Column(db.String(1), default=config.LIKE_MATCH)
    image_news_id = db.Column(db.Integer(), db.ForeignKey('wechat_image_news.id'))
    image_news = db.relationship(WechatImageNews)


class WechatSystemReply(db.Model):
    __searchable__ = {'keyword': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(32), nullable=False)
    match_type = db.Column(db.String(1), default=config.LIKE_MATCH)
    menu_id = db.Column(db.Integer(), db.ForeignKey('wechat_menu.id'))
    menu = db.relationship(WechatMenu)


class WechatSubscribeReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    select_type = db.Column(db.String(1), default=config.MEDIA_TYPE_NEWS)
    text = db.Column(db.UnicodeText)
    image_news_id = db.Column(db.Integer(), db.ForeignKey('wechat_image_news.id'))
    image_news = db.relationship(WechatImageNews)
    menu_id = db.Column(db.Integer(), db.ForeignKey('wechat_menu.id'))
    menu = db.relationship(WechatMenu)


class WechatUselessWordReply(db.Model):
    __searchable__ = {'text': 'text'}
    id = db.Column(db.Integer, primary_key=True)
    select_type = db.Column(db.String(1), default=config.MEDIA_TYPE_NEWS)
    text = db.Column(db.UnicodeText)
    image_news_id = db.Column(db.Integer(), db.ForeignKey('wechat_image_news.id'))
    image_news = db.relationship(WechatImageNews)
    menu_id = db.Column(db.Integer(), db.ForeignKey('wechat_menu.id'))
    menu = db.relationship(WechatMenu)
