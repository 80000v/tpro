#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-09-07 18:00:30
@LastEditTime: 2019-09-20 20:20:01
@Description: 自定义系统功能模块
'''

from typing import Any

import qtawesome
from bson import ObjectId
from PyQt5 import QtCore, QtWidgets

from tpro.api.mongo import MongoApi
from tpro.core.ui.baseWidget import (AccountTable, BacktestTable, NewAccount, NewRealTrading, NewStrategy,
                                     PaperTradingTable, RealTradingTable, StrategyTable)
from tpro.core.ui.editor import Editor


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


class TableFrame(QtWidgets.QFrame):
    """
    自定义表格页面，包含搜索、新建、删除功能
    """
    open_tab_signal = QtCore.pyqtSignal(dict)

    dialog_type = {'my_strategy': NewStrategy, 'real_trading': NewRealTrading, 'funds_account': NewAccount}

    def __init__(self, source: str = None, parent: Any = None):
        super(TableFrame, self).__init__(parent)
        self._db = MongoApi()
        self._source = source if source else 'my_strategy'

        _tbl = Tab_Type[self._source][1]
        self._table = _tbl(self)

        self.init_ui()

    def init_ui(self):
        """
        Initialize user interface
        """
        self.setStyleSheet(
            "QHeaderView::section{background-color: transparent;font-size: 13px;font-weight: bold;padding-left: 4px;border: 0px;}"
        )

        self._filter = QtWidgets.QLineEdit()
        self._filter.addAction(qtawesome.icon('fa5s.search', color='white'), self._filter.TrailingPosition)
        self._filter.textChanged.connect(self.filter_record)

        self._new_btn = QtWidgets.QPushButton(qtawesome.icon('fa5s.plus', color='white'), '')
        self._new_btn.clicked.connect(self.new_dialog)

        self._save_btn = QtWidgets.QPushButton(qtawesome.icon('fa5s.download', color='white'), '')
        self._save_btn.clicked.connect(self.save_records)

        self._table.set_datas(self._db.query('tpro', self._source))

        top_lyt = QtWidgets.QHBoxLayout()
        top_lyt.addStretch(1)
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

        self._table = _tbl(self)
        self._table.set_datas(_datas)
        self.layout().addWidget(self._table)
        self._filter.clear()

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

    def new_dialog(self):
        """
        新建记录，并回显至表格
        """
        _dialog = self.dialog_type[self._source]()
        _dialog.ok_signal.connect(self.add_record)
        _dialog.exec_()

    def add_record(self, data: dict, index: str):
        _id = self._db.insert('tpro', self._source, data, index)
        if _id:
            data['_id'] = _id
            self._table.insert_new_row(data, 'bottom')

    def save_records(self):
        """
        保存当前表格数据
        """
        self._table.save_csv()

    def perform_operate(self, collection: str, opt: str, flt: dict, data: dict = None):
        """
        Save operate result
        """
        if opt == 'update':
            self._db.update('tpro', collection, data, flt)
            return

        if opt == 'delete':
            self._db.delete('tpro', collection, flt)
            return


class TabWidget(QtWidgets.QTabWidget):
    """
    自定义选项卡组件
    """
    def __init__(self, parent: Any = None):
        super(TabWidget, self).__init__(parent)
        self._tabs = [None]        # 已开选项卡列表

        self.init_ui()

    def init_ui(self):
        """
        Initialize user interface
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
        if self._tabs[0] is None:
            self._tabs[0] = TableFrame()
            self._tabs[0].open_tab_signal.connect(self.open_tab)

            _widget = QtWidgets.QWidget()
            _lyt = QtWidgets.QHBoxLayout(_widget)
            _lyt.setContentsMargins(0, 0, 0, 0)
            _lyt.addWidget(self._tabs[0])

            self.insertTab(0, _widget, '我的策略')
            self.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)
            self.setCurrentIndex(0)
            return

        if self._tabs[0].source == flag:
            self.setCurrentIndex(0)
            return

        if flag in Tab_Type and isinstance(self._tabs[0], TableFrame):
            self.setTabText(0, Tab_Type[flag][0])
            self._tabs[0].source = flag
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
        self.widget(0).layout().removeWidget(self._tabs[0])
        self.widget(0).layout().addWidget(_widget)
        self.setCurrentIndex(0)
        self._tabs[0] = _widget

    def open_tab(self, _document: dict):
        """
        根据文档数据打开或创建选项页
        """
        _id = _document['_id']
        _name = _document['name']

        if _id in self._tabs:
            self.setCurrentIndex(self._tabs.index(_id))
            return

        _title, _, _widget = Tab_Type[self._tabs[0].source]
        _title = '-'.join([_title, _name])
        _widget = _widget(_document, self)
        _widget.operate_signal.connect(self._tabs[0].perform_operate)

        idx = self.addTab(_widget, _title)
        self.setTabToolTip(idx, _title)
        self.setCurrentIndex(idx)

        self._tabs.append(_id)

    def open_history(self, _id: ObjectId):
        """
        Open new tab with specify _id
        """
        if _id in self._tabs:
            self.setCurrentIndex(self._tabs.index(_id))
            return



    def close_tab(self, idx: int):
        """
        关闭选项页时调用，当选项页为策略编辑页面时检测是否已保存
        """
        _wgt = self.widget(idx)

        if isinstance(_wgt, Editor):
            if not _wgt.ok_to_continue:
                reply = QtWidgets.QMessageBox.question(self, '策略代码未保存', '是否保存当前策略代码？',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.Yes)
                if reply == QtWidgets.QMessageBox.Yes:
                    _wgt.save_code()

            _wgt.gather_config()

        self._tabs.pop(idx)
        self.removeTab(idx)
