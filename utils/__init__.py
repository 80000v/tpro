#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-08-23 14:07:36
@LastEditTime: 2019-09-19 08:15:15
@Description: the folder for general functions
'''

import json
import os
import traceback
from typing import Any

from PyQt5.QtGui import QFont, QIcon

BASIC_FONT = QFont(u'微软雅黑', 11)

# 图标及JSON配置路径字典（全局变量）
Icon_Map = {}
Json_Map = {}
Qss_Map = {}

# 遍历安装目录
for root, subdirs, files in os.walk(os.path.abspath(os.path.dirname(__file__))):
    for filename in files:
        if '.ico' in filename or '.png' in filename:
            Icon_Map[filename] = os.path.join(root, filename)
        if '.json' in filename:
            Json_Map[filename] = os.path.join(root, filename)
        if '.qss' in filename:
            Qss_Map[filename] = os.path.join(root, filename)

# 遍历工作目录
for root, subdirs, files in os.walk(os.getcwd()):
    for filename in files:
        if '.ico' in filename or '.png' in filename:
            Icon_Map[filename] = os.path.join(root, filename)
        if '.json' in filename:
            Json_Map[filename] = os.path.join(root, filename)
        if '.qss' in filename:
            Qss_Map[filename] = os.path.join(root, filename)


# ----------------------------------------------------------------------
def load_icon(icon_name: str):
    """
    Get QIcon object with ico name
    """
    return QIcon(Icon_Map.get(icon_name, ''))


# ----------------------------------------------------------------------
def load_json(file_name: str, sub_item: str = None):
    """
    Load data from json file, you can select one of the subitems
    """
    file_path = Json_Map.get(file_name, '')

    try:
        with open(file_path, mode='r', encoding='UTF-8') as f:
            data = json.load(f)

        if sub_item is None:
            return data

        return data.get(sub_item, {})
    except:
        traceback.print_exc()


# ----------------------------------------------------------------------
def save_json(file_name: str, data: dict, sub_item: str = None):
    """
    Save data into json file, you can specify one of the subitems
    """
    if sub_item is None:
        full_data = data
    else:
        full_data = load_json(file_name)
        full_data[sub_item] = data

    file_path = Json_Map.get(file_name, '')

    with open(file_path, mode='w+', encoding='UTF-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ----------------------------------------------------------------------
def load_qss(file_name: str):
    """
    Get Qss file absolutely path
    """
    return Qss_Map.get(file_name, '')


# ----------------------------------------------------------------------
def get_temp_file(file_name: str):
    """
    Get path for temp file with filename
    """
    temp_path = os.path.join(os.getcwd(), 'tmp')
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    return os.path.join(temp_path, file_name)


# ----------------------------------------------------------------------
def get_dict_value(target_dict: dict, keyword: str):
    """
    Get keyword's value from target dictionary with recursive algorithm
    """
    _value = None
    for key, value in target_dict.items():
        if key == keyword:
            _value = value
        elif isinstance(value, dict):
            _value = get_dict_value(value, keyword)
    if _value is None:
        return ''
    return _value


# ----------------------------------------------------------------------
def set_dict_value(target_dict: dict, keyword: str, value: Any):
    """
    Set keyword's value in target dictionary with recursive algorithm
    """
    for k, v in target_dict.items():
        if k == keyword:
            target_dict[k] = value
            return
        if isinstance(v, dict):
            set_dict_value(v, keyword, value)
    return
