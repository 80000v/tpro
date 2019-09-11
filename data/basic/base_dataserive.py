#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Freemoses
# @Date:   2019-07-08 07:58:42
# @Last Modified by:   Freemoses
# @Last Modified time: 2019-08-21 20:36:16
import datetime
import shelve

from time import sleep
from threading import Thread

from PyQt5 import QtCore

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from QuanTrader.utils.constants import DatabaseName
from QuanTrader.utils import load_json, get_temp_file


from .instruments_mixin import InstrumentsMixin
from .trading_dates_mixin import TradingDatesMixin


########################################################################
class BaseDataService(QtCore.QObject, InstrumentsMixin, TradingDatesMixin):
    """数据服务基础类"""

    digitSignal = QtCore.pyqtSignal(int, str)

    msgSignal = QtCore.pyqtSignal(str)

    settingFile = 'DS_setting.json'

    def __init__(self, parent=None):
        super(BaseDataService, self).__init__(parent)

        self._active = False
        self._setting = load_json(self.settingFile)

        self.thread = Thread(target=self.run)

        InstrumentsMixin.__init__(self)
        TradingDatesMixin.__init__(self)

    # ------------------------------------------------------------------
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, act):
        if isinstance(act, bool):
            self._active = act
        else:
            return
        if self._active:
            if not self.thread.is_alive():
                self.thread.setDaemon(True)
                self.thread.start()
                self.writeLog('QuantOS 数据服务已启动...')
        else:
            self.exit()

    # ------------------------------------------------------------------
    def _connect_db(self, config):
        url = 'mongodb://{}:{}'.format(config.get('HOST', '127.0.0.1'), config.get('PORT', 27017))

        try:
            _dbClient = MongoClient(url, serverSelectionTimeoutMS=10)
            _dbClient.server_info()
            return _dbClient
        except ConnectionFailure:
            return None

    # ------------------------------------------------------------------
    def load_updated_date(self):
        """从硬盘读取最后的更新日期"""
        f = shelve.open(get_temp_file('temporary.qt'))
        return f['last_updated'] if 'last_updated' in f else datetime.date(1990, 12, 19)

    # ------------------------------------------------------------------
    def save_updated_date(self, updated_date):
        """保存最后的更新日期到硬盘"""
        f = shelve.open(get_temp_file('temporary.qt'))
        f['last_updated'] = updated_date
        f.close()

    # ------------------------------------------------------------------
    def writeLog(self, msg):
        """记录日志"""
        self.msgSignal.emit(msg)

    # ------------------------------------------------------------------
    def writeRate(self, rate=0, total=1, symbol=''):
        """记录当前更新进度"""
        self.digitSignal.emit(100 * rate // total, symbol)

    # ------------------------------------------------------------------
    def exit(self):
        self._active = False
        if self.thread.is_alive():
            self.thread.join(timeout=10)
        self.writeLog('数据服务已停止！')

    # ------------------------------------------------------------------
    def close(self):
        self.exit()

    # ------------------------------------------------------------------
    def run(self):
        waiting = 0
        last_updated = self.load_updated_date()

        while self._active:
            sleep(1)

            waiting += 1
            if waiting < 5:
                continue
            waiting = 0

            t = datetime.datetime.now()

            if t.date() != last_updated:
                last_trade_date = self.get_previous_trading_date(t)

                if last_trade_date.date() != last_updated:
                    self._to_update(last_trade_date)

                    if t.isoweekday() > 5:
                        self._to_adjust(last_trade_date)

                    last_updated = last_trade_date.date()
        return

    # ------------------------------------------------------------------
    def _to_update(self, update_date):
        _retry = 3

        while _retry > 0:
            _task = Thread(target=self._update_process, args=(update_date,))
            _task.start()

            try:
                _task.join()
                if self._active:
                    self.save_updated_date(update_date.date())
                break
            except:
                _retry -= 1

    # ------------------------------------------------------------------
    def _to_adjust(self, end_date):
        # 调整本周每日最后一分钟数据
        _db = self._connect_db(self._setting.get('MongoDB', {}))[DatabaseName.MINUTE.value]
        instrument_list = [x for x in self.get_stock_contracts() if x.type == 'CS' and x.status == 'Active']

        digit = 0
        total = len(instrument_list)

        self.writeLog('开始调整本周每日最后一分钟数据...')

        for instrument in instrument_list:
            digit += 1
            self.writeRate(digit, total, '正在调整: %s - %s' % (instrument.order_book_id, instrument.symbol))
            try:
                self.adjust_minute_bar(_db, instrument, end_date, prev_nday=10)
            except Exception as e:
                self.writeLog('调整分钟线数据时出现错误： %s ' % e)
                raise e

        self.writeLog('本周分钟线数据调整完毕！')
        self.writeRate(symbol='finish')

    # ------------------------------------------------------------------
    def _update_process(self, end_date):
        _db_client = self._connect_db(self._setting.get('MongoDB', {}))

        if _db_client is None:
            return
        else:
            daily_db = _db_client[DatabaseName.DAILY.value]
            minute_db = _db_client[DatabaseName.MINUTE.value]
            factor_db = _db_client[DatabaseName.FACTOR.value]

        self.writeLog('开始更新 %s 数据...' % end_date.date())

        digit = 0

        instrument_list = self.get_stock_contracts()
        total = len(instrument_list)

        for instrument in instrument_list:
            if not self._active:
                return

            if instrument.de_listed_date < end_date or (instrument.type == 'CS' and instrument.status != 'Active'):
                digit += 1
                self.writeRate(digit, total, '正在更新: %s - %s' % (instrument.order_book_id, instrument.symbol))
                continue

            # _date = min(end_date, instrument.de_listed_date)

            try:
                digit += 1
                self.writeRate(digit, total, '正在更新: %s - %s' % (instrument.order_book_id, instrument.symbol))

                self.update_day_bar(daily_db, instrument, end_date)
                self.update_minute_bar(minute_db, instrument, end_date)
                if instrument.type == 'CS':
                    self.update_daily_factor(factor_db, instrument, end_date)
                    self.adjust_minute_bar(minute_db, instrument, end_date, prev_nday=1)
            except Exception as e:
                self.writeLog('更新 【 %s -- %s 】 数据时出现错误： %s' % (instrument.order_book_id, instrument.symbol, e))

        _db_client.close()
        del _db_client

        self.writeLog('数据更新完毕!')
        self.writeRate(symbol='finish')

        return

    # ------------------------------------------------------------------
    def update_day_bar(self, db, instrument, end_date):
        """
         更新指定合约日线数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期

         :return: bool: 是否活跃合约
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    def update_minute_bar(self, db, instrument, end_date):
        """
         更新指定合约分钟线数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    def update_daily_factor(self, db, instrument, end_date):
        """
         更新指定合约每日因子数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期
        """
        raise NotImplementedError

    # ------------------------------------------------------------------
    def adjust_minute_bar(self, db, instrument, end_date, prev_nday=5):
        """
         调整指定合约分钟线数据

         :param pymongo.database.Database db: Mongo数据库
         :param Instrument instrument: 合约对象
         :param datetime.datetime end_date: 更新日期
         :param int prev_nday: 向前调整 n 日分钟线数据(默认为5天)
        """
        raise NotImplementedError
