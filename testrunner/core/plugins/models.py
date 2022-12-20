#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:models
@time:2022/12/20
@email:tao.xu2008@outlook.com
@description: 数据模型
"""


class Settings:
    """定义测试配置信息"""
    driver = None  # 浏览器 driver
    timeout = 10
    debug = False
    base_url = None
    app_server = None
    app_info = None
    env = None
    api_data_url = None


class BrowserConfig:
    """定义浏览器配置信息"""
    NAME = None
    REPORT_PATH = None
    REPORT_TITLE = "Test Report"
    LOG_PATH = None


if __name__ == '__main__':
    pass
