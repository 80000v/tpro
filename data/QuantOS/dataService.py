#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Freemoses
# @Date:   2019-07-14 15:17:54
# @Last Modified by:   Freemoses
# @Last Modified time: 2019-08-21 21:06:29
import functools
from time import sleep
from collections import OrderedDict
import pandas as pd

from pymongo import ASCENDING, DESCENDING
from rqalpha.model.instrument import Instrument

from QuanTrader.api.jaqs import DataApi
from QuanTrader.data.basic import BaseDataService
from QuanTrader.utils.datetime_func import convert_dt_to_date_int, convert_int_to_date, convert_int_to_datetime


SUFFIX_MAP = {"XSHE": "SZ", "XSHG": "SH", "CFFEX": "CFE", "CZCE": "CZC",
              "DCE": "DCE", "SHFE": "SHF", "SGEX": "SGE"}
SUFFIX_MAP_REVERSE = {v: k for k, v in SUFFIX_MAP.items()}


def trans_suffix(instrument):
    """转换交易所编码后缀"""
    if isinstance(instrument, Instrument):
        if instrument.type in ['CS', 'INDX']:
            code, suffix = instrument.order_book_id.split('.')
            return '.'.join([code, SUFFIX_MAP[suffix]])
        elif instrument.type == 'Future':
            return '.'.join([instrument.order_book_id.lower(), SUFFIX_MAP[instrument.exchange]])
        else:
            return instrument.order_book_id

    code, suffix = instrument.split('.')
    if suffix in ['SH', 'SZ']:
        return '.'.join([code, SUFFIX_MAP_REVERSE[suffix]])
    else:
        return code.upper()


class QuantOSQueryError(Exception):
    """Error occurrs when make query from quantos."""


class DataService(BaseDataService):
    """docstring for QuantOS DataSerivice"""

    dataSource = 'QuantOS'

    def __init__(self):
        super(DataService, self).__init__()

        self._api = None

    # ------------------------------------------------------------------
    def ensure_api_login(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except:
                self.api_login(self._setting.get('QuantOS', {}))
                return func(self, *args, **kwargs)
        return wrapper

    # ------------------------------------------------------------------
    def api_login(self, config):
        server = config.get('SERVER', '')
        user = config.get('USER', '')
        token = config.get('TOKEN', '')

        _retry = 0
        while _retry <= 3:
            _retry += 1
            try:
                self._api = DataApi(server)
                r, msg = self._api.login(user, token)

                if r is None:
                    raise QuantOSQueryError('%s \nQuantOS login failed...' % msg)
                else:
                    break
            except QuantOSQueryError as e:
                self.writeLog("[QuantOS] Exception occurs when call api.login: %s" % e)
                if _retry > 3:
                    raise e
                else:
                    sleep(_retry)

    # ------------------------------------------------------------------
    @ensure_api_login
    def _get_day_bar(self, symbol, start_date, end_date):
        """下载指定合约日线数据"""
        df, msg = self._api.daily(symbol=symbol,
                                  freq='1d',
                                  start_date=str(start_date.date()),
                                  end_date=str(end_date.date()),
                                  data_format='pandas')

        if isinstance(df, pd.DataFrame) and not df.empty:
            df.drop_duplicates(['trade_date'], keep='last', inplace=True)  # 去重
            df.sort_values(by=['trade_date'], inplace=True)                # 排序
            df = df.reset_index(drop=True)                                 # 重建索引

            df['limit_up'] = df['preclose'] * 1.1
            df['limit_down'] = df['preclose'] * 0.9
            return df

        return pd.DataFrame()

    # ------------------------------------------------------------------
    @ensure_api_login
    def _get_minute_bar(self, symbol, trade_date, start_time=93000, end_time=160000, retry=5):
        """下载指定合约分钟线数据"""
        df = None
        start_time, end_time = min(start_time, 93000), max(end_time, 160000)

        while retry > 0:
            df, msg = self._api.bar(symbol=symbol,
                                    freq="1M",
                                    trade_date=str(trade_date.date()),
                                    start_time=start_time,
                                    end_time=end_time,
                                    data_format='pandas')

            if isinstance(df, pd.DataFrame) and not df.empty:
                if df.loc[df['close'] == 0].empty:
                    df.drop_duplicates(['date', 'time'], keep='last', inplace=True)  # 去重
                    df.sort_values(by=['date', 'time'], inplace=True)                # 排序
                    return df.reset_index(drop=True)                                 # 重建索引

            retry -= 1

        if df is None:
            return pd.DataFrame()
        else:
            df.drop_duplicates(['date', 'time'], keep='last', inplace=True)  # 去重
            df.sort_values(by=['date', 'time'], inplace=True)               # 排序
            return df.reset_index(drop=True)                                # 重建索引

    # ------------------------------------------------------------------
    @ensure_api_login
    def _get_daily_indicator(self, symbol, start_date, end_date):
        """下载指定合约每日指标数据"""
        df, msg = self._api.query(view="lb.secDailyIndicator",
                                  fields="trade_date,close,turnover_ratio,pe,pe_ttm,pb,ps,ps_ttm,total_share,float_share,total_mv,float_mv",
                                  filter="symbol={0}&start_date={1}&end_date={2}".format(
                                      symbol, convert_dt_to_date_int(start_date), convert_dt_to_date_int(end_date)),
                                  data_format='pandas')

        if isinstance(df, pd.DataFrame) and not df.empty:
            df.drop_duplicates(['trade_date'], keep='last', inplace=True)  # 去重
            df.sort_values(by=['trade_date'], inplace=True)               # 排序
            return df.reset_index(drop=True)                              # 重建索引

        return pd.DataFrame()

    # ------------------------------------------------------------------
    @ensure_api_login
    def _get_adjust_factor(self, symbol, start_date, end_date):
        """下载指定合约复权因子数据"""
        df, msg = self._api.query(view="jy.secAdjFactor",
                                  fields="trade_date,adjust_factor",
                                  filter="symbol={0}&start_date={1}&end_date={2}".format(
                                      symbol, convert_dt_to_date_int(start_date), convert_dt_to_date_int(end_date)),
                                  data_format='pandas')

        if isinstance(df, pd.DataFrame) and not df.empty:
            df.drop_duplicates(['trade_date'], keep='last', inplace=True)  # 去重
            df.sort_values(by=['trade_date'], inplace=True)               # 排序
            return df.reset_index(drop=True)                              # 重建索引

        return pd.DataFrame()

    # ------------------------------------------------------------------
    def update_day_bar(self, db, instrument, end_date):
        """
         更新指定合约日线数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期
        """
        if self._active:
            symbol = trans_suffix(instrument)
            cl = db[symbol]
            last_record = cl.find_one(sort=[('datetime', DESCENDING)])

            start_date = self.get_next_trading_date(last_record['datetime']) if last_record else instrument.listed_date

            if start_date <= end_date:
                datas = self._get_day_bar(symbol, start_date, end_date)

                if not datas.empty:
                    # 针对ST股票及科创板股票调整涨跌幅
                    if instrument.type == 'CS':
                        _is_st = self.is_st_stock(instrument.order_book_id, datas['trade_date'].tolist())
                        datas.loc[_is_st, 'limit_up'] = datas.loc[_is_st, 'preclose'] * 1.05
                        datas.loc[_is_st, 'limit_down'] = datas.loc[_is_st, 'preclose'] * 0.95

                        if instrument.board_type == 'KSH':
                            datas['limit_up'] = datas['preclose'] * 1.2
                            datas['limit_down'] = datas['preclose'] * 0.8

                    # 更新到数据库
                    cl.ensure_index([('datetime', ASCENDING)], unique=True)

                    _bars = []

                    for _, row in datas.iterrows():
                        bar = self._generate_day_bar(row)
                        _bars.append(bar)

                    if _bars:
                        cl.insert_many(_bars)

            if cl.count() == 0:
                cl.drop()

    # ------------------------------------------------------------------
    def update_minute_bar(self, db, instrument, end_date):
        """
         更新指定合约分钟线数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期
        """
        # TODO: 获取非停牌日期的Series，从而避免无效数据申请
        if self._active:
            symbol = trans_suffix(instrument)
            cl = db[symbol]
            last_record = cl.find_one(sort=[('datetime', DESCENDING)])

            start_date = self.get_next_trading_date(last_record['datetime']) if last_record else max(
                convert_int_to_date(20110104), instrument.listed_date)

            while start_date <= end_date and self._active:
                if self.is_trading_date(start_date) and not self.is_suspended(instrument.order_book_id, start_date)[0]:
                    datas = self._get_minute_bar(symbol, start_date)
                else:
                    start_date = self.get_next_trading_date(start_date)
                    continue

                datas = datas if datas.loc[datas['close'] ==
                                           0].empty else self._get_vaild_minute_bars(symbol, start_date, datas)

                # 更新到数据库
                cl.ensure_index([('datetime', ASCENDING)], unique=True)

                _bars = []

                for _, row in datas.iterrows():
                    bar = self._generate_minute_bar(row)
                    _bars.append(bar)

                if _bars:
                    cl.insert_many(_bars)

                start_date = self.get_next_trading_date(start_date)

            if cl.count() == 0:
                cl.drop()

    # ------------------------------------------------------------------
    def update_daily_factor(self, db, instrument, end_date):
        """
         更新指定合约每日因子数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期
        """
        if self._active and instrument.type == 'CS':
            symbol = trans_suffix(instrument)
            cl = db[symbol]
            last_record = cl.find_one(sort=[('datetime', DESCENDING)])

            start_date = self.get_next_trading_date(last_record['datetime']) if last_record else instrument.listed_date

            if start_date <= end_date:
                indicators = self._get_daily_indicator(symbol, start_date, end_date)
                adjfactors = self._get_adjust_factor(symbol, start_date, end_date)

                if indicators.empty or adjfactors.empty:
                    return

                del adjfactors['symbol']

                datas = pd.merge(indicators, adjfactors, how='right', on='trade_date')
                datas.sort_values(by=['trade_date'], inplace=True)
                datas.dropna(subset=['symbol'], inplace=True)

                # 更新到数据库
                cl.ensure_index([('datetime', ASCENDING)], unique=True)

                _bars = []          # 暂存bar的列表

                for _, row in datas.iterrows():
                    bar = self._generate_daily_factor(row)
                    _bars.append(bar)

                if _bars:
                    cl.insert_many(_bars)

            if cl.count() == 0:
                cl.drop()

    # ------------------------------------------------------------------
    def _generate_day_bar(self, row):
        bar = OrderedDict()
        bar['datetime'] = convert_int_to_date(row.trade_date)

        bar['open'] = row.open
        bar['high'] = row.high
        bar['low'] = row.low

        bar['close'] = row.close
        bar['volume'] = row.volume
        bar['total_turnover'] = row.turnover

        bar['limit_up'] = row.limit_up
        bar['limit_down'] = row.limit_down

        bar['open_interest'] = row.oi               # 【期货专用】 持仓量
        bar['settlement'] = row.settle              # 【期货专用】 结算价

        return bar

    # ------------------------------------------------------------------
    def _generate_minute_bar(self, row):
        bar = OrderedDict()
        bar['datetime'] = convert_int_to_datetime(row.trade_date * 1000000 + row.time)

        bar['open'] = row.open
        bar['high'] = row.high
        bar['low'] = row.low
        bar['close'] = row.close
        bar['volume'] = row.volume
        bar['total_turnover'] = row.turnover

        bar['open_interest'] = row.oi               # 【期货专用】 当前持仓量

        return bar

    # ------------------------------------------------------------------
    def _generate_daily_factor(self, row):
        bar = OrderedDict()
        bar['datetime'] = convert_int_to_date(row.trade_date)

        bar['close'] = row.close                        # 收盘价
        bar['turnover_rate'] = row.turnover_ratio       # 换手率
        bar['adj_factor'] = row.adjust_factor           # 复权因子
        bar['pe'] = row.pe                              # 市盈率(总市值/净利润)
        bar['pe_ttm'] = row.pe_ttm                      # 市盈率(TTM)
        bar['pb'] = row.pb                              # 市净率(总市值/净资产)
        bar['ps'] = row.ps                              # 市销率
        bar['ps_ttm'] = row.ps_ttm                      # 市销率(TTM)
        bar['total_share'] = row.total_share            # 总股本(万)
        bar['float_share'] = row.float_share            # 流通股本(万)
        bar['total_mv'] = row.total_mv                  # 总市值(万元)
        bar['float_mv'] = row.float_mv                  # 流通市值(万元)

        bar['from'] = 'QuantOS'

        return bar

    # ------------------------------------------------------------------
    def _get_vaild_minute_bars(self, symbol, trade_date, datas=None):
        """获取有效的分钟线数据"""
        df = self._get_day_bar(symbol, trade_date, trade_date)
        if datas is None:
            datas = self._get_minute_bar(symbol, trade_date)

        if df.empty or datas.empty:
            return datas

        if datas.iloc[0]['close'] == 0:
            datas.loc[0, ['open', 'high', 'low', 'close']] = df.iloc[0]['preclose']

        for row in range(1, len(datas)):
            if datas.iloc[row]['close'] == 0:
                datas.loc[row, ['open', 'high', 'low', 'close']] = datas.iloc[row - 1]['close']

        return datas

    # ------------------------------------------------------------------
    def adjust_minute_bar(self, db, instrument, end_date, prev_nday=5):
        """
         调整指定合约分钟线数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期
         :param int prev_nday: 向前调整 n 日分钟线数据(默认为5天)
        """
        # TODO: 实现超时控制功能
        def _get_last_bar(url, max_retry=10):
            _try = max_retry
            while _try > 0:
                _try -= 1
                sleep(0.1)
                try:
                    tick_bars = pd.read_excel(url)
                    if tick_bars.empty:
                        continue
                    else:
                        return tick_bars.iloc[-1]
                except:
                    if _try == 0:
                        break
                    else:
                        continue
            return pd.DataFrame()

        symbol = trans_suffix(instrument)
        cl = db[symbol]

        code, suffix = symbol.split('.')
        code = '0' + code if suffix == 'SH' else '1' + code

        while prev_nday > 0:
            prev_nday -= 1
            t_date = self.get_previous_trading_date(end_date, prev_nday).replace(hour=15)
            record = cl.find_one({'datetime': t_date})

            if record is None or record['volume'] > 0:
                continue

            url = 'http://quotes.money.163.com/cjmx/{0}/{1}/{2}.xls'.format(
                t_date.year, convert_dt_to_date_int(t_date), code)

            last_bar = _get_last_bar(url)

            if isinstance(last_bar, pd.Series) and not last_bar.empty:
                record['close'] = round(last_bar['成交价'] * 1.0, ndigits=2)
                record['high'] = max(record['high'], record['close'])
                record['low'] = min(record['low'], record['close'])
                record['volume'] = last_bar['成交量（手）'] * 100.0
                record['total_turnover'] = round(last_bar['成交额（元）'] * 1.0, ndigits=2)

                cl.update_one({'datetime': t_date}, {'$set': record})

    # ------------------------------------------------------------------
    def fix_minute_bar(self):
        """修复分钟线数据库中 收盘价为0 的无效数据"""
        _conn = self._connect_db(self._setting.get('MongoDB', {}))

        if _conn is None:
            return
        else:
            minute_db = _conn['minute_db']

        self.writeLog('开始修复分钟线数据库...')

        for symbol in sorted([x for x in minute_db.list_collection_names() if x.endswith(('SH', 'SZ'))]):
            cl = minute_db[symbol]
            invaild_datas = cl.find({'close': 0})

            if invaild_datas.count() > 0:
                print('%s: %d' % (symbol, invaild_datas.count()))
                fix_dates = set()
                cl.ensure_index([('datetime', ASCENDING)], unique=True)

                for x in invaild_datas:
                    fix_dates.add(x['datetime'].replace(hour=0, minute=0, second=0))

                for fix_date in sorted(fix_dates):
                    vaild_datas = self._get_vaild_minute_bars(symbol, fix_date)

                    for _, row in vaild_datas.iterrows():
                        bar = self._generate_minute_bar(row)
                        cl.replace_one({'datetime': bar['datetime']}, bar, True)

        self.writeLog('分钟线数据库修复完毕！')
        _conn.close()
