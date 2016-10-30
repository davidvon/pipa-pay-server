# -*- coding: utf-8 -*-
import time
from urllib import urlencode

from flask import request, current_app

from app import app, logger, db
from config import WXPAY_CONIFG, WEIXIN_APPID
from models import Order
from signals import signal_order_notify
from wexin_pay.pub import verify_notify, xml_to_dict, random_str, sign_md5, format_param_map
from wexin_pay.wxlib_v2 import build_warning_sign, build_right_sign, get_address_sign
from wexin_pay.wxlib_v3 import build_pay_prepayid_form


@app.route('/wxpay/authorize/notify', methods=['POST'])
def auth_notify():
    logger.info('[WEIXIN] payment notify.... request args=%s, data=%s' % (str(request.args), str(request.data)))
    request_data = xml_to_dict(request.data)
    verify_result = verify_notify(request_data)
    if not verify_result:
        logger.error('[WEIXIN] notify delivery verify failed!')
        return 'verify result failed', 400

    out_trade_no = request_data['out_trade_no']
    total_fee = request_data['total_fee']
    logger.info('[WEIXIN] Wechat payment verify succeeded! order[%s] fee[%s]' % (out_trade_no, total_fee))

    if request_data['result_code'] == "SUCCESS":
        order = Order.query.filter_by(order_id=out_trade_no).first()
        if not order:
            logger.error('order[%s] not exist' % out_trade_no)
            return "order[%s] not exist" % out_trade_no, 400
        order.to_pay(2)
        db.session.add(order)
        db.session.commit()
        logger.info('[WEIXIN] order[%s] pay confirmed!' % out_trade_no)
        args = order.get_order_params()
        signal_order_notify.send(current_app._get_current_object(), args=args, status='pay-confirm')  # notify
        return "success"
    else:
        logger.error(
            '[WEIXIN] wechat delivery notify failed:(%s):%s' % (request_data['err_code'], request_data['err_code_des']))
        return 'delivery notify failed!', 400


def payable(request, openid, order):
    logger.info('[WEIXIN] payable....')
    parameter = {
        'body': '噼啪支付-电子卡包',
        'out_trade_no': order.order_id,
        'spbill_create_ip': request.remote_addr,
        'total_fee': int(order.pay_amount * 100),  # unit is fen check other day
        'notify_url': 'http://%s/wxpay/authorize/notify' % request.host,  # 'pipapay.ngrok.cc', #TODO
        'openid': openid  # 'o80wpvwh6C59IZ7W7EMv9_hu5BW8' # openid #TODO
    }
    return build_pay_prepayid_form(parameter)


# 告警接口
@app.route('/wxpay/alarm/alarm', methods=['POST'])
def warning_notify():
    logger.info('[WEIXIN] request.args=%s, request.data=%s' % (str(request.args), str(request.data)))
    raw_str = str(request.data)
    wechat_data = xml_to_dict(raw_str)
    parameters = {key.lower(): wechat_data[key] for key in wechat_data}
    if build_warning_sign(parameters) == wechat_data['AppSignature']:
        return 'success'
    else:
        logger.error('[WEIXIN] Wechat Warning Notify Verify Failed!')
        return 'error'


@app.route('/wxpay/alarm/notify', methods=['POST'])
def right_notify():
    # raw_str = request.body
    logger.info('[WEIXIN] request.args=%s' % str(request.args))
    logger.info('[WEIXIN] request.data=%s' % str(request.data))
    raw_str = str(request.data)
    logger.info('[WEIXIN] alarm right notify: %s' % unicode(raw_str))
    wechat_data = xml_to_dict(raw_str)
    parameters = {key.lower(): wechat_data[key] for key in wechat_data}
    if build_right_sign(parameters) == wechat_data['AppSignature']:
        return 'success'
    else:
        logger.error('Wechat Right Notify Verify Failed!')
        return 'error'


def get_address_data(request):
    params = {'accesstoken': request.QUERY_PARAMS.get('accesstoken'), 'url': request.META['HTTP_HOST'] + request.path}
    result = get_address_sign(params)
    return result


@app.route('/wxpay/native/callback', methods=['POST'])
def native_callback():
    raw_str = str(request.data)
    logger.info('[WEIXIN] native callback Request: %s' % unicode(raw_str))
    # params = xml_to_dict(raw_str)
    # service_id = params["service_id"]
    # firm_service = Service.query.filter_by(id=service_id).first()
    # if not firm_service:
    # return '<xml>' \
    #            '<return_code><![CDATA[FAIL]]></return_code>' \
    #            '<return_msg><![CDATA[Service not exist]]></return_msg>' \
    #            '</xml>'
    # parameter = {
    #     'body': firm_service.title,
    #     'out_trade_no': str(int(time.time())),
    #     'spbill_create_ip': request.remote_addr,
    #     'total_fee': str(int(firm_service.now_price * 100)),  # unit is fen check other day
    #     'notify_url': 'http://%s/wxpay/authorize/notify' % request.host,
    #     'openid': params['openid']
    # }
    # return build_static_qrcode_form(parameter)
    pass


@app.route('/wxpay/qrcode/static/create', methods=['GET', 'POST'])
def static_qrcode_create():
    if not request.args.get("service_id"):
        return 'error'
    param = {
        'appid': WEIXIN_APPID,
        'nonce_str': random_str(),
        'mch_id': WXPAY_CONIFG['mch_id'],
        'time_stamp': str(int(time.time())),
        'service_id': str(request.args["service_id"]),
    }
    sign = sign_md5(param)
    param['sign'] = sign
    info = format_param_map(param)
    text = 'weixin://wxpay/bizpayurl?%s' % info
    qrcode_txt = dict(text=text, logo='http://chexianghui-srv.qiniudn.com/ico.jpeg', w=200, m=1, el='m')
    qrcode_img = "<img src='http://qr.liantu.com/api.php?%s'/>" % urlencode(qrcode_txt)
    return qrcode_img


@app.route('/wxpay/qrcode/dynamic/create', methods=['GET', 'POST'])
def dynamic_qrcode_create():
    # if not request.args.get("service_id"):
    # return 'error: service_id not exist'
    # service_id = request.args["service_id"]
    # open_id = request.args["uid"]
    # firm_service = Service.query.filter_by(id=service_id).first()
    # if not firm_service:
    #     return 'error: service[%s] not exist' % service_id
    # parameter = {
    #     'body': firm_service.title,
    #     'out_trade_no': str(int(time.time())),
    #     'spbill_create_ip': request.remote_addr,
    #     'total_fee': str(int(firm_service.now_price * 100)),  # unit is fen check other day
    #     'notify_url': 'http://%s/wxpay/authorize/notify' % request.host,
    #     'openid': open_id
    # }
    # return build_dynamic_qrcode_form(parameter)
    pass