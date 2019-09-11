#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-09-07 18:00:30
@LastEditTime: 2019-09-10 06:58:35
@Description: 自定义系统功能模块
'''

from typing import Any

import qtawesome
from PyQt5 import QtCore, QtWidgets

from tpro.api.mongo import MongoApi
from tpro.core.ui.baseWidget import (AccountTable, BacktestTable, PaperTradingTable, RealTradingTable, StrategyTable)

# from bson.objectid import ObjectId


########################################################################
class Editor(QtWidgets.QWidget):
    """
    编辑器组件
    """
    def __init__(self, parent: Any = None):
        super(Editor, self).__init__(parent)
        self.parent = parent
        self._env = None


########################################################################
class PaperTrader(QtWidgets.QWidget):
    """
    模拟交易组件
    """
    def __init__(self, parent: Any = None):
        super(PaperTrader, self).__init__(parent)
        self.parent = parent
        self._env = None


########################################################################
class RealTrader(QtWidgets.QWidget):
    """
    实盘交易组件
    """
    def __init__(self, parent: Any = None):
        super(RealTrader, self).__init__(parent)
        self.parent = parent
        self._env = None


########################################################################
class FundsAccount(QtWidgets.QWidget):
    """
    资金账号管理组件
    """
    def __init__(self, parent: Any = None):
        super(FundsAccount, self).__init__(parent)
        self.parent = parent
        self._broker = None


########################################################################
class BackTester(QtWidgets.QWidget):
    """
    策略回测组件
    """
    def __init__(self, parent: Any = None):
        super(BackTester, self).__init__(parent)
        self.parent = parent
        self._env = None


########################################################################
class DataManager(QtWidgets.QWidget):
    """
    数据管理组件
    """
    source = 'data_manage'

    def __init__(self, parent: Any = None):
        super(DataManager, self).__init__(parent)
        self.parent = parent
        self._api = None


########################################################################
class Configurator(QtWidgets.QWidget):
    """
    系统参数配置组件
    """
    source = 'config'

    def __init__(self, parent: Any = None):
        super(Configurator, self).__init__(parent)
        self.parent = parent
        self._setting = None


########################################################################
Tab_Type = {
    'my_strategy': ['我的策略', StrategyTable, Editor],
    'paper_trading': ['模拟交易', PaperTradingTable, PaperTrader],
    'real_trading': ['实盘交易', RealTradingTable, RealTrader],
    'funds_account': ['资金账号', AccountTable, FundsAccount],
    'backtest_history': ['历史回测', BacktestTable, BackTester]
}


class TableFrame(QtWidgets.QWidget):
    """
    自定义表格组件，包含搜索、新建、删除功能
    """
    open_tab_signal = QtCore.pyqtSignal(str, str, dict)

    def __init__(self, source: str = None, parent: Any = None):
        super(TableFrame, self).__init__(parent)
        self._db = MongoApi()
        self._source = source if source else 'my_strategy'

        _tbl = Tab_Type[self._source][1]
        self._table = _tbl()

        self.init_ui()

    def init_ui(self):
        """
        初始化用户界面
        """
        self._filter = QtWidgets.QLineEdit()
        self._filter.addAction(qtawesome.icon('fa5s.search', color='white'), self._filter.TrailingPosition)
        self._filter.textChanged.connect(self.filter_record)

        self._new_btn = QtWidgets.QPushButton(qtawesome.icon('fa5s.plus', color='white'), '')
        self._new_btn.clicked.connect(self.new_record)

        self._save_btn = QtWidgets.QPushButton(qtawesome.icon('fa5s.download', color='white'), '')
        self._save_btn.clicked.connect(self.save_record)

        self._table.set_datas(self._db.query('tpro', self._source))

        top_lyt = QtWidgets.QHBoxLayout()
        top_lyt.addStretch()
        top_lyt.addWidget(self._filter)
        top_lyt.addWidget(self._new_btn)
        top_lyt.addWidget(self._save_btn)

        lyt = QtWidgets.QVBoxLayout(self)
        lyt.addLayout(top_lyt)
        lyt.addWidget(self._table)

    def change_source(self):
        """
        更改首页功能模块
        """
        self.layout().removeWidget(self._table)
        del self._table

        _tbl = Tab_Type[self._source][1]
        _datas = self._db.query('tpro', self._source)

        self._table = _tbl()
        self._table.set_datas(_datas)
        self.layout().addWidget(self._table)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, flag: str):
        if self._source == flag:
            return

        self._source = flag
        self.change_source()

    def filter_record(self, key: str):
        """
        根据关键字模糊查找记录，并回显至表格
        """
        self._table.set_datas(self._db.query('tpro', self._source, flt={'name': {'$regex': key}}))

    def new_record(self, data: dict):
        """
        新建记录，并回显至表格
        """
        _id = self._db.insert('tpro', self._source, data)
        data['_id'] = _id
        self._table.insert_new_row(data, 'bottom')

    def save_record(self):
        """
        保存当前表格数据
        """
        self._table.save_csv()


class TabWidget(QtWidgets.QTabWidget):
    """
    自定义选项卡组件
    """
    def __init__(self, parent: Any = None):
        super(TabWidget, self).__init__(parent)
        self._home_wgt = None  # 首页标识
        self._tabs_dict = {}  # 选项卡字典

        self.init_ui()

    def init_ui(self):
        """
        初始化用户界面
        """
        self.setTabsClosable(True)
        self.setElideMode(QtCore.Qt.ElideRight)
        self.setStyleSheet('QTabBar::tab{background-color:rbg(255,255,255,0);}')

        self.tabCloseRequested.connect(self.close_tab)

        self.set_homepage()

    def set_homepage(self, flag: str = 'my_strategy'):
        """
        根据标识符生成首页功能模块，默认首页显示'我的策略'
        """
        if self._home_wgt is None:
            self._home_wgt = TableFrame()
            self._home_wgt.open_tab_signal.connect(self.open_tab)

            _widget = QtWidgets.QWidget()
            _lyt = QtWidgets.QHBoxLayout(_widget)
            _lyt.setContentsMargins(0, 0, 0, 0)
            _lyt.addWidget(self._home_wgt)

            self.insertTab(0, _widget, '我的策略')
            self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)
            self.setCurrentIndex(0)
            return

        if self._home_wgt.source == flag:
            self.setCurrentIndex(0)
            return

        if flag in Tab_Type and isinstance(self._home_wgt, TableFrame):
            self.setTabText(0, Tab_Type[flag][0])
            self._home_wgt.source = flag
            self.setCurrentIndex(0)
            return

        if flag in Tab_Type:
            _title = Tab_Type[flag][0]
            _widget = TableFrame(flag, self)
            _widget.open_tab_signal.connect(self.open_tab)
        elif flag == 'data_manage':
            _title = '数据管理'
            _widget = DataManager(self)
        elif flag == 'config':
            _title = '参数配置'
            _widget = Configurator(self)
        else:
            raise NotImplementedError

        self.setTabText(0, _title)
        self.widget(0).layout().removeWidget(self._home_wgt)
        self.widget(0).layout().addWidget(_widget)
        self.setCurrentIndex(0)
        self._home_wgt = _widget

    def open_tab(self, _id: str, flag: str, datas: dict = None):
        """
        根据文档'_id'打开或创建选项页
        """
        if _id in self._tabs_dict:
            self.setCurrentIndex(self._tabs_dict[_id][0])
            return

        assert flag in Tab_Type, 'Invaild tab type - {}!'.format(flag)

        _title, _, _widget = Tab_Type[flag]
        _widget = _widget(datas, self)

        idx = self.addTab(_widget, _title)
        self.setTabToolTip(idx, _title)

        self._tabs_dict[_id] = [idx, _widget]

    def close_tab(self, idx: int):
        """
        关闭选项页时调用，当选项页为策略编辑页面时检测是否已保存
        """
        _id = [x for x in self._tabs_dict if self._tabs_dict[x][0] == idx]

        if _id:
            del self._tabs_dict[_id.pop()]
