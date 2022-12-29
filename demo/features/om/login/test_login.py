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
import allure
from testrunner import MetaClass, dynamic
from demo.page_objects.login_page import LoginPage, teardown_logout


@allure.epic("OM")
@allure.feature("登录")
@allure.story("登录")
@allure.suite("登录")
class TestCaseUILogin(metaclass=MetaClass):
    meta_decoator = dynamic
    login_page = LoginPage()

    @pytest.mark.CI
    def test_login_001(self, teardown_logout):
        """正常登录成功"""
        self.login_page.login_success()

    @pytest.mark.P1
    def test_login_002(self):
        """使用错误用户名登录，失败"""
        self.login_page.login_with_err_user()

    @pytest.mark.P1
    def test_login_003(self):
        """使用错误用户名密码登录，失败"""
        self.login_page.login_with_err_pass()

    @pytest.mark.P2
    def test_login_004(self):
        """使用错误用户名+密码登录，失败"""
        self.login_page.login_with_err_user_pass()


if __name__ == '__main__':
    pass
