#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:db_init
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
from loguru import logger

from testrunner.config import DB_INFO
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
            db_path = DB_INFO.get('DB_PATH')  # os.path.abspath(os.path.join(root_dir, '../db.sqlite3'))
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
        CREATE TABLE IF NOT EXISTS "api_test_testreport"
        :return:
        """
        sql = '''
        CREATE TABLE IF NOT EXISTS "{}" (
          "update_time" datetime,
          "delete_time" datetime,
          "is_delete" bool NOT NULL,
          "description" varchar(4096),
          "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
          "create_time" datetime NOT NULL,
          "build_type" varchar(20) NOT NULL,
          "build_status" varchar(50) NOT NULL,
          "status" bool NOT NULL,
          "duration" integer NOT NULL,
          "case_total" integer NOT NULL,
          "case_passed" integer NOT NULL,
          "case_failed" integer NOT NULL,
          "case_skipped" integer NOT NULL,
          "case_error" integer NOT NULL,
          "case_pass_rate" real NOT NULL,
          "case_failed_list" text NOT NULL,
          "case_error_list" text NOT NULL,
          "case_skipped_list" text NOT NULL,
          "step_total" integer NOT NULL,
          "step_passed" integer NOT NULL,
          "step_failed" integer NOT NULL,
          "step_skipped" integer NOT NULL,
          "step_error" integer NOT NULL,
          "step_pass_rate" real NOT NULL,
          "broken_apis" text NOT NULL,
          "step_failed_list" text NOT NULL,
          "step_error_list" text NOT NULL,
          "step_skipped_list" text NOT NULL,
          "client" varchar(50),
          "log_path" text,
          "html_report_path" text,
          "allure_xml_path" text,
          "allure_url" varchar(500),
          "jenkins_job_name" varchar(100),
          "jenkins_build_number" integer,
          "env_id" integer,
          FOREIGN KEY ("env_id") REFERENCES "api_test_globalenv" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
           ((JSON_VALID("case_failed_list") OR "case_failed_list" IS NULL)),
           ((JSON_VALID("case_error_list") OR "case_error_list" IS NULL)),
           ((JSON_VALID("case_skipped_list") OR "case_skipped_list" IS NULL)),
           ((JSON_VALID("broken_apis") OR "broken_apis" IS NULL)),
           ((JSON_VALID("step_failed_list") OR "step_failed_list" IS NULL)),
           ((JSON_VALID("step_error_list") OR "step_error_list" IS NULL)),
           ((JSON_VALID("step_skipped_list") OR "step_skipped_list" IS NULL))
        )
        '''.format(self.table_name)

        logger.info("CREATE TABLE IF NOT EXISTS \"{}\" ...".format(self.table_name))
        self.db.create_table(sql)
        return True

    def insert_init_testreport(self):
        insert_sql = '''INSERT INTO {} values (?, ?, ?, ?, ?, ?)'''.format(self.table_name)
        data = [(1, 'Hongten', 'boy', 20, 'guangzhou', '13423****62'),
                (2, 'Tom', 'boy', 22, 'guangzhou', '15423****63'),
                (3, 'Jake', 'girl', 18, 'guangzhou', '18823****87'),
                (4, 'Cate', 'girl', 21, 'guangzhou', '14323****32')]
        self.db.insert_update_delete(insert_sql, data)


if __name__ == '__main__':
    pass
