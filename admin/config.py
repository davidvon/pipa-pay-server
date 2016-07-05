# -*- coding: utf8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# available languages
LANGUAGES = {'zh_CN': 'Chinese'}
BABEL_DEFAULT_LOCALE = 'zh_CN'

# weixin account
ISONLINE = 'ONLINE_SERVER' in os.environ
WEIXIN_APPID = 'wxb3ec764893b99722'
WEIXIN_SECRET = '04a37bc738a0c2759ba850c4334b99fc'
WEIXIN_TOKEN = 'pipapay'
WXPAY_CONIFG = {
    'partnerId': '1304148101',
    'partnerKey': '',
    'apiKey': '85a3027dez49d259pipapay26fr58yJH'
}

IS_ONLINE = 'ONLINE_SERVER' in os.environ
DEBUG = not IS_ONLINE
UNITTEST = True if 'TEST' in os.environ else False

if IS_ONLINE:
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:bilin123@127.0.0.1/laundry?unix_socket=/tmp/mysql.sock&charset=utf8'
else:
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Davidvon12345@127.0.0.1/pipapay?unix_socket=/tmp/mysql.sock&charset=utf8'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# log
LOG_MAX_SIZE = 2 * 1024 * 1024
LOG_MAX_FILES = 4
LOG_MODE = 'a'
LOG_DIR = os.path.join(basedir, "../logs")
LOG_FILE = os.path.join(LOG_DIR, "server.log")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

DEFAULT_HOST_URL = 'http://127.0.0.1/'


