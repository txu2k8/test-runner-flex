#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_home
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 首页显示验证
"""
import pytest
import allure
from testrunner import MetaClass, dynamic
from demo.page_objects.login_page import LoginPage, teardown_logout


@allure.epic("OM")
@allure.feature("首页")
@allure.story("首页")
@allure.suite("首页")
class TestCaseHome(metaclass=MetaClass):
    meta_decoator = dynamic
    login_page = LoginPage()

    @pytest.mark.CI
    def test_home_001(self, teardown_logout):
        """正常登录成功"""
        self.login_page.login_success()


if __name__ == '__main__':
    pass
