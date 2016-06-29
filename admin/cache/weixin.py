__author__ = 'fengguanhua'

from app import redis_client


def cache_access_token(token, expires_in):
    redis_client.set('assess_token', token, expires_in)


def get_cache_access_token():
    return redis_client.get('assess_token')


def cache_ticket(type, token, expires_in):
    redis_client.set('%s_ticket' % type, token, expires_in)


def get_cache_ticket(type):
    return redis_client.get('%s_ticket' % type)
