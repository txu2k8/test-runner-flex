#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:random_func
@time:2022/12/20
@email:tao.xu2008@outlook.com
@description: 生成随机数据的方法
"""
import time


def get_timestamp(level="second") -> str:
    """
    get now timestamp
    :return:
    """
    time_list = str(time.time()).split('.', maxsplit=1)
    if level == "second":
        return time_list[0]
    if level == "millisecond":
        return time_list[0] + time_list[1]

    return ""


if __name__ == '__main__':
    pass
