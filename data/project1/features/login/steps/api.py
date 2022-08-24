#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:api
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
from testrunner.core.operator import ApiStep, RunRequest


def login(user="admin", password="Pass@0301"):
    return ApiStep(RunRequest("登录")
            .with_description("设置cookies（正常值）")
            .get("http://127.0.0.1:8000/api/user_auth/jwt/token/v2")
            .with_params(**{"username": user, "password": password})
            .with_headers(**{})
            .with_cookies(**{})
            .with_data({})
            .extract()
            .with_jsonpath("$..data.token", "token")
            .validate().assert_length_greater_than("$..data.token", 1, message="token为空")
            )


if __name__ == '__main__':
    pass
