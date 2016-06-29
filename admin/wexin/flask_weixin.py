# coding: utf-8
"""
    flask_weixin
    ~~~~~~~~~~~~

    Weixin implementation in Flask.

    :copyright: (c) 2013 by Hsiaoming Yang.
    :license: BSD, see LICENSE for more detail.
"""
from flask import session
from helper import *
from reply import ReplyKeyWords
from flask import request

try:
    from lxml import etree
except ImportError:
    from xml.etree import cElementTree as etree
except:
    from xml.etree import ElementTree as etree


class FlaskWeixin(object):
    def __init__(self, app=None):
        self.session = session
        self.weixin_helper = WeixinHelper()
        self.weixin_reply = ReplyKeyWords(self)
        self._registry = {}


    def register(self, key, func=None):
        if func:
            self._registry[key] = func
            return
        return self.__call__(key)

    def __call__(self, key):
        """Register a reply function.

        Only available as a decorator::

            @weixin('help')
            def print_help(*args, **kwargs):
                username = kwargs.get('sender')
                sender = kwargs.get('receiver')
                return weixin.reply(
                    username, sender=sender, content='text reply'
                )
        """
        def wrapper(func):
            self._registry[key] = func

        return wrapper

    def view_func(self):
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        self.weixin_helper.check_signature(signature,timestamp, nonce)
        if request.method == 'GET':
            echostr = request.args.get('echostr')
            return echostr

        try:
            request_params = self.weixin_helper.to_json(request.data)
        except:
            return 'invalid', 400

        if request_params['msgtype']:
            self.weixin_reply.msg_request(request_params)
            return self.weixin_reply.msg_reply()

    view_func.methods = ['GET', 'POST']

