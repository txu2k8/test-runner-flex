#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 全局配置，及配置文件读写方法。
"""
from testrunner.config.globals import *
from testrunner.config.cf_xml import ConfigXml
from testrunner.config.cf_yaml import read_yaml
from testrunner.config.cf_ini import ConfigIni, read_ini

__all__ = [
    "VERSION", "AUTHOR",
    # 基本方法
    "read_yaml", "ConfigIni", "ConfigXml",
    # 全局内存变量-读写
    "set_global_value", "get_global_value", "get_global_dict",
    # 环境变量-读写
    "set_os_environ", "unset_os_environ", "get_os_environment",
    # 全局常量
    "BASE_DIR", "TESTCASE_DIR", "DATA_DIR", "LOG_DIR", "REPORT_DIR",  # 全局路径 dir
    "global_cf",
    "DB_INFO",  # 数据库配置
    "TIME_STR",  # 时间戳
    "FILE_LOG_LEVEL", "CONSOLE_LOG_LEVEL", "MAX_ROTATION", "MAX_RETENTION",  # 日志配置
]


if __name__ == '__main__':
    pass
