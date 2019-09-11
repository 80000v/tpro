#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-08-24 00:54:36
@LastEditTime: 2019-09-10 06:48:02
@Description: provide general functions for datetime
'''

import datetime
from collections import namedtuple
from functools import lru_cache

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


def get_last_date(trading_calendar, dt: datetime.datetime):
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


def convert_dt_to_time_int(dt: datetime.datetime):
    return dt.hour * 10000 + dt.minute * 100 + dt.second


def convert_int_to_time(dt: int):
    if dt > 1000000:
        dt %= 1000000
    hour, r = divmod(dt, 10000)
    minute, second = divmod(r, 100)
    return datetime.time(hour=hour, minute=minute, second=second)


@lru_cache()
def _convert_int_to_date(dt: int):
    year, r = divmod(dt, 10000)
    month, day = divmod(r, 100)
    return datetime.datetime(year, month, day)


@lru_cache()
def convert_int_to_datetime(dt: int):
    year, r = divmod(dt, 10000000000)
    month, r = divmod(r, 100000000)
    day, r = divmod(r, 1000000)
    hour, r = divmod(r, 10000)
    minute, second = divmod(r, 100)
    return datetime.datetime(year, month, day, hour, minute, second)


def convert_ms_int_to_datetime(dt: int):
    dt, ms = divmod(dt, 1000)
    return convert_int_to_datetime(dt).replace(microsecond=ms * 1000)


def convert_date_time_ms_int_to_datetime(dt_date: int, dt_time: int):
    dt = _convert_int_to_date(dt_date)

    hours, r = divmod(dt_time, 10000000)
    minutes, r = divmod(r, 100000)
    seconds, millisecond = divmod(r, 1000)

    return dt.replace(hour=hours, minute=minutes, second=seconds, microsecond=millisecond * 1000)
