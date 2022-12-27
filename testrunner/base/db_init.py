#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:db_init
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import os
import json
from loguru import logger

from testrunner.config import BASE_DIR, DB_INFO
from testrunner.base.models import ReportSummary
from testrunner.libs.sqlite_opt import Sqlite3Operation
from testrunner.libs.mysql_opt import MysqlOperation


class InitDB(object):
    """数据库初始化"""
    def __init__(self):
        self.db = None
        self.connect()
        self.table_name = "flex_testreport"

    def connect(self):
        """连接数据库"""
        if DB_INFO.get('ENGINE') == 'django.db.backends.sqlite3':
            db_path = os.path.join(BASE_DIR, DB_INFO.get('NAME'))  # os.path.abspath(os.path.join(root_dir, '../db.sqlite3'))
            self.db = Sqlite3Operation(db_path, logger=logger, show=True)
        elif DB_INFO.get('ENGINE') == 'django.db.backends.mysql':
            user = DB_INFO.get('USER')
            password = DB_INFO.get('PASSWORD')
            host = DB_INFO.get('HOST')
            port = DB_INFO.get('PORT')
            name = DB_INFO.get('NAME')
            self.db = MysqlOperation(host, port, user, password, name, logger=logger, show=True)
        else:
            logger.critical("错误的数据库类型，将跳过结果写入！")

    def create_table_if_not_exist(self):
        """
        CREATE TABLE IF NOT EXISTS "xxxxx"
        :return:
        """
        sql = '''
        CREATE TABLE IF NOT EXISTS "{}" (
          "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
          "create_time" datetime,
          "update_time" datetime,
          "delete_time" datetime,
          "is_delete" bool default(0),
          "build_type" varchar(20),
          "build_status" varchar(50),
          "success" bool default(0),
          "name" varchar(500),
          "description" varchar(4096),
          "status" varchar(50),
          "time" TEXT,
          "testcases_stat" TEXT,
          "teststeps_stat" TEXT,
          "log_path" varchar(2048),
          "report_allure_path" varchar(2048),
          "report_html_path" varchar(2048),
          "jenkins_job_name" varchar(100),
          "jenkins_build_number" integer,
          "allure_url" varchar(500),
          "env_id" integer default(0)
          )
        '''.format(self.table_name)

        logger.info("CREATE TABLE IF NOT EXISTS \"{}\" ...".format(self.table_name))
        self.db.create_table(sql)
        return True

    def get_last_id(self):
        sql = '''SELECT id FROM {} ORDER BY id DESC LIMIT 1'''.format(self.table_name)
        rows = self.db.execute(sql)
        for row in rows.fetchall():
            return row.id
        return 1

    def insert_init_testreport(self, report_id):
        report = ReportSummary().dict()
        report["id"] = report_id
        keys = report.keys()
        place_str = '%s' if self.db.__class__.__name__ == 'MysqlOperation' else '?'
        set_str = ', '.join([place_str for _ in keys])
        insert_sql = '''INSERT INTO {}({})  values ({})'''.format(self.table_name, ','.join(keys), set_str)
        values = []
        for k, v in report.items():
            if k in ['status']:
                values.append(v.value)
            elif k in ['time', 'testcases_stat', 'teststeps_stat']:
                values.append(json.dumps(v, indent=0).replace("\n", ""))
            else:
                values.append(v)

        self.db.insert_update_delete(insert_sql, [values])

    def update_testreport(self, report_id, report):
        pass


if __name__ == '__main__':
    pass
