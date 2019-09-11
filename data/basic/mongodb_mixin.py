#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Freemoses
# @Date:   2019-07-06 11:14:39
# @Last Modified by:   freem
# @Last Modified time: 2019-07-14 12:59:12
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure


class MongoDBMixin(object):
    """docstring for MongoDBMixin"""
    def __init__(self, config):
        super(MongoDBMixin, self).__init__()
        url = 'mongodb://%s:%s' % (config.get('HOST', '127.0.0.1'), config.get('PORT', '27017'))

        try:
            self.dbClient = MongoClient(url, serverSelectionTimesoutMS=10)
            self.dbClient.server_info()
        except ConnectionFailure:
            self.dbClient = None

    def dbInsert(self, dbName, collectionName, d):
        """向MongoDB中插入数据，d是具体数据"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.ensure_index([('datetime', ASCENDING)], unique=True)

            if isinstance(d, dict):
                collection.insert_one(d)
            elif isinstance(d, list):
                collection.insert_many(d)

    def dbQuery(self, dbName, collectionName, flt, sortKey='', sortDirection=ASCENDING):
        """从MongoDB中读取数据，flt是查询要求，返回的是数据库查询的指针"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]

            if sortKey:
                cursor = collection.find(flt).sort(sortKey, sortDirection)    # 对查询出来的数据进行排序
            else:
                cursor = collection.find(flt)

            return cursor

    def dbUpdate(self, dbName, collectionName, d, flt, upsert=False):
        """向MongoDB中更新数据，d是具体数据，flt是过滤条件，upsert代表若无是否要插入"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.replace_one(flt, d, upsert)

    def dbDelete(self, dbName, collectionName, flt):
        """从数据库中删除数据，flt是过滤条件"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.delete_many(flt)
