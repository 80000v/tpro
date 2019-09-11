#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Freemoses
# @Date:   2019-07-08 08:37:15
# @Last Modified by:   freem
# @Last Modified time: 2019-07-20 11:06:18
import os
import re
import six

from rqalpha.data.date_set import DateSet
from rqalpha.data.instrument_store import InstrumentStore


IGNORE_INDEX = ('000023.XSHG', '000140.XSHG', '000188.XSHG', '000801.XSHG', '000803.XSHG',
                '000804.XSHG', '000806.XSHG', '000807.XSHG', '000809.XSHG', '000810.XSHG',
                '000811.XSHG', '000812.XSHG', '000813.XSHG', '000815.XSHG', '000816.XSHG',
                '000817.XSHG', '000818.XSHG', '000820.XSHG', '000821.XSHG', '000822.XSHG',
                '000824.XSHG', '000825.XSHG', '000826.XSHG', '000829.XSHG', '000830.XSHG',
                '000831.XSHG', '000832.XSHG', '000833.XSHG', '000834.XSHG', '000835.XSHG',
                '000836.XSHG', '000837.XSHG', '000838.XSHG', '000839.XSHG', '000840.XSHG',
                '000843.XSHG', '000844.XSHG', '000845.XSHG', '000846.XSHG', '000850.XSHG',
                '000859.XSHG', '000861.XSHG', '000902.XSHG', '000907.XSHG', '000908.XSHG',
                '000909.XSHG', '000910.XSHG', '000911.XSHG', '000912.XSHG', '000915.XSHG',
                '000916.XSHG', '000917.XSHG', '000919.XSHG', '000920.XSHG', '000921.XSHG',
                '000922.XSHG', '000923.XSHG', '000924.XSHG', '000925.XSHG', '000926.XSHG',
                '000927.XSHG', '000929.XSHG', '000930.XSHG', '000931.XSHG', '000936.XSHG',
                '000937.XSHG', '000938.XSHG', '000939.XSHG', '000940.XSHG', '000941.XSHG',
                '000942.XSHG', '000943.XSHG', '000945.XSHG', '000946.XSHG', '000947.XSHG',
                '000948.XSHG', '000949.XSHG', '000950.XSHG', '000951.XSHG', '000952.XSHG',
                '000953.XSHG', '000954.XSHG', '000955.XSHG', '000956.XSHG', '000957.XSHG',
                '000959.XSHG', '000960.XSHG', '000961.XSHG', '000962.XSHG', '000963.XSHG',
                '000964.XSHG', '000965.XSHG', '000967.XSHG', '000968.XSHG', '000969.XSHG',
                '000970.XSHG', '000972.XSHG', '000973.XSHG', '000975.XSHG', '000976.XSHG',
                '000977.XSHG', '000978.XSHG', '000979.XSHG', '000980.XSHG', '000981.XSHG',
                '000983.XSHG', '000985.XSHG', '000988.XSHG', '000994.XSHG', '000995.XSHG',
                '000996.XSHG', '000997.XSHG', '000999.XSHG')


def _p(name):
    return os.path.join(os.path.expanduser("~/.rqalpha"), "bundle", name)


class InstrumentsMixin(object):
    """docstring for InstrumentsMixin"""

    def __init__(self, parent=None):
        self._instruments = {i.order_book_id: i for i in InstrumentStore(_p("instruments.pk")).get_all_instruments()}
        self._sym_id_map = {i.symbol: k for k, i in six.iteritems(self._instruments)
                            # 过滤掉 CSI300, SSE50, CSI500, SSE180
                            if not i.order_book_id.endswith('INDX')}
        # 股票ST数据
        self._st_stock_days = DateSet(_p('st_stock_days.bcolz'))

        # 股票停牌数据
        self._suspended_days = DateSet(_p('suspended_days.bcolz'))

        try:
            # FIXME
            # 沪深300 中证500 固定使用上证的
            for o in ['000300.XSHG', '000905.XSHG']:
                self._sym_id_map[self._instruments[o].symbol] = o
            # 上证180 及 上证180指数 两个symbol都指向 000010.XSHG
            self._sym_id_map[self._instruments['SSE180.INDX'].symbol] = '000010.XSHG'
        except KeyError:
            pass

    def industry(self, code):
        # 按行业获取合约代码
        return [v.order_book_id for v in self._instruments.values()
                if v.type == 'CS' and v.industry_code == code]

    def all_instruments(self, types, dt=None):
        return [i for i in self._instruments.values()
                if ((dt is None or i.listed_date.date() <= dt.date() <= i.de_listed_date.date()) and
                    (types is None or i.type in types))]

    def _instrument(self, sym_or_id):
        try:
            return self._instruments[sym_or_id]
        except KeyError:
            try:
                sym_or_id = self._sym_id_map[sym_or_id]
                return self._instruments[sym_or_id]
            except KeyError:
                return None

    def instruments(self, sym_or_ids):
        if isinstance(sym_or_ids, six.string_types):
            return self._instrument(sym_or_ids)

        return [i for i in [self._instrument(sid) for sid in sym_or_ids] if i is not None]

    def get_future_contracts(self, underlying, date):
        date = date.replace(hour=0, minute=0, second=0)
        futures = [v for o, v in six.iteritems(self._instruments)
                   if v.type == 'Future' and v.underlying_symbol == underlying and
                   not o.endswith('88') and not o.endswith('99')]
        if not futures:
            return []

        return sorted(i.order_book_id for i in futures if i.listed_date <= date <= i.de_listed_date)

    def get_stock_contracts(self):
        return [v for o, v in six.iteritems(self._instruments)
                if v.type in ['CS', 'INDX'] and v.exchange in ['XSHE', 'XSHG'] and
                re.match(r'^\d', o) and o not in IGNORE_INDEX]

    def is_suspended(self, order_book_id, dates):
        """
         根据 dates 来获取对应合约停牌的日期

         :param str order_book_id
         :param list['int' | 'np.int64' | 'np.uint64' | 'pd.Timestamp'] dates: 日期列表

         :return: list[bool]
        """
        if not isinstance(dates, list):
            dates = [dates]

        return self._suspended_days.contains(order_book_id, dates)

    def is_st_stock(self, order_book_id, dates):
        """
         根据 dates 来获取对应合约被ST处理的日期

         :param str symbol: 合约代码(Jaqs格式)
         :param list['int' | 'np.int64' | 'np.uint64' | 'pd.Timestamp'] dates: 日期列表

         :return: list['int']
        """
        if not isinstance(dates, list):
            dates = [dates]

        return self._st_stock_days.contains(order_book_id, dates)
