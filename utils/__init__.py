#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: freemoses
# DATE: 2019/08/24 周六
# TIME: 03:42:12

# DESCRIPTION: the folder for general functions

import json
import os
import traceback

from PyQt5.QtGui import QIcon

# 图标及JSON配置路径字典（全局变量）
ICONS = {}
JSONS = {}

# 遍历安装目录
for root, subdirs, files in os.walk(os.path.abspath(os.path.dirname(__file__))):
    for filename in files:
        if '.ico' in filename or '.png' in filename:
            ICONS[filename] = os.path.join(root, filename)
        if '.json' in filename:
            JSONS[filename] = os.path.join(root, filename)

# 遍历工作目录
for root, subdirs, files in os.walk(os.getcwd()):
    for filename in files:
        if '.ico' in filename or '.png' in filename:
            ICONS[filename] = os.path.join(root, filename)
        if '.json' in filename:
            JSONS[filename] = os.path.join(root, filename)


# ----------------------------------------------------------------------
def load_icon(icon_name: str):
    """
    Get QIcon object with ico name
    """
    return QIcon(ICONS.get(icon_name, ''))


# ----------------------------------------------------------------------
def load_json(file: str):
    """
    Load data from json file
    """
    file_path = JSONS.get(file, '')

    try:
        with open(file_path, mode='r', encoding='UTF-8') as f:
            data = json.load(f)
        return data
    except:
        traceback.print_exc()


# ----------------------------------------------------------------------
def save_json(file: str, data: dict):
    """
    Save data into json file
    """
    file_path = JSONS.get(file, '')

    with open(file_path, mode='w+', encoding='UTF-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ----------------------------------------------------------------------
def get_temp_file(file: str):
    """
    Get path for temp file with filename
    """
    temp_path = os.path.join(os.getcwd(), 'tmp')
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    return os.path.join(temp_path, file)
