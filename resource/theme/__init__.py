#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-08-31 11:45:13
@LastEditTime: 2019-09-10 06:44:10
@Description: system theme model
'''

import logging
import platform

from PyQt5.QtCore import QFile, QTextStream


#----------------------------------------------------------------------
def _logger():
    return logging.getLogger('theme')


# ----------------------------------------------------------------------
def load_stylesheet(theme: str = "default"):

    # 过渡方案
    if theme == "dark":
        return load_stylesheet_dark()

    if theme == "orange":
        return load_stylesheet_orange()

    if theme == "white":
        return load_stylesheet_white()

    if theme == "default":
        return load_stylesheet_default()

    return load_stylesheet_custom(theme)

    """
    以下为统一资源后的代码
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
    import tpro.resource.theme.darkstyle_rc

    f = QFile(":dark/style.qss")
    if not f.exists():
        # _logger().error("未发现相关资源，无法加载'经典暗黑'主题！")
        return ""

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
    import tpro.resource.theme.orangestyle_rc

    f = QFile(":orange/style.qss")
    if not f.exists():
        _logger().error("未发现相关资源，无法加载'炫酷暗橙'主题！")
        return ""

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
    import tpro.resource.theme.whitestyle_rc

    f = QFile(":white/style.qss")
    if not f.exists():
        _logger().error("未发现相关资源，无法加载'靓丽白色'主题！")
        return ""

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
    import tpro.resource.theme.defaultstyle_rc

    f = QFile(":default/style.qss")
    if not f.exists():
        _logger().error("未发现相关资源，无法加载默认主题！")
        return ""

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
def load_stylesheet_custom(file_name):
    from tpro.utils import load_qss

    f = QFile(load_qss(file_name))
    if not f.exists():
        _logger().error("未发现相关QSS文件，无法加载指定样式表！")
        return ""

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
