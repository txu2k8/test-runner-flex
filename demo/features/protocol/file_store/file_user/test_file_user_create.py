#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_file_user_create
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 文件用户 - 创建
"""
import pytest
import allure
from testrunner import MetaClass, dynamic
from demo.page_objects.login_page import LoginPage, teardown_logout


@allure.epic("协议")
@allure.feature("文件存储")
@allure.story("文件用户")
@allure.suite("本地用户/创建")
class TestCaseCreateLocalUser(metaclass=MetaClass):
    meta_decoator = dynamic
    login_page = LoginPage()

    @pytest.mark.CI
    def test_create_loacl_user_001(self, teardown_logout):
        """文件存储-正常创建本地用户成功"""
        self.login_page.login_success()


if __name__ == '__main__':
    pass
