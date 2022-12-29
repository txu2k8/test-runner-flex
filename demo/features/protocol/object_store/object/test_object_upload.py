#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:object
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 对象上传
"""
import pytest
import allure
from testrunner import MetaClass, dynamic
from testrunner.global_context import GlobalContext
from demo.page_objects.login_page import LoginPage
from demo.page_objects.buckets_page import BucketsPage


@allure.epic("协议")
@allure.feature("对象存储")
@allure.story("对象管理")
@allure.suite("上传对象")
class TestCaseUploadObject(metaclass=MetaClass):
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
    def test_upload_object_001(self):
        """上传对象成功"""
        bucket_name = f'auto_{self.time_str}'
        self.bucket_page.create_bucket(bucket_name)


if __name__ == '__main__':
    pass
