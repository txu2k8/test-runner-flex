#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:buckets_page
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description: 
"""
from testrunner import WebRunner
from testrunner.global_context import GlobalContext


class BucketsPage(WebRunner):
    """桶页面"""

    def __init__(self):
        super().__init__()
        self.env = GlobalContext.env
        self.bucket_url = self.env.web_url + "/buckets"

    def refresh_bucket(self):
        self.open(self.bucket_url)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div[1]/div[2]/span[4]/button')

    def enter_create_bucket(self):
        self.open(self.bucket_url)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div[1]/div[2]/span[5]/button')
        self.assertInUrl("add-bucket")

    def create_bucket(self, bucket_name):
        self.enter_create_bucket()
        self.type(xpath='//*[@id="root"]/div/main/div[3]/div/div/div/div[1]/form/div[1]/div[1]/div/div/div/div',
                  text=bucket_name, enter=False)
        self.click(xpath='//*[@id="root"]/div/main/div[3]/div/div/div/div[1]/form/div[2]/button[2]')
        self.assertInUrl(bucket_name)


if __name__ == '__main__':
    pass
