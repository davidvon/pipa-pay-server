__author__ = 'fengguanhua'

from app import redis_client
from json import JSONEncoder, JSONDecoder


def cache_access_token(token, expires_in):
    redis_client.set('assess_token', token, expires_in)


def get_cache_access_token():
    return redis_client.get('assess_token')


def cache_ticket(type, token, expires_in):
    redis_client.set('%s_ticket' % type, token, expires_in)


def get_cache_ticket(type):
    return redis_client.get('%s_ticket' % type)


def push_cache_card_id(card_id, openid, card_unique_id):
    val = redis_client.get('%s_%s_card' % (card_id, openid))
    tmp = JSONDecoder().decode(val) if val else []
    tmp.append(card_unique_id)
    val = JSONEncoder().encode(tmp)
    redis_client.set('%s_%s_card' % (card_id, openid), val, 120)


def pop_cache_card_id(card_id, openid):
    val = redis_client.get('%s_%s_card' % (card_id, openid))
    if not val:
        return None
    tmp = JSONDecoder().decode(val)
    if len(tmp) == 0:
        return None
    gid = tmp.pop()
    val = JSONEncoder().encode(tmp)
    redis_client.set('%s_%s_card' % (card_id, openid), val, 120)
    return gid


def cache_code_openid(card_id, openid):
    redis_client.set(card_id, openid, 30)


def get_cache_code_openid(card_id):
    return redis_client.get(card_id)


def cache_customer_cards(openid, cards):
    val = JSONEncoder().encode(cards)
    redis_client.set(openid+'_cards', val, 60)


def get_cache_customer_cards(open_id):
    val = redis_client.get(open_id+'_cards')
    if not val:
        return None
    cards = JSONDecoder().decode(val)
    return cards

