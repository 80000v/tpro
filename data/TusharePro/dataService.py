#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Tushare Pro 数据接口，提供全市场数据服务
"""
import os
import datetime
import pandas as pd

from time import sleep
from threading import Thread
from collections import OrderedDict

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

import tushare as ts

from rqalpha.data.date_set import DateSet
from rqalpha.data.instrument_store import InstrumentStore
from rqalpha.model.instrument import Instrument

from PyQt5 import QtCore

from utils.common_func import loadJsonSetting
from utils.datetime_func import convert_dt_to_date_int, convert_int_to_date, convert_int_to_datetime
from utils.constant import DATABASE_NAME


suffixMap = {
    "XSHE": "SZ",
    "XSHG": "SH",
    "CFFEX": "CFE",
    "CZCE": "CZC",
    "DCE": "DCE",
    "SHFE": "SHF",
    "SGEX": "SGE"
}
suffixMapReverse = {v: k for k, v in suffixMap.items()}


def trans_suffix(contract):
    """转换交易所编码后缀"""
    if isinstance(contract, Instrument):
        if contract.type in ('CS', 'INDX'):
            code, suffix = contract.order_book_id.split('.')
            return '.'.join([code, suffixMap[suffix]])
        elif contract.type == 'Future':
            return '.'.join([contract.order_book_id.lower(), suffixMap[contract.exchange]])
        else:
            return contract.order_book_id

    code, suffix = contract.split('.')
    if suffix in ('SH', 'SZ'):
        return '.'.join([code, suffixMapReverse[suffix]])
    else:
        return code.upper()


########################################################################
class TProService(QtCore.QObject):
    """tushare数据下载服务"""

    digitSignal = QtCore.pyqtSignal(str)

    msgSignal = QtCore.pyqtSignal(str)

    settingFile = 'DS_setting.json'

    # ------------------------------------------------------------------
    def __init__(self, parent=None):
        super(TProService, self).__init__(parent)
        self._api = None                        # 数据接口
        self._dbClient = None                   # MongoDB接口
        self._active = False                    # 运行状态

        self.thread = Thread(target=self.run)

        def _p(name):
            return os.path.join(os.path.expanduser("~/.rqalpha"), "bundle", name)

        # 合约列表
        self._instruments = [x for x in InstrumentStore(_p('instruments.pk')).get_all_instruments() if x.type in ('CS', 'INDX') and x.exchange in ('XSHE', 'XSHG')]
        self._total_of_instrument = len(self._instruments)

        # 交易日历
        try:
            self._trading_calendar = pd.read_csv('etc/calendar.csv').trade_date
        except Exception:
            self._trading_calendar = None

        # 股票ST信息
        self._st_stock_days = DateSet(_p('st_stock_days.bcolz'))

        # 股票停牌信息
        self._suspend_days = DateSet(_p('suspended_days.bcolz'))

    # ------------------------------------------------------------------
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, act):
        if isinstance(act, bool):
            self._active = act

    # ------------------------------------------------------------------
    def prevTradeDay(self, date):
        """取得前一交易日期"""
        if self._calendar is not None:
            index = self._calendar[self._calendar == int(date)].index.values[0]
            return self._calendar.iloc[index - 1]

    # ------------------------------------------------------------------
    def nextTradeDay(self, date):
        """取得下一交易日期"""
        if self._calendar is not None:
            index = self._calendar[self._calendar == int(date)].index.values[0]
            return self._calendar.iloc[index + 1]

    # ------------------------------------------------------------------
    def isTrade(self, date):
        """是否是交易日"""
        traded = True if int(date) in self._calendar.values else False
        return traded

    # ------------------------------------------------------------------
    def isST(self, vtSymbol, date):
        """
        检查指定股票的指定日期是否是ST股
        param - "date"： 20000101
        """
        df = self.__st.get(vtSymbol, None)

        if df is None:
            if self._api:
                df = self._api.namechange(ts_code=vtSymbol, fields='name,start_date,end_date')

                if df is None or df.empty:
                    return False
                else:
                    df = df[df.name.apply(lambda x: True if 'ST' in x else False)]
                    self.__st[vtSymbol] = df
            else:
                return False

        for _, row in df.iterrows():
            if row.start_date <= date < row.end_date:
                return True
        return False

    # ------------------------------------------------------------------
    def isSuspend(self, vtSymbol, date):
        """
        合约指定日期是否停牌
        param - "date"： 20000101
        """
        if self._api:
            df = self._api.suspend(ts_code=vtSymbol, suspend=date)

            if df is None or df.empty:
                return False
            else:
                return True
        return False

    # ------------------------------------------------------------------
    def connect(self):
        """连接"""
        if not self._active:
            setting = loadJsonSetting(self.settingFile)

            dbInfo = setting['MongoDB']
            apiInfo = setting['tushare']

            n1 = self.__dbConnect(dbInfo)
            n2 = self.__apiConnect(apiInfo)

            if n1 and n2:
                self._active = True
            else:
                self.writeLog('tushare 数据服务未启动，当前状态：  数据库连接：{0}，数据源连接：{1}'.format(n1, n2))
                return

        self.writeLog('tushare 数据更新服务已启动')

        self.thread.start()

    # ------------------------------------------------------------------
    def __dbConnect(self, config):
        """连接数据库"""
        if config:
            host = config.get('HOST', '')
            port = config.get('PORT', '')
        else:
            self.writeLog('MongoDB 数据库参数读取错误，请检查')
            return False

        try:
            self._dbClient = MongoClient(host, port, serverSelectionTimeoutMS=10)
            self._dbClient.server_info()
            return True
        except ConnectionFailure:
            self._dbClient = None
            return False

    # ------------------------------------------------------------------
    def __apiConnect(self, config):
        """连接数据源"""
        if config:
            token = config.get('TOKEN', None)
        else:
            self.writeLog('tushare 连接参数读取错误，请检查')
            return False

        if token:
            # 设置tushare数据令牌
            ts.set_token(token)
            try:
                self._api = ts.pro_api()

                # 构建合约信息字典
                stock_df = self._api.stock_basic(exchange='', list_status='L',
                                                 fields='ts_code,symbol,name,exchange,list_status,list_date,delist_date')

                if stock_df is None or stock_df.empty:
                    self.writeLog('未取得可交易的合约信息，请检查参数设置及网络连接状态')
                    self._api = None
                    return False

                stock_df.set_index('ts_code', inplace=True)
                self._contractDict = stock_df.T.to_dict()

                # 构建指数信息字典
                index_SSE_zh = self._api.index_basic(market='SSE', category='综合指数', fields='ts_code,name,market,category,list_date,desc')
                index_SSE_gm = self._api.index_basic(market='SSE', category='规模指数', fields='ts_code,name,market,category,list_date,desc')
                index_SZSE_zh = self._api.index_basic(market='SZSE', category='综合指数', fields='ts_code,name,market,category,list_date,desc')
                index_SZSE_gm = self._api.index_basic(market='SZSE', category='规模指数', fields='ts_code,name,market,category,list_date,desc')

                df = pd.concat([index_SSE_zh, index_SSE_gm, index_SZSE_zh, index_SZSE_gm], ignore_index=True)
                df.set_index('ts_code', inplace=True)

                self._indexDict = df.T.to_dict()

                # 构建交易日历
                try:
                    self._calendar = pd.read_csv('etc/calendar.csv').trade_date
                except Exception:
                    cal = self.tradeCalendar()
                    if cal is None:
                        self.writeLog('获取交易日历失败，请检查')
                        return False
                    else:
                        self._calendar = cal
                        self._calendar.to_csv('etc/calendar.csv', header=True, index=False)
                return True
            except Exception as e:
                self.writeLog('程序错误： %s' % e)
                self._api = None
                return False
        else:
            self.writeLog('tushare 数据令牌未设置，请检查')
            return False

    # ------------------------------------------------------------------
    def tradeCalendar(self):
        """交易日历"""
        if self._api:
            df = self._api.trade_cal(exchange='SSE', fields='cal_date,is_open')

            if df is None or df.empty:
                self.writeLog('获取交易日历失败，请检查')
                return None
            else:
                df = df[df.is_open == 1]
                df.sort_values(by=['cal_date'], inplace=True)
            return df['cal_date']
        else:
            self.writeLog('tushare 数据源未连接')
            return None

    # --------------------------------------------------------------
    def update_DailyBar(self, vtSymbol, freq, ctype):
        """
        更新某一合约日、周、月K线数据
        param： "freq" - 'Daily', 'Weekly', 'Monthly'
               "ctype" - 'CS':股票、'INDX':指数、'Future':期货、'ETF'

        return： False - 更新失败、 True - 更新成功
        """
        if self._active:
            db = self._dbClient[DataBaseMap[freq]]
            cl = db[vtSymbol]

            last = cl.find_one(sort=[('datetime', DESCENDING)])

            if last:
                start = self.nextTradeDay(last['date'])
            else:
                start = '19901219'

            end = date.today() if datetime.today().time() > time(17, 0) else date.today() - timedelta(1)
            end = end.strftime('%Y%m%d')


            if start <= end:
                msg_1 = '下载 {0} 日线级更新数据，开始时间： {1}'.format(vtSymbol, start)
                msg_2 = '初次下载 {} 日线级数据，耗时可能较长，请耐心等待...'.format(vtSymbol)
                msg = msg_1 if start != '19901219' else msg_2
                self.writeLog(msg)

                if freq == '1d':
                    df = self._api.daily(ts_code=vtSymbol, start_date=start, end_date=end)
                elif freq == '1w':
                    df = self._api.weekly(ts_code=vtSymbol, start_date=start, end_date=end)
                elif freq == '1m':
                    df = self._api.monthly(ts_code=vtSymbol, start_date=start, end_date=end)
                else:
                    self.writeLog('周期参数设置错误，请检查')
                    return

                if df is None or df.empty:
                    self.writeLog('未能获取 %s 日线级更新数据' % vtSymbol)
                    return

                df.drop_duplicates(['trade_date'], keep='last', inplace=True)
                df.sort_values(by=['trade_date'], inplace=True)
                df = df.reset_index(drop=True)

                df['insttype'] = ctype

                # 更新至数据库
                cl.ensure_index([('datetime', ASCENDING)], unique=True)

                blist = []          # 暂存bar的列表

                for ix, row in df.iterrows():
                    bar = self.generateBar(row)
                    blist.append(bar)

                if blist:
                    cl.insert_many(blist)

    # --------------------------------------------------------------
    def update_MinuteBar(self, vtSymbol, freq, ctype):
        """
        更新某一合约分钟级K线数据
         param： "freq" - '5M', '30M', '60M'
                "ctype" - 'CS':股票、'INDX':指数、'Future':期货、'ETF'
        return： False - 更新失败、 True - 更新成功
        """
        if self._active:
            db = self._dbClient[DataBaseMap[freq]]
            cl = db[vtSymbol]

            last = cl.find_one(sort=[('datetime', DESCENDING)])

            if last:
                start = self.nextTradeDay(last['date'])
                start = start[:4] + '-' + start[4:6] + '-' + start[6:]
            else:
                start = '2018-01-01'

            end = date.today() if datetime.today().time() > time(17, 0) else date.today() - timedelta(1)
            end = end.strftime('%Y-%m-%d')

            msg_1 = '下载 {0} {1} 分钟更新数据，开始时间： {2}'.format(vtSymbol, freq[:-1], start)
            msg_2 = '初次下载 {} 分钟级数据，耗时可能较长，请耐心等待...'.format(vtSymbol)
            msg = msg_1 if start != '2018-01-01' else msg_2
            self.writeLog(msg)

            if start <= end:
                code, _ = vtSymbol.split('.')
                df = ts.get_hist_data(code, start=start, end=end, ktype=freq[:-1])

                if df is None or df.empty:
                    self.writeLog('未能获取 {0} {1}分钟更新数据'.format(vtSymbol, freq[:-1]))
                    return

                df.sort_index(inplace=True)
                df.reset_index(inplace=True)

                df['ts_code'] = vtSymbol
                df['insttype'] = ctype
                df['trade_date'], df['time'] = df.date.apply(lambda x: x.split(' '))
                df['trade_date'] = df.trade_date.apply(lambda x: x.replace('-', ''))
                df['time'] = df.time.apply(lambda x: x.replace(':', ''))
                df.rename(columns={'volume': 'vol', 'price_change': 'change', 'p_change': 'pct_chg'}, inplace=True)

                # 更新到数据库
                cl.ensure_index([('datetime', ASCENDING)], unique=True)

                blist = []          # 暂存bar的列表

                for ix, row in df.iterrows():
                    bar = self.generateBar(row)
                    blist.append(bar)

                if blist:
                    cl.insert_many(blist)

    # ------------------------------------------------------------------
    def update_DailyBasis(self, vtSymbol):
        """更新某一合约基本面因子数据"""
        if self._active:
            db = self._dbClient[FACTOR_DB_NAME]
            cl = db[vtSymbol]

            last = cl.find_one(sort=[('date', DESCENDING)])

            if last:
                start = self.nextTradeDay(last['date'])
            else:
                start = ''

            end = date.today() if datetime.today().time() > time(17, 0) else date.today() - timedelta(1)
            end = end.strftime('%Y%m%d')

            msg_1 = '下载 {0} 基本面因子更新数据，开始时间： {1}'.format(vtSymbol, start)
            msg_2 = '初次下载 {} 基本面因子数据，耗时可能较长，请耐心等待...'.format(vtSymbol)
            msg = msg_1 if start else msg_2
            self.writeLog(msg)

            if start <= end:
                df = self._api.daily_basic(ts_code=vtSymbol, start_date=start, end_date=end)
                af = self._api.adj_factor(ts_code=vtSymbol, start_date=start, end_date=end)

                if df.empty or af.empty:
                    self.writeLog('未能获取 %s 基本面因子更新数据' % vtSymbol)
                    return

                del af['ts_code']

                df = pd.merge(df, af, how='right', on='trade_date')

                df.sort_values(by=['trade_date'], inplace=True)

                # 更新至数据库
                cl.ensure_index([('date', ASCENDING)], unique=True)

                blist = []          # 暂存bar的列表

                for ix, row in df.iterrows():
                    bar = self.generateBasis(row)
                    blist.append(bar)

                if blist:
                    cl.insert_many(blist)

    # ------------------------------------------------------------------
    def generateBar(self, row):
        """生成数据k线"""
        bar = OrderedDict()
        bar['vtSymbol'] = row.ts_code
        bar['date'] = row.trade_date
        bar['time'] = row.get(time, '000000').rjust(6, '0')

        bar['open'] = row.open
        bar['high'] = row.high
        bar['low'] = row.low
        bar['close'] = row.close

        bar['change'] = row.change
        bar['pct_chg'] = row.pct_chg

        bar['volume'] = row.vol * 100
        bar['turnover'] = row.get('amount', 0) * 1000

        bar['datetime'] = datetime.strptime(' '.join([bar['date'], bar['time']]), '%Y%m%d %H%M%S')

        bar['status'] = row.get('trade_status', '')
        bar['insttype'] = row.insttype
        bar['gatewayName'] = self.dataSource

        return bar

    # ------------------------------------------------------------------
    def generateBasis(self, row):
        """生成基本面记录"""
        bar = OrderedDict()

        bar['vtSymbol'] = row.ts_code
        bar['date'] = row.trade_date

        bar['close'] = row.close                        # 收盘价
        bar['adj_factor'] = row.adj_factor              # 复权因子
        bar['turnover_rate'] = row.turnover_rate        # 换手率
        bar['pe'] = row.pe                              # 市盈率(总市值/净利润)
        bar['pe_ttm'] = row.pe_ttm                      # 市盈率(TTM)
        bar['pb'] = row.pb                              # 市净率(总市值/净资产)
        bar['ps'] = row.ps                              # 市销率
        bar['ps_ttm'] = row.ps_ttm                      # 市销率(TTM)
        bar['total_share'] = row.total_share            # 总股本(万)
        bar['float_share'] = row.float_share            # 流通股本(万)
        bar['total_mv'] = row.total_mv                  # 总市值(万元)
        bar['float_mv'] = row.circ_mv                   # 流通市值(万元)

        bar['gatewayName'] = self.dataSource

        return bar

    # ------------------------------------------------------------------
    def run(self):
        """运行"""
        count = 0
        completedDate = None
        taskTime = time(17, 6)

        while self._active:
            sleep(1)

            count += 1
            if count < 10:
                continue
            count = 0

            t = datetime.now()

            digit = 0

            # 每日到达任务执行时间后，执行数据更新的操作
            if int(t.date().strftime('%Y%m%d')) in self._calendar.values:
                if t.time() > taskTime and t.date() != completedDate:
                    for symbol in self._contractDict.keys():
                        self.update_DailyBar(symbol, '1d', 'CS')
                        self.update_DailyBasis(symbol)
                        digit += 1
                        self.writeRate(digit)

                    for symbol in self._indexDict.keys():
                        self.update_DailyBar(symbol, '1d', 'INDX')
                        digit += 1
                        self.writeRate(digit)

                    completedDate = t.date()
                    self.writeLog('今日数据更新完毕！')
                    self.writeRate('finish')
                else:
                    self.writeLog('当前时间 %s，任务定时 %s' % (t, taskTime))
            else:
                self.writeLog('非交易日，不执行更新')

        self.writeLog('tushare 数据更新服务已退出')

    # ------------------------------------------------------------------
    def writeLog(self, msg):
        """记录日志"""
        self.msgSignal.emit(msg)

    # ------------------------------------------------------------------
    def writeRate(self, rate):
        """记录当前更新进度"""
        if isinstance(rate, str):
            self.digitSignal.emit(rate)
        else:
            self.digitSignal.emit('%d/%d' %(rate, self.stock_total))

    # ------------------------------------------------------------------
    def close(self):
        """关闭"""
        self._active = False

        if self._dbClient:
            self._dbClient.close()

        if self.thread.isAlive():
            self.thread.join()

    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    @property
    def contractDict(self):
        """合约信息字典"""
        return self._contractDict

    @property
    def contractList(self):
        """合约代码列表"""
        return list(self._contractDict.keys())

    @property
    def indexDict(self):
        """指数信息字典"""
        return self._indexDict

    @property
    def indexList(self):
        """指数代码列表"""
        return list(self._indexDict.keys())

    @property
    def calendar(self):
        """交易日历"""
        return self._calendar

    @property
    def online(self):
        """当前连接状态"""
        return self._online

    # ------------------------------------------------------------------
    def getContract(self, vtSymbol):
        """获取某一合约的详细信息"""
        return self._contractDict.get(vtSymbol, None)

    # ------------------------------------------------------------------
    def getIndex(self, vtSymbol):
        """获得某一指数的详细信息"""
        return self._indexDict.get(vtSymbol, None)

    # ------------------------------------------------------------------
    def getNameChange(self, vtSymbol):
        """获取某一合约的历史名称变更记录"""
        if self._online:
            df = self._api.namechange(ts_code=vtSymbol, fields='ts_code,name,start_date,end_date,change_reason')
            df.sort_values(by=['start_date'], inplace=True)
            return df
