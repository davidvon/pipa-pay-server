from app import app
from wexin.reply import ReplyKeyWords

__author__ = 'fengguanhua'


if __name__ == '__main__':
    reply = ReplyKeyWords(None)
    reply.sender = 'oDF3iY9P32sK_5GgYiRkjsCo45bk'
    args = {'isgivebyfriend': 1,
            'friendusername': '11F3iY9P32sK_5GgYiRkjsCo4111',
            'cardid': 'pDF3iY9tv9zCGCj4jTXFOo1DxHdo',
            'usercardcode': '8888888',
            'oldusercardcode': '123456789'
            }
    reply.card_give(args)
