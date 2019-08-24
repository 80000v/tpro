#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: freemoses
# DATE: 2019/08/24 周六
# TIME: 03:45:20

# DESCRIPTION: main entry for Trader Pro system

import sys
import platform

from PyQt5.QtWidgets import QApplication

from tpro.core.ui import MainWindow
from tpro.resource import theme
from tpro.utils import load_icon


def main():
    app = QApplication(['Trader Pro', ''])

    # 设置Windows进程ID
    if 'Windows' in platform.uname():
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Trader Pro')

    # 设置程序图标
    app.setWindowIcon(load_icon('app.ico'))
    # app.setWindowsIcon(QIcon(':/app.ico'))

    try:
        app.setStyleSheet(theme.load_stylesheet('dark'))
    except:
        pass

    mw = MainWindow()
    mw.showMaximized()

    sys.exit(app.exec_())


# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
