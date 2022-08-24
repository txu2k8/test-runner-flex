#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:test_init
@time:2022/08/24
@email:tao.xu2008@outlook.com
@description: 测试session初始化
"""
import os
from loguru import logger
from testrunner.base.models import TestConf
from testrunner.config import *
from testrunner.utils.util import zfill


# 设置测试session基本数据
class TestSession(object):
    """根据测试配置文件/数据，初始化测试session"""
    def __init__(self, test_conf_path, *args, **kwargs):
        self.test_conf_path = test_conf_path
        # 配置文件/输入参数 解析
        self.test_conf = self.test_conf_parse()  # -> TestConf

        self.log_level = FILE_LOG_LEVEL
        self.max_rotation = MAX_ROTATION

        # 数据库初始化
        self.report_id = self.test_db_init()
        self.zfill_report_id = zfill(self.report_id)

    def test_conf_parse(self) -> TestConf:
        """
        xml测试配置文件-解析
        :return:
        """
        if self.test_conf_path:
            logger.info("XML配置文件参数解析...")
            cx = ConfigXml(self.test_conf_path)
            test_conf = cx.parse_test_conf()
        else:
            logger.info("测试输入参数解析... TODO")  # TODO
            raise Exception("输入参数解析暂不支持，请输入XML配置文件路径！")
        return test_conf

    def test_db_init(self):
        """数据库初始化、插入测试session数据到test_report表"""
        # TODO
        project_name = self.test_conf.project
        logger.info(project_name)
        # db = InitDB()
        # db.create_table_if_not_exist()
        # db.insert_init_testreport()

        report_id = 1
        return report_id

    @property
    def testcase_path(self):
        return os.path.join(TESTCASE_DIR, self.test_conf.project, 'test_{}'.format(self.zfill_report_id))

    @property
    def log_path(self):
        return os.path.join(
            LOG_DIR,
            self.test_conf.project,
            '{}-{}-message.log'.format(self.zfill_report_id, TIME_STR)
        )

    @property
    def html_report_path(self):
        return os.path.join(REPORT_DIR, self.test_conf.project, self.zfill_report_id, "html", "report.html")

    @property
    def xml_report_path(self):
        return os.path.join(REPORT_DIR, self.test_conf.project, self.zfill_report_id, "xml")


if __name__ == '__main__':
    pass
