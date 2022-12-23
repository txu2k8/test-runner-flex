#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 测试用例数据加载，读取数据并解析
    1. xmind - 支持
    2. csv/xls - 暂不支持
    3. yaml - 暂不支持
"""
from .case_loader import CaseLoader, load_testcase


__all__ = [
    'CaseLoader', 'load_testcase'
]


if __name__ == '__main__':
    pass
