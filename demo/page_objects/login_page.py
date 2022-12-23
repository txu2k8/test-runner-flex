#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:login_page
@time:2022/12/23
@email:tao.xu2008@outlook.com
@description: 
"""
from testrunner import Settings, WebDriver


class LoginPage(WebDriver):
    """登录页面"""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.env = settings.env

    def login(self):
        self.open(self.env["web_url"])
        self.type(id_="accessKey", text=self.env["RootUser"], enter=False)
        self.type(id_="secretKey", text=self.env["RootPass"], enter=False)
        self.click(id_="do-login")


if __name__ == '__main__':
    pass
