#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
@Author: freemoses
@Since: 2019-08-27 22:49:33
@LastEditTime: 2019-09-14 13:11:58
@Description: MongoDB data service api
'''

from typing import Any

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import ConnectionFailure

from tpro.utils import load_json


class MongoApi():
    """
    MongoDB 数据服务类，提供数据的增、删、查、改等操作
    """
    config = "api.json"

    def __init__(self):
        setting = load_json(self.config, 'MongoDB')
        uri = 'mongodb://{}:{}'.format(setting.get('HOST', '127.0.0.1'), setting.get('PORT', 27017))

        try:
            self.db_client = MongoClient(uri, serverSelectionTimeoutMS=10)
            self.db_client.server_info()
        except ConnectionFailure:
            self.db_client = None

    # ------------------------------------------------------------------
    def query(self,
              db_name: str,
              collection_name: str,
              flt: dict = None,
              sort_key: str = '',
              direction: int = ASCENDING):
        """
        查询数据，flt为查询条件，sort_key为排序关键字，direction为排序方式
        """
        flt = {} if flt is None else flt

        assert isinstance(flt, dict), "Invaild query filtering conditions."

        if self.db_client:
            cl = self.db_client[db_name][collection_name]
            direction = ASCENDING if direction > 0 else DESCENDING
            cursor = cl.find(flt).sort(sort_key, direction) if sort_key else cl.find(flt)
            return list(cursor)
        return False

    # ------------------------------------------------------------------
    def insert(self, db_name: str, collection_name: str, data: Any, index_key: str = 'datetime'):
        """
        插入数据，data为具体数据(字典或列表类型)，index_key为索引字段(默认为'datetime'字段)
        """
        assert isinstance(data, (dict, list)), "Can't insert %s data." % type(data)

        if self.db_client:
            cl = self.db_client[db_name][collection_name]
            cl.ensure_index([(index_key, ASCENDING)], unique=True)

            try:
                if isinstance(data, dict):
                    _id = cl.insert_one(data)
                    return _id.inserted_id
                if isinstance(data, list):
                    _id = cl.insert_many(data)
                    return _id.inserted_ids
            except:
                return False
        return False

    # ------------------------------------------------------------------
    def update(self, db_name: str, collection_name: str, data: dict, flt: dict, upsert: bool = False):
        """
        更新数据，data为具体数据, flt为过滤条件， upsert表示若无是否要插入
        """
        assert isinstance(data, dict), "Can't insert %s data." % type(data)
        assert isinstance(flt, dict), "Invaild filter conditions."

        if self.db_client:
            cl = self.db_client[db_name][collection_name]

            try:
                cl.replace_one(flt, data, upsert)
                return True
            except:
                return False
        return False

    # ------------------------------------------------------------------
    def delete(self, db_name: str, collection_name: str, flt: dict):
        """
        删除数据，flt为过滤条件
        """
        assert isinstance(flt, dict), "Invaild delete filtering conditions."

        if self.db_client:
            cl = self.db_client[db_name][collection_name]

            try:
                cl.delete_many(flt)
                return True
            except:
                return False
        return False
