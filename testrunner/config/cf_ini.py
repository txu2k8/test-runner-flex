#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:cf_rw
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: ini 配置文件读写
"""
import configparser


# 读取配置文件
def read_ini(file_path, section, option):
    """
    读取ini配置文件section->option的值，如：
    [TEST]
    url = https://xxxxx.com
    :param file_path:
    :param section: --TEST
    :param option: --url
    :return:
    """
    conf = configparser.ConfigParser()
    conf.read(file_path)
    return conf.get(section, option)


def read_ini_section(file_path, section):
    """
    读取ini配置文件section下所有键值对，返回字典
    :param file_path:
    :param section:
    :return:
    """
    conf = configparser.ConfigParser()
    conf.read(file_path)
    return dict(conf.items(section))


class ConfigIni(object):
    """读、写ini配置文件"""
    def __init__(self, file_path):
        """
        生成配置文件对象并读取配置文件
        :param file_path: 配置文件的绝对路径
        """
        self.file_path = file_path
        # 定义配置文件对象，并读取配置文件
        self.cf = configparser.ConfigParser()
        self.cf.read(file_path, encoding='utf-8')

    # 获取字符串的配置内容
    def get_str(self, section, option):
        """
        获取配置文件的value值
        :param section: 配置文件中section的值
        :param option: 配置文件中option的值
        :return value: 返回value的值
        """
        return self.cf.get(section, option)

    # 获取int数字型内容
    def get_int(self, section, option):
        """
        获取配置文件的value值
        :param section: 配置文件中section的值
        :param option: 配置文件中option的值
        :return value:  返回value的值
        """
        return self.cf.getint(section, option)

    # 获取float型数字内容
    def get_float(self, section, option):
        """
        获取配置文件的value值
        :param section: 配置文件中section的值
        :param option: 配置文件中option的值
        :return value:  返回value的值
        """
        return self.cf.getfloat(section, option)

    # 获取布尔值的返回内容
    def get_boolean(self, section, option):
        """
        获取配置文件的value值
        :param section: 配置文件中section的值
        :param option: 配置文件中option的值
        :return value:  返回value的值
        """
        return self.cf.getboolean(section, option)

    def get_kvs(self, section):
        return dict(self.cf.items(section))

    # 修改配置文件的value值
    def set_value(self, section, option, value):
        """
        修改value的值
        :param section: 配置文件中section的值
        :param option: 配置文件中option的值
        :param value: 修改value的值
        :return:
        """
        # python内存先修改值
        self.cf.set(section, option, value)
        # 需要通过文件的方式写入才行，不然实体文件的值不会改变
        with open(self.file_path, "w+") as f:
            self.cf.write(f)
        return True


if __name__ == '__main__':
    pass
