# -*- coding: utf-8 -*-
__author__ = 'fengguanhua'
import datetime as dt
from datetime import datetime


def current_collect_dates(count, offend=0):
    collect_dates = []
    today = dt.datetime.now()
    for i in range(offend, count + offend):
        next_day = today + dt.timedelta(days=i)
        week_id = int(dt.datetime.strftime(next_day, '%w'))
        week_lan = ['日', '一', '二', '三', '四', '五', '六']
        if i == 0:
            week = '今天（周' + week_lan[week_id] + '）'
        elif i == 1:
            week = '明天（周' + week_lan[week_id] + '）'
        elif i == 2:
            week = '后天（周' + week_lan[week_id] + '）'
        else:
            week = dt.datetime.strftime(next_day, '%m月%d日（周') + week_lan[week_id] + '）'
        collect_dates.append({'id': i, 'date': week})
    return collect_dates


def current_collect_time():
    collect_times = []
    for i in range(5, 10):
        collect_times.append({'id': i * 2, 'time': '%s:00-%s:00' % (i * 2, (i + 1) * 2)})
    return collect_times


def date_format(date):
    for i in range(0, 3):
        next_day = dt.datetime.now() - dt.timedelta(days=i)
        if next_day.date() == date:
            key = ['今天', '昨天', '前天']
            return key[i]
    for i in range(0, 3):
        next_day = dt.datetime.now() + dt.timedelta(days=i)
        if next_day.date() == date:
            if i < 3:
                key = ['今天', '明天', '后天']
                return key[i]
    week_id = int(dt.datetime.strftime(date, '%w'))
    week_lan = ['日', '一', '二', '三', '四', '五', '六']
    week = dt.datetime.strftime(date, '%m月%d日 周') + week_lan[week_id]
    return week


def time_range_format(time_id):
    times = current_collect_time()
    for time in times:
        if time['id'] == time_id:
            return time['time']
    return "%s:00-%s:00" % (time_id, time_id+1)
