#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:cf_yaml
@time:2022/08/24
@email:tao.xu2008@outlook.com
@description:
"""
import yaml
import codecs


def read_yaml(file_path, yaml_loader=yaml.FullLoader):
    """
    读取yaml文件内容，返回字典
    :param file_path:
    :param yaml_loader:
    :return:
    """
    with codecs.open(file_path, 'r', 'utf-8') as f:
        data = yaml.load(f, Loader=yaml_loader)
    return data


if __name__ == '__main__':
    pass
