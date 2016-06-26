from app import config
from config import WXPAY_CONIFG
from utils.encoding import smart_str, smart_unicode
import xml.etree.ElementTree as ET
import hashlib
from random import Random
import urllib2

__author__ = 'fengguanhua'


def para_filter(params):
    if params.get('sign'):
        filter_param = params
        filter_param.pop('sign')
        return filter_param
    return params


def sign_md5(params):
    keys = params.keys()
    keys.sort()
    array = []
    for key in keys:
        if not params[key] or params[key] == '':
            continue
        if key == 'sign':
            continue
        array.append("%s=%s" % (key, params[key]))
    string1 = "&".join(array)
    string_sign_temp = string1 + '&key=' + WXPAY_CONIFG['apiKey']
    m = hashlib.md5(string_sign_temp.encode('utf-8'))
    return m.hexdigest().upper()


def verify_notify(params):
    wx_sign = params['sign']
    sign = sign_md5(params)
    return wx_sign == sign


def random_str(randomlength=32):
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def xml_to_dict(raw_str):
    raw_str = smart_str(raw_str)
    raw_str = str(raw_str)
    msg = {}
    root_elem = ET.fromstring(raw_str)
    if root_elem.tag == 'xml':
        for child in root_elem:
            msg[child.tag] = smart_unicode(child.text)
            msg[child.tag] = unicode(child.text)
        return msg
    else:
        return None


def dict_to_xml(params):
    xml_elements = ["<xml>", ]
    for (k, v) in params.items():
        if str(v).isdigit():
            xml_elements.append('<%s>%s</%s>' % (k, v, k))
        else:
            xml_elements.append('<%s><![CDATA[%s]]></%s>' % (k, v, k))
    xml_elements.append('</xml>')
    return ''.join(xml_elements)


def do_post(url, data):
    req = urllib2.Request(url)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.read()


def format_param_map(param_map):
    sort_list = sorted(param_map)
    buff = []
    for k in sort_list:
        buff.append("{0}={1}".format(k, param_map[k]))
    return "&".join(buff)