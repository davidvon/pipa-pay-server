from json import JSONEncoder, JSONDecoder
from config import DEFAULT_HOST_URL

__author__ = 'fengguanhua'
from app import redis_client


def cache_url(hosturl):
    url = redis_client.get('HOST_URL')
    if not url:
        redis_client.set('HOST_URL', hosturl)
    return hosturl


def url_from_cache():
    url = redis_client.get('HOST_URL')
    if not url: url = DEFAULT_HOST_URL
    return url


def oauth_code_cache(code):
    key = str('OAUTH_' + code)
    val = redis_client.get(key)
    if not val:
        redis_client.set(key, code, 10)
        return False
    else:
        return True


def cache_phone_auth_code(phone, random, timeout):
    key = '%scode' % phone
    redis_client.set(key, random, timeout)


def phone_auth_code_from_cache(phone):
    key = '%scode' % phone
    return redis_client.get(key)


def cache_home_info(args):
    key = 'home_info'
    data = JSONEncoder().encode(args)
    redis_client.set(key, data, 3*60)


def home_info_cache():
    key = 'home_info'
    val = redis_client.get(key)
    if val:
        data = JSONDecoder().decode(val)
    else:
        data = None
    return data

def home_order_messages_cache():
    key = 'home_order_messages'
    val = redis_client.get(key)
    if val:
        data = JSONDecoder().decode(val)
    else:
        data = None
    return data