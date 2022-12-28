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
from testrunner.global_context import GlobalContext
from demo.page_objects.login_page import LoginPage
from demo.page_objects.buckets_page import BucketsPage


class TestCaseUICreateBucket(object):

    time_str = GlobalContext.get_time_str()

    @pytest.mark.P0
    def test_create_bucket_001(self):
        """创建桶成功"""
        bucket_name = f'auto_{self.time_str}'
        LoginPage().login_success()
        BucketsPage().create_bucket(bucket_name)


if __name__ == '__main__':
    pass
