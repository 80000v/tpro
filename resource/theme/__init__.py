#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2019 Freemoses
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import platform
from PyQt5.QtCore import QFile, QTextStream

__version__ = "0.1.0"
__author__ = "freemoses"


#----------------------------------------------------------------------
def _logger():
    return logging.getLogger('theme')


# ----------------------------------------------------------------------
def load_stylesheet(theme="default"):

    # 过渡方案
    if theme == "dark":
        return load_stylesheet_dark()
    elif theme == "orange":
        return load_stylesheet_orange()
    elif theme == "white":
        return load_stylesheet_white()
    else:
        return load_stylesheet_default()

    # 以下为统一资源后的代码
    """
    f = QFile(":{0}/style.qss".format(theme))
    if not f.exists():
        _logger().error('未找到资源文件，无法加载"{0}"皮肤'.format(theme))
        return ""
    else:
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
        if platform.system().lower() == 'darwin':
            mac_fix = '''
            QDockWidgets::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }'''
            stylesheet += mac_fix
        return stylesheet
    """


# ----------------------------------------------------------------------
def load_stylesheet_dark():
    import QuanTrader.resource.theme.darkstyle_rc

    f = QFile(":dark/style.qss")
    if not f.exists():
        # _logger().error("未发现相关资源，无法加载'经典暗黑'主题！")
        return ""
    else:
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
        if platform.system().lower() == 'darwin':
            mac_fix = '''
            QDockWidgets::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }'''
            stylesheet += mac_fix
        return stylesheet


# ----------------------------------------------------------------------
def load_stylesheet_orange():
    import QuanTrader.resource.theme.orangestyle_rc

    f = QFile(":orange/style.qss")
    if not f.exists():
        _logger().error("未发现相关资源，无法加载'炫酷暗橙'主题！")
        return ""
    else:
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
        if platform.system().lower() == 'darwin':
            mac_fix = '''
            QDockWidgets::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }'''
            stylesheet += mac_fix
        return stylesheet


# ----------------------------------------------------------------------
def load_stylesheet_white():
    import QuanTrader.resource.theme.whitestyle_rc

    f = QFile(":white/style.qss")
    if not f.exists():
        _logger().error("未发现相关资源，无法加载'靓丽白色'主题！")
        return ""
    else:
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
        if platform.system().lower() == 'darwin':
            mac_fix = '''
            QDockWidgets::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }'''
            stylesheet += mac_fix
        return stylesheet


# ----------------------------------------------------------------------
def load_stylesheet_default():
    import QuanTrader.resource.theme.defaultstyle_rc

    f = QFile(":default/style.qss")
    if not f.exists():
        _logger().error("未发现相关资源，无法加载默认主题！")
        return ""
    else:
        f.open(QFile.ReadOnly | QFile.Text)
        ts = QTextStream(f)
        stylesheet = ts.readAll()
        if platform.system().lower() == 'darwin':
            mac_fix = '''
            QDockWidgets::title
            {
                background-color: #31363b;
                text-align: center;
                height: 12px;
            }'''
            stylesheet += mac_fix
        return stylesheet
