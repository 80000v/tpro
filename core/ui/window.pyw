#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: freemoses
# DATE: 2019/08/24 周六
# TIME: 03:47:48

# DESCRIPTION: mainwindow class define

import qtawesome as qta
from PyQt5 import QtCore, QtWidgets

from tpro.core.ui.clock import AnalogClock
from tpro.core.ui.tabWidget import TabWidget


########################################################################
class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle('Trader Pro')

        self._tab = TabWidget()

        # 按钮图标
        editor_icon = qta.icon('mdi.finance', color='gray', color_active='orange')
        paper_trading_icon = qta.icon('fa5s.chalkboard', color='gray', color_active='orange')
        real_trading_icon = qta.icon('fa5s.money-check-alt', color='gray', color_active='orange')
        account_icon = qta.icon('fa5s.yen-sign', color='gray', color_active='orange')
        data_manage_icon = qta.icon('fa5s.database', color='gray', color_active='orange')
        config_icon = qta.icon('fa5s.cogs', color='gray', color_active='orange')

        # 按钮
        editor_btn = QtWidgets.QPushButton(editor_icon, '我的策略')
        editor_btn.clicked.connect(lambda: self._tab.set_major_tab('strategy'))

        paper_trading_btn = QtWidgets.QPushButton(paper_trading_icon, '模拟交易')
        paper_trading_btn.clicked.connect(lambda: self._tab.set_major_tab('paper_trade'))

        real_trading_btn = QtWidgets.QPushButton(real_trading_icon, '实盘交易')
        real_trading_btn.clicked.connect(lambda: self._tab.set_major_tab('real_trade'))

        account_btn = QtWidgets.QPushButton(account_icon, '资金账户')
        account_btn.clicked.connect(lambda: self._tab.set_major_tab('funds_account'))

        data_manage_btn = QtWidgets.QPushButton(data_manage_icon, '数据管理')
        data_manage_btn.clicked.connect(lambda: self._tab.set_major_tab('data_manage'))

        configure_btn = QtWidgets.QPushButton(config_icon, '参数设置')
        configure_btn.clicked.connect(lambda: self._tab.set_major_tab('configure'))

        edge_lyt = QtWidgets.QVBoxLayout(self)
        edge_lyt.setContentsMargins(0, 0, 0, 0)
        edge_lyt.addWidget(AnalogClock())
        edge_lyt.addWidget(editor_btn, alignment=QtCore.Qt.AlignRight)
        edge_lyt.addWidget(paper_trading_btn, alignment=QtCore.Qt.AlignRight)
        edge_lyt.addWidget(real_trading_btn, alignment=QtCore.Qt.AlignRight)
        edge_lyt.addWidget(account_btn, alignment=QtCore.Qt.AlignRight)
        edge_lyt.addWidget(data_manage_btn, alignment=QtCore.Qt.AlignRight)
        edge_lyt.addWidget(configure_btn, alignment=QtCore.Qt.AlignRight)
        edge_lyt.addStretch()

        main_lyt = QtWidgets.QHBoxLayout(self)
        main_lyt.addLayout(edge_lyt)
        main_lyt.addWidget(self._tab)

        self.setLayout(main_lyt)
