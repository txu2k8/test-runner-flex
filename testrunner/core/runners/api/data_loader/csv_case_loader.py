#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:csv_loader
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: TODO
"""


class CSVCaseLoader(object):
    """
    读取 excel/csv 内容，返回用例数据：
    字典列表（list[dict1,dict2]）
    """

    def __init__(self, file_path, book=""):
        self.file_path = file_path
        self.book = book

    def get_csv_data(self):
        return []


if __name__ == '__main__':
    pass
