#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Freemoses
# @Date:   2019-06-07 22:20:28
# @Last Modified by:   Administrator
# @Last Modified time: 2019-08-17 20:43:40
from PyQt5 import QtWidgets

from tpro.core.ui import Table, Editor, BackTester, PaperTrader, RealTrader, FundsAccount, DataManager, Configure
from tpro.utils.connect import ensure_mongo_login


HEADERS_MAP = {
    "strategy": {
        "title": "我的策略",
        # '名称','类型', '最新修改时间', '操作'
        "headers": ['name', 'type', 'last_modify_time', 'operate'],
    },
    "paper_trade": {
        "title": "模拟交易",
        # '名称', 'ID', '类型', '状态', '操作', '总权益', '可用资金', '当日盈亏', '累计收益', '开始时间', '结束时间', '原因'
        "headers": ['name', '_id', 'type', 'state', 'operate', 'total_equity', 'available_funds', 'today_income', 'total_income', 'start_time', 'end_time', 'stop_reason'],
    },
    "real_trade": {
        "title": "实盘交易",
        # '名称', 'ID', '状态', '操作', '总权益', '可用资金', '当日盈亏', '累计收益', '开始时间'
        "headers": ['trade_name', '_id', 'state', 'operate', 'total_equity', 'available_funds', 'today_income', 'total_income', 'start_time'],
    },
    "funds_account": {
        "title": "资金账户",
        # '资金账户', '经纪商', '备注', '是否启用', '连接状态', '消息', '操作'
        "headers": ['account', 'broker', 'comment', 'enabled', 'connect_state', 'message', 'operate'],
    },
    "backtest_history": {
        "title": "历史回测",
        # 'ID', '回测时间', '状态', '频率', '名称', '代码与参数', '开始时间', '结束时间', '收益', '备注', '操作'
        "headers": ['_id', 'backtest_time', 'state', 'frequency', 'name', 'code&param', 'start_time', 'end_time', 'income', 'comment', 'operate']
    }
}


########################################################################
class TabWidget(QtWidgets.QTabWidget):

    # ------------------------------------------------------------------
    def __init__(self, mainEngine, parent=None):
        super(TabWidget, self).__init__(parent)
        self.mainEngine = mainEngine

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        self._major_tab = None          # 当前主页面
        self._records = None            # 当前主页面信息表
        self._tab_dict = {}             # 已打开的页面字典

        self.major_tab('editor')

    # ------------------------------------------------------------------
    @ensure_mongo_login
    def major_tab(self, flag):
        if self._major_tab == flag:
            self.setCurrentIndex(0)
            return
        else:
            self.removeTab(0)

        if flag in HEADERS_MAP.keys():
            self._records = self.mainEngine.dbQuery('system_db', flag)
            self.insertTab(0, Table([HEADERS_MAP[flag]['headers'], self._records], self), HEADERS_MAP[flag]['title'])
        elif flag == 'data_manage':
            self.insertTab(0, DataManager(self), '数据管理')
        elif flag == 'configure':
            self.insertTab(0, Configure(self), '参数设置')
        else:
            return

        self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)    # 设置首页为不可关闭
        self.setCurrentIndex(0)
        self._major_tab = flag

    # ------------------------------------------------------------------
    def open_tab(self, tab_id, tab_type):
        if tab_id in self._tab_dict:
            self.setCurrentIndex(self.indexOf(self._tab_dict[tab_id]))
            return

        if tab_type == 'edit':
            record = [x for x in self._records if x['_id'] == tab_id]
            if record:
                frame = Editor(record[0])
                title = '我的策略 - %s' % record[0]['name']
        elif tab_type == 'paper_trading':
            record = [x for x in self._records if x['_id'] == tab_id]
            if record:
                frame = PaperTrader(record[0])
                title = '模拟交易 - %s' % record[0]['name']
        elif tab_type == 'real_trading':
            record = [x for x in self._records if x['_id'] == tab_id]
            if record:
                frame = RealTrader(record[0])
                title = '实盘交易 - %s' % record[0]['trade_name']
        elif tab_type == 'account':
            record = [x for x in self._records if x['_id'] == tab_id]
            if record:
                frame = FundsAccount(record[0])
                title = '资金账户 - %s' % record[0]['account']
        elif tab_type == 'backtest':
            record = [x for x in self.mainEngine.dbQuery('system_db', 'backtest_history') if x['_id'] == tab_id]
            if record:
                frame = BackTester(record[0])
                title = '回测结果 - %s' % record[0]['name']
        elif tab_type == 'backtest_history':
            # 当打开'历史回测'页面时，tab_id 为策略名
            record = self.mainEngine.dbQuery('system_db', 'backtest_history', d={'name': tab_id})
            _list = ['data', record] if record else ['header', HEADERS_MAP['backtest_history']['headers']]
            frame = Table(_list)
            title = '历史回测 - %s' % tab_id
        else:
            raise NotImplementedError

        self.addTab(frame, title)
        self._tab_dict[tab_id] = frame

    # ------------------------------------------------------------------
    def close_tab(self, idx):
        """
        页面关闭请求，这里可以检测编辑的策略是否已保存。
        未保存的策略用弹出框提示
        """
        pass
