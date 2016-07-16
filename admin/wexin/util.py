# coding: utf-8
import random
import string
import datetime as dt
from datetime import datetime
from time import sleep

from app import db, logger
from models import Customer
from utils.util import async


def update_customer_info(openid):
    try:
        logger.info('[WEIXIN] customer[%s] update info.' % openid)
        from wexin.views import weixin

        userinfo = weixin.weixin_helper.get_user_info(openid)
        customer = Customer.query.filter(Customer.openid == openid).one()
        customer.active = userinfo['subscribe']
        if customer.active:
            customer.province = userinfo['province']
            customer.city = userinfo['city']
            customer.sex = userinfo['sex']
            customer.head_image = userinfo['headimgurl']
            customer.nickname = userinfo['nickname']
            customer.register_time = dt.datetime.utcfromtimestamp(userinfo['subscribe_time']) + dt.timedelta(hours=8)
            customer.register_date = customer.register_time.date()
        db.session.add(customer)
        db.session.commit()
        logger.info('[WEIXIN] customer[%s] update info[%s] done.' % (openid, userinfo))
        return True
    except Exception, e:
        logger.error('[WEIXIN] customer[%s] update info error:%s' % (openid, str(e)))
        return False


def create_customer_try(openid):
    customer = Customer.query.filter(Customer.openid == openid).first()
    if customer:
        customer.active = True
        customer.last_visited = datetime.now()
    else:
        customer = Customer(openid=openid, active=True)
    db.session.add(customer)
    db.session.commit()
    logger.info('[WEIXIN] create customer[%s] done.' % openid)


def unsubscribe_customer(openid):
    customer = Customer.query.filter(Customer.openid == openid).first()
    if not customer: return
    customer.active = False
    customer.logined = False
    db.session.add(customer)
    db.session.commit()
    logger.info('[WEIXIN] customer[%s] unsubscribed.' % openid)


@async
def async_update_customer_info(openid):
    logger.info('[async_update_customer_info] openid:%s start.' % openid)
    sleep(1)
    update_customer_info(openid)


@async
def async_unsubscribe_customer(openid):
    sleep(1)
    unsubscribe_customer(openid)


def nonce_str(num=12):
    return ''.join(random.sample(string.ascii_letters, num))
