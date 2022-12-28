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
from demo.page_objects.login_page import LoginPage


@allure.suite("登录")
class TestCaseUILogin(object):

    @pytest.mark.P0
    @allure.tag("P0")
    def test_login_001(self):
        """正常登录成功"""
        LoginPage().login_success()


if __name__ == '__main__':
    pass
