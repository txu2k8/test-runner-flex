#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py
@time:2022/08/24
@email:tao.xu2008@outlook.com
@description:
"""
# from testrunner.global_context import GlobalContext
from testrunner.core.runners.api.step import ApiStep, RunRequest
from testrunner.core.runners.web import WebRunner, WebDriver, WebElement

__version__ = '0.0.1'
__all__ = [
    # "GlobalContext",
    "ApiStep", "RunRequest",
    "WebRunner", "WebDriver", "WebElement",  # WEB UI 测试
]


if __name__ == '__main__':
    pass
