#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description: Web自动化测试
"""
from testrunner.core.runners.web.webdriver import WebDriver, WebElement
from testrunner.core.runners.web.runner import WebRunner


__all__ = ["WebRunner", "WebDriver", "WebElement"]


if __name__ == '__main__':
    pass
