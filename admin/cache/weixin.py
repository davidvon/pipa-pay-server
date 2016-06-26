__author__ = 'fengguanhua'

from app import redis_client


def cache_access_token(token, expires_in):
    redis_client.set('WX_ACCESS_TOKEN', token, expires_in-100)


def access_token_from_cache():
    val = redis_client.get('WX_ACCESS_TOKEN')
    return val



