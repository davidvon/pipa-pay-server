# -*- coding: utf-8 -*-
from threading import Thread
from datetime import datetime
import time, os
from random import Random
import datetime as dt
from flask.ext.login import current_user
__author__ = 'fengguanhua'


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def date_random_str(random_len=4):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    now = time.strftime('%Y%m%d%H%M%S')
    for i in range(random_len):
        str += chars[random.randint(0, length)]
    return '%s%s' % (now, str)


def random_digit(random_len=6):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_len):
        str += chars[random.randint(0, length)]
    return str


def resize_img(img_path, out_path, new_width):
    try:
        import Image

        im = Image.open(img_path)
        width, height = im.size
        ratio = 1.0 * height / width
        new_height = int(new_width * ratio)
        new_size = (new_width, new_height)
        out = im.resize(new_size, Image.ANTIALIAS)
        out.save(out_path)
    except:
        pass


def delete_file(file):
    try:
        os.remove(file)
    except OSError:
        pass


def date_diff_format(date):
    if not date: return ''
    now = dt.date.today()
    diff = date - now
    return str(diff.days)


def date_enable(date):
    if not date: return False
    now = dt.date.today()
    diff = date - now
    return diff.days >= 0


def today_fromto():
    left = datetime.strptime(datetime.now().strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S')
    right = datetime.strptime(datetime.now().strftime('%Y-%m-%d 23:59:59'), '%Y-%m-%d %H:%M:%S')
    return left, right


def current_user_firm():
    is_admin = current_user.is_admin()
    current_user_firm = None
    if not is_admin:
        current_user_firm = current_user.firm
    return is_admin, current_user_firm


