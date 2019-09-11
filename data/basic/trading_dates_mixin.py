#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Freemoses
# @Date:   2019-07-06 21:03:49
# @Last Modified by:   freem
# @Last Modified time: 2019-07-08 07:52:26
import os
import datetime
import pandas as pd
from functools import lru_cache

from rqalpha.data.trading_dates_store import TradingDatesStore


def _to_timestamp(d):
    if isinstance(d, int):
        d = str(d)
    return pd.Timestamp(d).replace(hour=0, minute=0, second=0, microsecond=0)


def _p(name):
    return os.path.join(os.path.expanduser("~/.rqalpha"), "bundle", name)


class TradingDatesMixin(object):
    """docstring for TradingDatesMixin"""
    def __init__(self):
        self._dates = TradingDatesStore(_p('trading_dates.bcolz')).get_trading_calendar()

    def get_trading_dates(self, start_date, end_date):
        # 只需要date部分
        start_date = _to_timestamp(start_date)
        end_date = _to_timestamp(end_date)
        left = self._dates.searchsorted(start_date)
        right = self._dates.searchsorted(end_date, side='right')
        return self._dates[left:right]

    def get_previous_trading_date(self, date, n=1):
        date = _to_timestamp(date)
        pos = self._dates.searchsorted(date)
        if pos >= n:
            return self._dates[pos - n]
        else:
            return self._dates[0]

    def get_next_trading_date(self, date, n=1):
        date = _to_timestamp(date)
        pos = self._dates.searchsorted(date, side='right')
        if pos + n > len(self._dates):
            return self._dates[-1]
        else:
            return self._dates[pos + n - 1]

    def is_trading_date(self, date):
        date = _to_timestamp(date)
        pos = self._dates.searchsorted(date)
        return pos < len(self._dates) and self._dates[pos] == date
