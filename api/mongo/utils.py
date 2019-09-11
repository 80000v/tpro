#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-08-27 22:49:33
@LastEditTime: 2019-09-10 07:07:27
@Description:
'''

import datetime as dt
from collections import namedtuple

import numpy as np
import pandas as pd

try:
    basestring
except NameError:
    basestring = str

long_nan = 9223372036854775807

def is_long_nan(v):
    if v == long_nan:
        return True
    return False


def to_nan(x):
    if is_long_nan(x):
        return np.nan
    return x


def _to_date(row):
    date = int(row['DATE'])
    return pd.datetime(year=date // 10000, month=date // 100 % 100, day=date % 100)


def _to_datetime(row):
    date = int(row['DATE'])
    time = int(row['TIME']) // 1000
    return pd.datetime(year=date // 10000, month=date // 100 % 100, day=date % 100,
                       hour=time // 10000, minute=time // 100 % 100, second=time % 100)


def _to_dataframe(cloumset, index_func=None, index_column=None):
    df = pd.DataFrame(cloumset)
    for col in df.columns:
        if df.dtypes.loc[col] == np.int64:
            df.loc[:, col] = df.loc[:, col].apply(to_nan)
    if index_func:
        df.index = df.apply(index_func, axis=1)
    elif index_column:
        df.index = df[index_column]
        del df.index.name

    return df


def _error_to_str(error):
    if error:
        if 'message' in error:
            return str(error['error']) + "," + error['message']
        return str(error['error']) + ","
    return ","


def to_obj(class_name, data):
    try:
        if isinstance(data, (list, tuple)):
            result = []
            for d in data:
                result.append(namedtuple(class_name, list(d.keys()))(*list(d.values())))
            return result

        if type(data) == dict:
            result = namedtuple(class_name, list(data.keys()))(*list(data.values()))
            return result
        return data
    except Exception as e:
        print(class_name, data, e)
        return data


def to_date_int(date):
    if isinstance(date, basestring):
        tmp = date.replace('-' , '')
        return int(tmp)
    if isinstance(date, (int, np.integer)):
        return date
    return -1


def to_time_int(time):
    if isinstance(time, basestring):
        if ':' in time:
            tmp = time.replace(':','')
            return int(tmp)

        t = dt.datetime.strptime(time, "%H:%M:%S")
        time_int = t.hour * 10000 + t.minute * 100 + t.second
        return time_int

    if isinstance(time, (int, np.integer)):
        return time
    return -1


def extract_result(cr, data_format="", index_column=None, class_name=""):
    """
        format supports pandas, obj.
    """

    err = _error_to_str(cr['error']) if 'error' in cr else None
    if 'result' in cr and cr['result'] is not None:
        if data_format == "pandas":
            if index_column:
                return (_to_dataframe(cr['result'], None, index_column), err)
            # if 'TIME' in cr['result']:
            #     return (_to_dataframe(cr['result'], _to_datetime), err)
            # elif 'DATE' in cr['result']:
            #     return (_to_dataframe(cr['result'], _to_date), err)
            return (_to_dataframe(cr['result']), err)

        if data_format == "obj" and cr['result'] and class_name:
            r = cr['result']
            if isinstance(r, (list, tuple)):
                result = []
                for d in r:
                    result.append(namedtuple(class_name, list(d.keys()))(*list(d.values())))
            elif isinstance(r, dict):
                result = namedtuple(class_name, list(r.keys()))(*list(r.values()))
            else:
                result = r

            return (result, err)
        return (cr['result'], err)
    return (None, err)
