#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:login_page
@time:2022/12/23
@email:tao.xu2008@outlook.com
@description: 
"""
from testrunner import WebRunner
from testrunner.global_context import GlobalContext


class LoginPage(WebRunner):
    """登录页面"""

    def __init__(self):
        super().__init__()
        self.env = GlobalContext.env

    def login_success(self):
        self.open(self.env.web_url)
        self.type(id_="accessKey", text=self.env.web_user, enter=False)
        self.type(id_="secretKey", text=self.env.web_pass, enter=False)
        self.click(id_="do-login")

        self.assertInUrl("buckets")
        self.assertInTitle("MinIO Console")

    def login_with_err_user(self):
        pass

    def login_with_err_pass(self):
        pass

    def login_with_err_user_pass(self):
        pass


if __name__ == '__main__':
    pass
