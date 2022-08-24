#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:sqlite_opt
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description:
"""

import unittest
import sqlite3
from loguru import logger as default_logger
from testrunner.utils.singleton import Singleton


class Sqlite3Operation(object, metaclass=Singleton):
    """sqlite3 数据库操作"""

    def __init__(self, db_path, show=False, logger=default_logger):
        self.db_path = db_path
        self.show = show
        self.logger = logger

        self.conn = None
        self.connect()

    def connect(self):
        self.logger.info("连接 {} ...".format(self.db_path))
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.logger.info("连接 {} 成功！".format(self.db_path))
        except Exception as e:
            raise e

    def close(self):
        self.logger.info("断开Sqlite3数据库的连接...")
        self.conn.close()

    def execute(self, sql, args=[]):
        """
        执行sql命令
        :param sql:
        :param args:
        :return:
        """
        if self.show:
            self.logger.debug('sql:[{}],args:[{}]'.format(sql, args))
        cursor = self.conn.cursor()

        try:
            rows = cursor.execute(sql, args)
            self.conn.commit()
            return rows
        except Exception as e:
            self.logger.warning('{err}, rollback commit ...'.format(err=e))
            self.conn.rollback()
            return False

    def create_table(self, sql):
        """
        create table
        :param sql:
        :return:
        """

        if sql is not None and sql != '':
            self.execute(sql)
            self.logger.info('create tablle success')
        else:
            self.logger.info('the [{}] is empty or equal None!'.format(sql))

    def insert_update_delete(self, sql, data_list=None):
        if sql is not None and sql != '':
            if data_list is not None:
                for d in data_list:
                    self.execute(sql, d)
            else:
                self.execute(sql)
        else:
            self.logger.info('The [{}] is empty or equal None!'.format(sql))

    def fetchall(self, sql):
        if self.show:
            self.logger.info('execute sql:[{}]'.format(sql))

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            if self.show:
                for row in rows:
                    self.logger.info(row)
                self.logger.info('=' * 50)
            return rows
        except Exception as e:
            self.conn.rollback()
            raise Exception(e)


class Sqlite3TestCase(unittest.TestCase):
    """docstring for Sqlite3TestCase"""

    def test_1(self):
        """测试创建表"""
        sqlite3_opt = Sqlite3Operation(db_path='../db.sqlite3')
        sqlite3_opt.logger.info("test_1")
        fetchall_sql = '''SELECT * FROM student'''
        create_table = '''CREATE TABLE IF NOT EXISTS `student` (
                              `id` int(11) NOT NULL,
                              `name` varchar(20) NOT NULL,
                              `gender` varchar(4) DEFAULT NULL,
                              `age` int(11) DEFAULT NULL,
                              `address` varchar(200) DEFAULT NULL,
                              `phone` varchar(20) DEFAULT NULL,
                               PRIMARY KEY (`id`)
                            )
                            '''
        sqlite3_opt.execute('DROP TABLE IF EXISTS student')
        sqlite3_opt.create_table(create_table)
        sqlite3_opt.fetchall(fetchall_sql)

    def test_2(self):
        """测试数据插入"""
        sqlite3_opt = Sqlite3Operation(db_path='../db.sqlite3')
        sqlite3_opt.logger.info("test_2")
        fetchall_sql = '''SELECT * FROM student'''
        insert_sql = '''INSERT INTO student values (?, ?, ?, ?, ?, ?)'''
        data = [(1, 'Hongten', 'boy', 20, 'guangzhou', '13423****62'),
                (2, 'Tom', 'boy', 22, 'guangzhou', '15423****63'),
                (3, 'Jake', 'girl', 18, 'guangzhou', '18823****87'),
                (4, 'Cate', 'girl', 21, 'guangzhou', '14323****32')]
        sqlite3_opt.insert_update_delete(insert_sql, data)
        sqlite3_opt.fetchall(fetchall_sql)

    def test_3(self):
        """测试数据更新"""
        sqlite3_opt = Sqlite3Operation(db_path='../db.sqlite3', show=True)
        sqlite3_opt.logger.info("test_3")
        fetchall_sql = '''SELECT * FROM student'''
        # update_sql = 'UPDATE student SET name = ? WHERE ID = ? '
        update_sql = 'UPDATE student SET (name,gender) = (?,?) WHERE ID = ? '
        data = [('HongtenAA2', 'boy', 1),
                ('HongtenBB2', 'boy', 2),
                ('HongtenCC2', 'boy', 3),
                ('HongtenDD2', 'boy', 4)]
        sqlite3_opt.insert_update_delete(update_sql, data)
        sqlite3_opt.fetchall(fetchall_sql)

    def test_4(self):
        """测试数据删除"""
        sqlite3_opt = Sqlite3Operation(db_path='../db.sqlite3')
        sqlite3_opt.logger.info("test_4")
        fetchall_sql = '''SELECT * FROM student'''
        delete_sql = 'DELETE FROM student WHERE NAME = ? AND ID = ? '
        data = [('HongtenAA2', 1),
                ('HongtenCC2', 3)]
        sqlite3_opt.insert_update_delete(delete_sql, data)
        sqlite3_opt.fetchall(fetchall_sql)


if __name__ == '__main__':
    pass
    suite = unittest.TestLoader().loadTestsFromTestCase(Sqlite3TestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
