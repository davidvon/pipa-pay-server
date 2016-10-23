# -*- coding: UTF-8 -*-
from sdk import TemplateSMS

sms_account_sid = '8a48b5514e00e2d3014e045c006601bf'
sms_account_token = '3b405fd42be04e91a2ddc0f32430cf28'
sms_app_id = '8a48b5514e0b153e014e0b29bbb80016'
sms_server_ip = 'app.cloopen.com'
sms_server_port = '8883'
sms_version = '2013-12-26'
sms_template_id = "24838"
sms_valid_minutes = '3'


def send_template_sms(to, random):
    rest = TemplateSMS(sms_server_ip, sms_server_port, sms_version)
    rest.set_account(sms_account_sid, sms_account_token)
    rest.set_app_id(sms_app_id)
    result = rest.send_template_sms(to, random, sms_valid_minutes, sms_template_id)
    return True if int(result['statusCode']) == 0 else False


def get_account_info():
    rest = TemplateSMS(sms_server_ip, sms_server_port, sms_version)
    rest.set_account(sms_account_sid, sms_account_token)
    rest.set_app_id(sms_app_id)
    result = rest.query_account_info()
    return result

    # get_account_info()
    # send_template_sms('18651816350', '135849')