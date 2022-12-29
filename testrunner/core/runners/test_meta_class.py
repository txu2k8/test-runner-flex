#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_meta_class
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 
"""
import six
from testrunner.core.runners.meta_class import MetaClass, step


class obj(object):

    def __init__(self):
        print('obj.__init__')

    def one(self):
        """步骤描述 1111111"""
        print('obj.one')


# @six.add_metaclass(MetaClass)
class obj1(obj, metaclass=MetaClass):
    # 只要继承类中有meta_decoator属性,这个属性的方法就会自动装饰下面所有的方法
    # 包括类属性,实例属性,property属性,静态属性
    meta_decoator = step

    @classmethod
    def three(cls):
        """步骤描述 3333"""
        print('obj1.three')

    @staticmethod
    def four():
        """步骤描述 444444444"""
        print('obj1.four')

    def two(self):
        """步骤描述 22222"""
        print(self.pro)
        print('obj1.two')
        self.one()

    @property
    def pro(self):
        return 1


if __name__ == '__main__':
    b = obj1()
    b.one()
    b.two()
    b.three()
    b.four()

    a = obj1
    a.four()
    a.three()
