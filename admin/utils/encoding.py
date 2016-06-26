__author__ = 'fengguanhua'

def smart_unicode(s, encoding='utf-8'):
    if type(s) != unicode:
        return s.decode(encoding)
    return s


def smart_str(s, encoding='utf-8'):
    if type(s) != str:
        return s.encode(encoding)
    return s