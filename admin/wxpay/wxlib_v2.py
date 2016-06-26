# encoding=utf-8

import hashlib
import json
from random import Random
import urllib
import urllib2
import time
from app import config, logger
from wxpay.pub import para_filter, random_str, do_post

DELIVER_NOTIFY_URL = 'https://api.weixin.qq.com/pay/delivernotify'
ORDER_QUERY_URL = 'https://api.weixin.qq.com/pay/orderquery'
ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'


def build_form(parameter):
    base = {
        'bank_type': 'WX',
        'fee_type': '1',
        'input_charset': 'UTF-8',
        'partner': config.WXPAY_CONIFG['partnerId']
    }
    parameter.update(base)
    parameter['package'] = build_package(parameter)
    timestamp = str(int(time.time()))
    noncestr = random_str()
    pay_sign_array = {
        'appid': config.WEIXIN_APPID,
        'noncestr': noncestr,
        'package': parameter['package'],
        'timestamp': timestamp
    }
    key_filter = ['appid', 'timestamp', 'noncestr', 'package', 'appkey']
    pay_sign_array['paysign'] = build_sign(pay_sign_array, key_filter)
    pay_sign_array['signtype'] = 'SHA1'
    del pay_sign_array['appkey']
    return pay_sign_array


def build_package(parameter):
    filterParameter = para_filter(parameter)
    filterKeys = filterParameter.keys()
    filterKeys.sort()
    joined_string = '&'.join(['%s=%s' % (key.lower(), unicode(filterParameter[key])) for key in filterKeys])
    joined_string += '&key=' + config.WXPAY_CONIFG['partnerKey']
    m = hashlib.md5(joined_string.encode('utf-8'))
    m.digest()
    sign = m.hexdigest().upper()
    package = '&'.join(
        ['%s=%s' % (key, urllib.quote(unicode(filterParameter[key]).encode('utf-8'))) for key in filterKeys])
    package += '&sign=' + sign
    return package


def build_sign(parameter, key_filter):
    key_filter.sort()
    parameter['appkey'] = config.WXPAY_CONIFG['paySignKey']
    joined_string = '&'.join(['%s=%s' % (key.lower(), parameter[key]) for key in key_filter])
    sign = hashlib.sha1(joined_string).hexdigest()
    logger.info('[WEIXIN] qcode=%s, sign=%s' % (joined_string,sign))
    return sign


def build_delivery_sign(parameter):
    key_filter = ['appid', 'appkey', 'openid', 'transid', 'out_trade_no', 'deliver_timestamp', 'deliver_status',
              'deliver_msg']
    key_filter.sort()
    parameter['appkey'] = config.WXPAY_CONIFG['paySignKey']
    joined_string = '&'.join(['%s=%s' % (key.lower(), parameter[key]) for key in key_filter])
    sign = hashlib.sha1(joined_string).hexdigest()
    return sign


def build_right_sign(parameter):
    filter_key = ['appid', 'appkey', 'timestamp', 'openid']
    filter_key.sort()
    parameter['appkey'] = config.WXPAY_CONIFG['paySignKey']
    joined_string = '&'.join(['%s=%s' % (key.lower(), parameter[key]) for key in filter_key])
    sign = hashlib.sha1(joined_string).hexdigest()
    return sign


def build_warning_sign(parameter):
    filter_key = ['alarmcontent','appid','appkey','description','errortype','timestamp']
    filter_key.sort()
    parameter['appkey'] = config.WXPAY_CONIFG['paySignKey']
    joined_string = '&'.join(['%s=%s' % (key.lower(), parameter[key]) for key in filter_key])
    sign = hashlib.sha1(joined_string).hexdigest()
    return sign


def get_access_token():
    token_url = ACCESS_TOKEN_URL + '?grant_type=client_credential&appid=' + config.WEIXIN_APPID + '&secret=' + config.WEIXIN_SECRET
    urlopen = urllib2.urlopen(token_url, timeout=12000)
    result = urlopen.read()
    data = json.loads(result)
    if 'errcode' in data:
        return False
    return data['access_token']


def deliver_notify(parameter):
    url = DELIVER_NOTIFY_URL + '?access_token=' + get_access_token()
    parameter['appid'] = config.WEIXIN_APPID
    parameter['app_signature'] = build_delivery_sign(parameter)
    parameter['sign_method'] = 'sha1'
    del parameter['appkey']
    result = do_post(url, json.dumps(parameter))
    return json.loads(result)


def order_query(out_trade_no):
    if config.WXPAY_CONIFG != None or out_trade_no != None:
        return False
    url = ORDER_QUERY_URL + '?access_token=' + get_access_token()
    parameter = {
        'appid': config.WEIXIN_APPID,
        'package': 'out_trade_no=' + out_trade_no +
                   '&partner=' + config.WXPAY_CONIFG['partnerId'] +
                   '&sign=' + (hashlib.md5('out_trade_no=' + out_trade_no +
                                           '&partner=' + config.WXPAY_CONIFG['partnerId'] +
                                           '&key=' + config.WXPAY_CONIFG['partnerkey'])).lower(),
        'timestamp': int(time.time())
    }
    key_filter = ['appid', 'timestamp', 'noncestr', 'package', 'appkey']
    app_signature = build_sign(parameter, key_filter)
    parameter['app_signature'] = app_signature
    parameter['sign_method'] = 'sha1'
    result = do_post(url, json.dumps(parameter))
    return json.load(result)


def get_address_sign(parameter):
    parameter['appid'] = config.WEIXIN_APPID
    parameter['noncestr'] = random_str()
    parameter['timestamp'] = int(time.time())
    key_filter = ['appid', 'url', 'timestamp', 'noncestr', 'accesstoken']
    key_filter.sort()
    joined_string = '&'.join(['%s=%s' % (key.lower(), parameter[key]) for key in key_filter])
    sign = hashlib.sha1(joined_string).hexdigest()
    parameter['addrsign'] = sign
    parameter['scope'] = 'jsapi_address'
    parameter['signType'] = 'SHA1'
    return parameter


def build_qrcode_form(package_params, inparms):
    base = {
        'bank_type': 'WX',
        'fee_type': '1',
        'input_charset': 'UTF-8',
        'partner': config.WXPAY_CONIFG['partnerId']
    }
    package_params.update(base)
    package_params['package'] = build_package(package_params)
    pay_sign_array = {
        'appid': inparms['AppId'],
        'package': package_params['package'],
        'timestamp': inparms['TimeStamp'],
        'noncestr': inparms['NonceStr'],
        'retcode':'0',
        'reterrmsg':'OK'
    }
    key_filter = ['appid', 'appkey', 'package', 'timestamp', 'noncestr', 'retcode','reterrmsg']
    pay_sign_array['paysign'] = build_sign(pay_sign_array, key_filter)
    pay_sign_array['signtype'] = 'SHA1'
    del pay_sign_array['appkey']
    return pay_sign_array
