# -*- coding: UTF-8 -*-
import hashlib
import base64
import datetime
import urllib2
import json


class TemplateSMS:
    account_sid = ''
    account_token = ''
    app_id = ''
    server_ip = ''
    server_port = ''
    soft_version = ''
    timestamp = ''

    def set_account(self, account_sid, token):
        self.account_sid = account_sid
        self.account_token = token

    def __init__(self, ip, port, version):
        self.server_ip = ip
        self.server_port = port
        self.soft_version = version

    def set_app_id(self, app_id):
        self.app_id = app_id

    def send_template_sms(self, to, random, valid_min, temp_id):
        now_date = datetime.datetime.now()
        self.timestamp = now_date.strftime("%Y%m%d%H%M%S")
        signature = self.account_sid + self.account_token + self.timestamp
        sig = hashlib.md5()
        sig.update(signature)
        sig = sig.hexdigest().upper()
        url = "https://" + self.server_ip + ":" + self.server_port + "/" + self.soft_version + "/Accounts/" + \
              self.account_sid + "/SMS/TemplateSMS?sig=" + sig
        src = self.account_sid + ":" + self.timestamp
        req = urllib2.Request(url)
        b = '["%s","%s"]' % (random, valid_min)
        body = '''{"to": "%s", "datas": %s, "templateId": "%s", "appId": "%s"}''' % (to, b, temp_id, self.app_id)
        req.add_data(body)
        auth = base64.encodestring(src).strip()
        req.add_header("Authorization", auth)
        req.add_header("Accept", 'application/json;')
        req.add_header("Content-Type", "application/json;charset=utf-8;")
        req.add_header("Host", "127.0.0.1")
        req.add_header("content-length", len(body))
        try:
            res = urllib2.urlopen(req)
            data = res.read()
            res.close()
            locations = json.loads(data)
            return locations
        except:
            return {'172001': 'network error'}

    def query_account_info(self):
        now_date = datetime.datetime.now()
        self.timestamp = now_date.strftime("%Y%m%d%H%M%S")
        signature = self.account_sid + self.account_token + self.timestamp
        sig = hashlib.md5()
        sig.update(signature)
        sig = sig.hexdigest().upper()
        url = "https://" + self.server_ip + ":" + self.server_port + "/" + self.soft_version + "/Accounts/" + \
              self.account_sid + "/AccountInfo?sig=" + sig
        src = self.account_sid + ":" + self.timestamp
        auth = base64.encodestring(src).strip()
        req = urllib2.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/jsoncharset=utf-8")
        req.add_header("Authorization", auth)
        try:
            res = urllib2.urlopen(req)
            data = res.read()
            res.close()
            locations = json.loads(data)
            return locations
        except:
            return {"statusCode": '172001'}
