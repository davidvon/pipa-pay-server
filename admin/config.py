# -*- coding: utf8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# available languages
LANGUAGES = {'zh_Hans_CN': 'Chinese'}
BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'

# pagination
COUNT_PER_PAGE = 20
MAX_SEARCH_RESULTS = 50

# weixin account
ISONLINE = 'ONLINE_SERVER' in os.environ
WEIXIN_APPID = 'wx67dfef61c86de4c7'
WEIXIN_SECRET = 'fbc9eaf0ac4cf7a4f4d2947e5a882b8f'
WEIXIN_TOKEN = 'neighbour_laundry'
WXPAY_CONIFG = {
    'partnerId': '1232854202',
    'partnerKey': '966605',
    'apiKey':'polycn600048poly600048poly600048'
}

IS_ONLINE = 'ONLINE_SERVER' in os.environ
DEBUG = not IS_ONLINE
UNITTEST = True if 'TEST' in os.environ else False

if IS_ONLINE:
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:bilin123@127.0.0.1/laundry?unix_socket=/tmp/mysql.sock&charset=utf8'
else:
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Davidvon12345@127.0.0.1/laundry?unix_socket=/tmp/mysql.sock&charset=utf8'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# log
LOG_MAX_SIZE = 2 * 1024 * 1024
LOG_MAX_FILES = 4
LOG_MODE = 'a'
LOG_DIR = os.path.join(basedir, "../logs")
LOG_FILE = os.path.join(LOG_DIR, "server.log")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)


POS_PLAT_SERVER_IP = "192.168.200.105"
POS_PLAT_SERVER_PORT = 8583

DEFAULT_HOST_URL = 'http://123.57.205.55/'


