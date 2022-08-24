#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:mysql_opt
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: MySQL操作
"""
import pymysql
import unittest
from loguru import logger as default_logger


class MysqlOperation(object):
    """MySQL数据库操作"""
    def __init__(self, db_host, db_port, db_user, db_password, db_name,
                 db_charset='utf8mb4', show=False, logger=default_logger):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.db_charset = db_charset
        self.show = show
        self.logger = logger
        self.conn = self.connect()

    def connect(self):
        """
        connect to mysql
        :return:
        """
        self.logger.info("连接MySQL {0}:{1}(DataBase:{2}) ...".format(
            self.db_host, self.db_port, self.db_name))
        try:
            conn = pymysql.connect(
                host=self.db_host, port=self.db_port, user=self.db_user, passwd=self.db_password,
                db=self.db_name, charset=self.db_charset)
            self.logger.info("MySQL数据库已经连接成功!")
            return conn
        except Exception as e:
            raise e

    def close(self):
        self.logger.info("断开MySQL数据库的连接...")
        self.conn.close()

    def execute(self, sql, args=None):
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

    def fetchmany(self, sql, size):
        if self.show:
            print('execute sql:[{}]'.format(sql))

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchmany(size)
            if self.show:
                for row in rows:
                    print(row)
                print('=' * 50)
            return rows
        except Exception as e:
            self.conn.rollback()
            raise Exception(e)

    def fetchone(self, sql):
        if self.show:
            print('execute sql:[{}]'.format(sql))

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchone()
            if self.show:
                for row in rows:
                    print(row)
                print('=' * 50)
            return rows
        except Exception as e:
            self.conn.rollback()
            raise Exception(e)


class MySQLTestCase(unittest.TestCase):
    """docstring for MySQLTestCase"""

    def test_1(self):
        """测试创建表"""
        mysql = MysqlOperation(db_host='192.168.0.208', db_port=3306,
                               db_user='root', db_password='Abcd1234', db_name='Apiplatform')
        mysql.logger.info("test_1")
        fetchall_sql = '''SELECT * FROM student'''

        mysql.execute('DROP TABLE IF EXISTS student')
        create_table = '''CREATE TABLE `student` (
                              `id` int(11) NOT NULL,
                              `name` varchar(20) NOT NULL,
                              `gender` varchar(4) DEFAULT NULL,
                              `age` int(11) DEFAULT NULL,
                              `address` varchar(200) DEFAULT NULL,
                              `phone` varchar(20) DEFAULT NULL,
                               PRIMARY KEY (`id`)
                            )'''
        mysql.create_table(create_table)
        mysql.fetchall(fetchall_sql)

    def test_2(self):
        """测试数据插入"""
        mysql = MysqlOperation(db_host='192.168.0.208', db_port=3306,
                               db_user='root', db_password='Abcd1234', db_name='Apiplatform')
        mysql.logger.info("test_2")
        fetchall_sql = '''SELECT * FROM student'''
        insert_sql = '''INSERT INTO student values (%s, %s, %s, %s, %s, %s)'''
        data = [(1, 'Hongten', 'boy', 20, 'guangzhou', '13423****62'),
                (2, 'Tom', 'boy', 22, 'guangzhou', '15423****63'),
                (3, 'Jake', 'girl', 18, 'guangzhou', '18823****87'),
                (4, 'Cate', 'girl', 21, 'guangzhou', '14323****32')]
        mysql.insert_update_delete(insert_sql, data)
        mysql.fetchall(fetchall_sql)

    def test_3(self):
        """测试数据更新"""
        mysql = MysqlOperation(db_host='192.168.0.208', db_port=3306,
                               db_user='root', db_password='Abcd1234', db_name='Apiplatform', show=True)
        mysql.logger.info("test_3")
        fetchall_sql = '''SELECT * FROM student'''
        update_sql = 'UPDATE student SET name = %s, gender = %s WHERE ID = %s '
        # update_sql = 'UPDATE student SET (name,gender)=(%s,%s) WHERE ID = %s '
        data = [('HongtenAA2', 'boy', 1),
                ('HongtenBB2', 'boy', 2),
                ('HongtenCC2', 'boy', 3),
                ('HongtenDD2', 'boy', 4)]
        mysql.insert_update_delete(update_sql, data)
        mysql.fetchall(fetchall_sql)

    def test_4(self):
        """测试数据删除"""
        mysql = MysqlOperation(db_host='192.168.0.208', db_port=3306,
                               db_user='root', db_password='Abcd1234', db_name='Apiplatform')
        mysql.logger.info("test_4")
        fetchall_sql = '''SELECT * FROM student'''
        delete_sql = 'DELETE FROM student WHERE NAME = %s AND ID = %s '
        data = [('HongtenAA2', 1),
                ('HongtenCC2', 3)]
        mysql.insert_update_delete(delete_sql, data)
        mysql.fetchall(fetchall_sql)


if __name__ == '__main__':
    # test
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(MySQLTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
