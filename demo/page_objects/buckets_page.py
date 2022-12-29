#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:buckets_page
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description: 桶页面 操作步骤
"""
from testrunner import WebRunner
from testrunner.global_context import GlobalContext
from testrunner import MetaClass


class BucketsPage(WebRunner, metaclass=MetaClass):
    """桶页面"""
    env = GlobalContext.env
    bucket_url = env.web_url + "/buckets"

    def refresh_bucket(self):
        """刷新桶列表"""
        self.open(self.bucket_url)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div[1]/div[2]/span[4]')

    def _enter_create_bucket(self):
        """进入”创建桶“页面"""
        self.open(self.bucket_url)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div[1]/div[2]/span[5]')
        self.assertInUrl("add-bucket")

    def _create_bucket_input(self, bucket_name):
        """创建桶输入信息"""
        self.type(xpath='//*[@id="root"]/div/main/div[3]/div/div/div/div[1]/form/div[1]/div[1]/div/div/div/div',
                  text=bucket_name, enter=False)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div/div[1]/form/div[2]/button[2]')

    def create_bucket(self, bucket_name):
        """创建一个桶"""
        self._enter_create_bucket()
        self._create_bucket_input(bucket_name)
        self.assertInUrl(bucket_name)


if __name__ == '__main__':
    pass
