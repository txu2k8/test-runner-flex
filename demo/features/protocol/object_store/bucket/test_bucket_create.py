#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_bucket_create
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description:
"""
import pytest
import allure
from testrunner import MetaClass, dynamic
from testrunner.global_context import GlobalContext
from demo.page_objects.login_page import LoginPage
from demo.page_objects.buckets_page import BucketsPage


@allure.epic("协议")
@allure.feature("对象存储")
@allure.story("桶管理")
@allure.suite("创建桶")
class TestCaseCreateBucket(metaclass=MetaClass):
    meta_decoator = dynamic
    time_str = GlobalContext.get_time_str()
    login_page = LoginPage()
    bucket_page = BucketsPage()

    @classmethod
    def setup_class(cls):
        cls.login_page.login_success()

    @classmethod
    def teardown_class(cls):
        cls.login_page.logout()

    @pytest.mark.P0
    def test_create_bucket_001(self):
        """创建桶成功"""
        bucket_name = f'auto_{self.time_str}'
        self.bucket_page.create_bucket(bucket_name)


if __name__ == '__main__':
    pass
