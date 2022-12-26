#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:login_001
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
from demo.page_objects.login_page import LoginPage
from testrunner.config.cf_xml import ConfigXml

settings = None


class TestCaseUILogin(object):

    # @pytest.mark()
    def test_002_web(self):
        LoginPage().login_success()


if __name__ == '__main__':
    pass
