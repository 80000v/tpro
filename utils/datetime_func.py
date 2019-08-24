#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: freemoses
# DATE: 2019/08/24 周六
# TIME: 01:39:10

# DESCRIPTION: provide general functions for datetime

import datetime
from collections import namedtuple

from rqalpha.utils.py2 import lru_cache

TimeRange = namedtuple('TimeRange', ['start', 'end'])


def get_month_begin_time(time: datetime.datetime = None):
    if time is None:
        time = datetime.datetime.now()
    return time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_month_end_time(time: datetime.datetime = None):
    try:
        return time.replace(month=time.month + 1, day=1, hour=23, minute=59,
                            microsecond=999) - datetime.timedelta(days=1)
    except ValueError:
        return time.replace(year=time.year + 1, month=1, day=1, hour=23, minute=59,
                            microsecond=999) - datetime.timedelta(days=1)


def get_last_date(trading_calendar, dt):
    idx = trading_calendar.searchsorted(dt)
    return trading_calendar[idx - 1]


def convert_date_to_date_int(dt: datetime.datetime):
    return dt.year * 10000 + dt.month * 100 + dt.day


def convert_date_to_int(dt: datetime.datetime):
    t = convert_date_to_date_int(dt)
    return t * 1000000


def convert_dt_to_int(dt: datetime.datetime):
    t = convert_date_to_int(dt)
    t += dt.hour * 10000 + dt.minute * 100 + dt.second
    return t
