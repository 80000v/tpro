#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-08-23 13:47:06
@LastEditTime: 2019-09-10 06:43:03
@Description: Main entry for Trader Pro system
'''

import platform
import sys

import qtawesome
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget)

from tpro.core.ui.clock import AnalogClock
from tpro.core.ui.funcWidget import TabWidget
from tpro.resource import theme
from tpro.utils import BASIC_FONT, load_icon


class MainWindow(QWidget):
    """系统主窗体"""
    def __init__(self):
        super(MainWindow, self).__init__()

        self.tab = TabWidget()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('Trader Pro')
        # 按钮
        editor_btn = QPushButton(qtawesome.icon('mdi.finance', color='gray', color_active='orange'), '我的策略')
        editor_btn.clicked.connect(lambda: self.tab.set_homepage('my_strategy'))

        paper_trading_btn = QPushButton(qtawesome.icon('fa5s.chalkboard', color='gray', color_active='orange'), '模拟交易')
        paper_trading_btn.clicked.connect(lambda: self.tab.set_homepage('paper_trading'))

        real_trading_btn = QPushButton(qtawesome.icon('fa5s.money-check-alt', color='gray', color_active='orange'),
                                       '实盘交易')
        real_trading_btn.clicked.connect(lambda: self.tab.set_homepage('real_trading'))

        account_btn = QPushButton(qtawesome.icon('fa5s.yen-sign', color='gray', color_active='orange'), '资金账户')
        account_btn.clicked.connect(lambda: self.tab.set_homepage('funds_account'))

        data_manage_btn = QPushButton(qtawesome.icon('fa5s.database', color='gray', color_active='orange'), '数据管理')
        data_manage_btn.clicked.connect(lambda: self.tab.set_homepage('data_manage'))

        configure_btn = QPushButton(qtawesome.icon('fa5s.cogs', color='gray', color_active='orange'), '参数设置')
        configure_btn.clicked.connect(lambda: self.tab.set_homepage('config'))

        nav_lyt = QVBoxLayout()
        nav_lyt.setContentsMargins(0, 0, 0, 0)
        nav_lyt.addWidget(AnalogClock())
        nav_lyt.addWidget(editor_btn, alignment=Qt.AlignRight)
        nav_lyt.addWidget(paper_trading_btn, alignment=Qt.AlignRight)
        nav_lyt.addWidget(real_trading_btn, alignment=Qt.AlignRight)
        nav_lyt.addWidget(account_btn, alignment=Qt.AlignRight)
        nav_lyt.addWidget(data_manage_btn, alignment=Qt.AlignRight)
        nav_lyt.addWidget(configure_btn, alignment=Qt.AlignRight)
        nav_lyt.addStretch()

        main_lyt = QHBoxLayout(self)
        main_lyt.addLayout(nav_lyt)
        main_lyt.addWidget(self.tab)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    tApp = QApplication(['Trader Pro', ''])

    # 设置字体
    tApp.setFont(BASIC_FONT)

    # 设置程序图标
    tApp.setWindowIcon(load_icon('app.ico'))

    # 设置Windows进程ID
    if 'Windows' in platform.uname():
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Trader Pro')

    # 设置外观样式
    try:
        tApp.setStyleSheet(theme.load_stylesheet('custom.qss'))
    except:
        pass

    mw = MainWindow()
    mw.showMaximized()

    # 在主线程中启动Qt事件循环
    sys.exit(tApp.exec_())
