#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:case
@time:2022/12/20
@email:tao.xu2008@outlook.com
@description: 测试用例模板
"""
from testrunner.core.plugins.web import WebDriver
from testrunner.core.plugins.api import ApiRunner
from testrunner.core.plugins.command import CMDRunner


class TestCase(WebDriver, ApiRunner, CMDRunner):
    """TestCase class"""

    def start_class(self):
        """
        Hook method for setting up class fixture before running tests in the class.
        """
        pass

    def end_class(self):
        """
        Hook method for deconstructing the class fixture after running all tests in the class.
        """
        pass

    @classmethod
    def setup_class(cls):
        cls().start_class()

    @classmethod
    def teardown_class(cls):
        cls().end_class()

    def start(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        pass

    def end(self):
        """
        Hook method for deconstructing the test fixture after testing it.
        """
        pass

    def setup(self):
        self.images = []
        self.start()

    def teardown(self):
        self.end()


if __name__ == '__main__':
    pass
