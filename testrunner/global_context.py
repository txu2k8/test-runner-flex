#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:global_context.py
@time:2022/12/26
@email:tao.xu2008@outlook.com
@description: 
"""
import os
from loguru import logger
from threading import local

from testrunner.base.models import TestConf, TestEnv
from testrunner.config.cf_xml import ConfigXml
from testrunner.config.globals import TIME_STR, FILE_LOG_LEVEL, MAX_ROTATION, TESTCASE_DIR, LOG_DIR, REPORT_DIR
from testrunner.utils.util import zfill


class GlobalContext:
    """全局上下文配置参数"""

    def __init__(self):
        pass

    driver = None  # 浏览器 driver
    timeout = 10

    # 配置文件/输入参数 解析
    test_conf_path = ""
    test_conf: TestConf = None
    env: TestEnv = None

    # 数据库初始化
    report_id = 1
    zfill_report_id = zfill(report_id)

    # 输出配置
    debug = False
    log_level = FILE_LOG_LEVEL
    max_rotation = MAX_ROTATION

    current_local = local()  # local cache

    @classmethod
    def set_env(cls, env):
        cls.env = env

    @classmethod
    def get_env(cls):
        return cls.env

    @classmethod
    def del_env(cls):
        del cls.env

    @classmethod
    def set_global_cache(cls, key, value):
        if not hasattr(cls.current_local, "glb_cache") or cls.current_local.glb_cache is None:
            cls.current_local.glb_cache = {}
        cls.current_local.glb_cache[key] = value

    @classmethod
    def get_global_cache(cls, key):
        if not hasattr(cls.current_local, "glb_cache") or cls.current_local.glb_cache is None:
            return None
        return cls.current_local.glb_cache.get(key)

    @classmethod
    def del_global_cache(cls):
        if not hasattr(cls.current_local, "glb_cache") or cls.current_local.glb_cache is None:
            return None
        rc_l = cls.current_local
        del rc_l.glb_cache

    @classmethod
    def get_test_conf(cls) -> TestConf:
        """
        xml测试配置文件-解析
        :return:
        """
        if not hasattr(cls.current_local, "test_conf") or cls.current_local.test_conf is None:
            if cls.test_conf_path:
                logger.info("XML配置文件参数解析...")
                cx = ConfigXml(cls.test_conf_path)
                cls.test_conf = cx.parse_test_conf()
            else:
                logger.info("测试输入参数解析... TODO")  # TODO
                raise Exception("输入参数解析暂不支持，请输入XML配置文件路径！")
        return cls.test_conf

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
