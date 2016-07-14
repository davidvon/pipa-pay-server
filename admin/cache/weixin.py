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


def cache_card_adding_tag(card_id, openid, card_unique_id):
    redis_client.set('%s_%s_card' % (card_id, openid), card_unique_id, 100)


def get_cache_card_adding_tag(card_id, openid):
    return redis_client.get('%s_%s_card' % (card_id, openid))


def cache_code_openid(card_id, openid):
    redis_client.set(card_id, openid, 30)


def get_cache_code_openid(card_id):
    return redis_client.get(card_id)

