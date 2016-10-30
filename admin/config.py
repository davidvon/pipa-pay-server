# -*- coding: utf8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# available languages
LANGUAGES = {'zh_CN': 'Chinese'}
BABEL_DEFAULT_LOCALE = 'zh_CN'

WEIXIN_TOKEN = 'chexianghui365'
WXPAY_CONIFG = {
    'mch_id': '1220396801',
    'api_key': 'FuiNBoblzcPN9MXq6nFxRnqcwyqf81vc',
    'partnerKey': ''  # v2
}

# role must be >1
ROLE_ADMIN = 'ADMIN'
ROLE_SHOP_STAFF = 'USER_EDIT'
ROLE_SHOP_STAFF_READONLY = 'USER_READ'
ROLE_FETCH_STEWARD = 'FETCH_STEWARD'
ROLE_POST_STEWARD = 'POST_STEWARD'
ROLES = [ROLE_ADMIN, ROLE_SHOP_STAFF, ROLE_SHOP_STAFF_READONLY, ROLE_FETCH_STEWARD, ROLE_POST_STEWARD]

# Flask-security
SECRET_KEY = 'its a dog'
SQLALCHEMY_POOL_RECYCLE = 5  # Solove MySQL has gone away,Sae 30s close connection. set to 5s reconnect.
THREADS_PER_PAGE = 8
CSRF_ENABLED = True
DATABASE_QUERY_TIMEOUT = 0.5  # slow database query threshold (in seconds)

RUN_MODE = os.environ.get('PIPAPAY_RUN_MODE', 'debug')
if RUN_MODE == 'production':
    DEBUG = False
    DEFAULT_HOST_URL = 'http://pay.chexianghui.com/'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Davidvon12345@127.0.0.1:33006/pipapay'
    REDIS_SERVER_IP = '127.0.0.1'
    REDIS_SERVER_PWD = ''
    REDIS_SERVER_DB = 1
    WEIXIN_APPID = 'wxacfa25edbc32b183'
    WEIXIN_SECRET = 'c780474a8dc84887e1b55cd18ef3031d'
elif RUN_MODE == 'sandbox':
    DEBUG = True
    DEFAULT_HOST_URL = 'http://pay.chexianghui.com/'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Davidvon12345@127.0.0.1:33006/pipapay'
    REDIS_SERVER_IP = '127.0.0.1'
    REDIS_SERVER_PWD = ''
    REDIS_SERVER_DB = 1
    WEIXIN_APPID = 'wxb3ec764893b99722'
    WEIXIN_SECRET = '04a37bc738a0c2759ba850c4334b99fc'
else:
    DEBUG = True
    DEFAULT_HOST_URL = 'http://127.0.0.1/'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Davidvon12345@127.0.0.1:33006/pipapay'
    REDIS_SERVER_IP = '127.0.0.1'
    REDIS_SERVER_PWD = ''
    REDIS_SERVER_DB = 1
    WEIXIN_APPID = 'wxb3ec764893b99722'
    WEIXIN_SECRET = '04a37bc738a0c2759ba850c4334b99fc'

SQLALCHEMY_DATABASE_URI += '?unix_socket=/tmp/mysql.sock&charset=utf8'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# log
LOG_MAX_SIZE = 2 * 1024 * 1024
LOG_MAX_FILES = 4
LOG_MODE = 'a'
LOG_DIR = os.path.join(basedir, "../logs")
LOG_FILE = os.path.join(LOG_DIR, "server.log")
if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

MEDIA_TYPE_TEXT = u'1'
MEDIA_TYPE_NEWS = u'2'
MEDIA_TYPE_URL = u'3'

LIKE_MATCH = u'1'
TOTAL_MATCH = u'2'
