# -*- coding: utf-8 -*-
from app import app
from cache.public import cache_url
from models import WechatMenu

__author__ = 'fengguanhua'
import time
import json
from flask import request, jsonify
from flask_weixin import FlaskWeixin
from wexin.util import *
from app import logger

from flask import Blueprint

weixin_module = Blueprint('weixin', __name__, static_folder='static')
weixin = FlaskWeixin(app)
app.add_url_rule('/weixin', view_func=weixin.view_func)


def get_menus_json():
    try:
        menulist = []
        menus = db.session.query(WechatMenu).filter(WechatMenu.parent_id == None).order_by(WechatMenu.seqid.asc()).all()
        for menu in menus:
            menulist.append(menu.to_dict())
        dicts = {"button": menulist}
        return dicts
    except:
        return None


@weixin('*')
def reply_all(**kwargs):
    return weixin.view_func()


@weixin_module.route('/api/menu/register', methods=['POST'])
def createMenu():
    menu = get_menus_json()
    logger.info('[WEIXIN] menu=%s' % menu)
    try:
        result = weixin.weixin_helper.create_menu(menu)
        result = jsonify(result)
        return result
    except Exception as e:
        logger.error(e.message)
        return jsonify({'result': 255, 'errmsg': e.message})


@weixin_module.route('/weixin_push', methods=['GET', 'POST'])
def weixin_push():
    cache_url(request.host_url)
    if request.data:
        data = json.loads(request.data)
        tag = data.get('tag')
        newsid = data.get('newsid')
        user = data.get('user')
    else:
        tag = request.args['tag']
        newsid = request.args['newsid']
        user = request.args['user']
    users = [user]
    if tag.find("news") >= 0:
        ret = weixin.weixin_reply.push_news_reply(weixin.weixin_helper, newsid, users)
    else:
        ret = weixin.weixin_reply.push_text_reply(weixin.weixin_helper, newsid, users)
    return str(ret)


@weixin_module.route('/update_customer_info')
def batch_update_customer_info():
    sucsess_count = 0
    error_count = 0
    total_count = 0
    openid = request.args.get('openid')
    customers = []
    if openid:
        customer = Customer.query.filter_by(openid=openid).first()
        if customer:
            customers.append(customer)
    else:
        customers = Customer.query.filter(Customer.nickname == None, Customer.head_image == None,
                                          Customer.active == True).all()
    for customer in customers:
        total_count += 1
        result = update_customer_info(customer.openid)
        if result:
            sucsess_count += 1
        else:
            error_count += 1
        time.sleep(0.5)
    return '{"err":"%d", "updated":%d, "all":%d}' % (error_count, sucsess_count, len(customers))
