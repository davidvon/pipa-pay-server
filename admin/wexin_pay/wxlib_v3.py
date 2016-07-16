# -*- coding: utf-8 -*-
# 微信支付V3接口

import time
from app import logger
from config import WXPAY_CONIFG, WEIXIN_APPID
from wexin_pay.pub import xml_to_dict, do_post, dict_to_xml, random_str, sign_md5


def build_form(params, trade_type):
    base_params = {
        'appid': WEIXIN_APPID,
        'mch_id': WXPAY_CONIFG['mch_id'],
        'nonce_str': random_str(),
        'trade_type': trade_type,
        'body': params['body'],
        'out_trade_no': params['out_trade_no'],
        'total_fee': params['total_fee'],
        'spbill_create_ip': params['spbill_create_ip'],
        'notify_url': params['notify_url'],
        'openid': params['openid']
    }
    base_params['sign'] = sign_md5(base_params)
    return dict_to_xml(base_params)


def build_pay_prepayid_form_by(prepay_id):
    base_params = {
        'appId': WEIXIN_APPID,
        'timeStamp': str(int(time.time())),
        'nonceStr': random_str(),
        'package': str("prepay_id=%s" % prepay_id),
        'signType': "MD5"
    }
    base_params['paySign'] = sign_md5(base_params)
    return base_params


def unified_order_post(params, trade_type='JSAPI'):
    xml = build_form(params, trade_type).encode('utf-8')
    logger.info('[WEIXIN][unified_order_post] request:%s' % xml)

    response = do_post('https://api.mch.weixin.qq.com/pay/unifiedorder', xml)
    logger.info('[WEIXIN][unified_order_post] response: %s' % response)
    response_dict = xml_to_dict(response)
    return response_dict


def build_pay_prepayid_form(params):
    dict = unified_order_post(params)
    if dict['return_code'] == 'SUCCESS':
        form = build_pay_prepayid_form_by(dict['prepay_id'])
        logger.info('[WEIXIN][build_pay_prepayid_form] result: %s' % form)
        return 0, form
    return 254, dict['return_msg']


def build_dynamic_qrcode_form(params):
    dict = unified_order_post(params, 'NATIVE')
    if dict['return_code'] == 'SUCCESS':
        code_url = dict['code_url']
        logger.info('[WEIXIN] [build_jsapi_qrcode_form] code_url: %s' % code_url)
        return code_url
    return dict['return_msg']


def build_static_qrcode_form(params):
    dict = unified_order_post(params, 'NATIVE')
    if dict['return_code'] != 'SUCCESS':
        return None
    base_params = {
        'return_code':'SUCCESS',
        'appid': WEIXIN_APPID,
        'mch_id': WXPAY_CONIFG['mch_id'],
        'nonce_str': random_str(),
        'prepay_id': dict['prepay_id'],
        'result_code': 'SUCCESS',
    }
    base_params['sign'] = sign_md5(base_params)
    xml = dict_to_xml(base_params)
    logger.info('[WEIXIN][build_static_qrcode_form] response: %s' % xml)
    return xml