#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:meta_class
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description: 利用元类批量给所有继承类增加装饰器
"""
import allure
import six
import types
import inspect
import unittest
from functools import wraps
from collections import OrderedDict
from loguru import logger


def step(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        logger.info(f'📌 {func.__doc__}')
        with allure.step(title=func.__doc__):
            return func(*args, **kwargs)

    return wrap


class MetaClass(type):
    func = None

    def __new__(cls, name, bases, attrs):
        """
        name:类名,
        bases:类所继承的父类
        attrs:类所有的属性
        """
        cls.func = step  # attrs.get('meta_decoator')
        assert inspect.isfunction(cls.func), '传入的meta装饰器不正确'
        # 在类生成的时候做一些手脚
        new_attrs = cls.options(bases, attrs)
        return super().__new__(cls, name, bases, new_attrs)

    @classmethod
    def options(cls, bases, attrs):
        new_attrs = OrderedDict()
        # 循环自己的所有属性
        for key, value in attrs.items():
            # 对各种类型的方法进行分别处理
            if hasattr(value, '__func__') or isinstance(value, types.FunctionType):
                if isinstance(value, staticmethod):
                    new_attrs[key] = staticmethod(cls.func(value.__func__))
                elif isinstance(value, classmethod):
                    new_attrs[key] = classmethod(cls.func(value.__func__))
                elif isinstance(value, property):
                    new_attrs[key] = property(fget=cls.func(value.fget), fset=cls.func(value.fset),
                                              fdel=cls.func(value.fdel), doc=value.__doc__)
                elif not key.startswith('__'):
                    new_attrs[key] = cls.func(value)
                continue
            new_attrs[key] = value
        # 循环所有继承类
        for base in bases:
            if isinstance(base, unittest.TestCase):
                continue
            for key, value in base.__dict__.items():
                if key not in new_attrs:
                    if hasattr(value, '__func__') or isinstance(value, types.FunctionType):
                        if key.startswith('addTypeEqualityFunc'):
                            continue
                        elif isinstance(value, staticmethod):
                            new_attrs[key] = staticmethod(cls.func(value.__func__))
                        elif isinstance(value, classmethod):
                            new_attrs[key] = classmethod(step(value.__func__))
                        elif isinstance(value, property):
                            new_attrs[key] = property(fget=cls.func(value.fget), fset=cls.func(value.fset),
                                                      fdel=cls.func(value.fdel), doc=value.__doc__)
                        elif not key.startswith('__'):
                            new_attrs[key] = step(value)
                        continue
                    new_attrs[key] = value

        return new_attrs


# from unittest import TestCase
#
#
# class obj(TestCase):
#
#     def __init__(self):
#         print('obj.__init__')
#
#     def one(self):
#         """DDDDDDDDDDD"""
#         print('obj.one')
#         self.assertFalse(0)
#
#
# # @six.add_metaclass(MetaClass)
# class obj1(obj, metaclass=MetaClass):
#     # 只要继承类中有meta_decoator属性,这个属性的方法就会自动装饰下面所有的方法
#     # 包括类属性,实例属性,property属性,静态属性
#     # meta_decoator = step
#     aa = 1
#
#     @classmethod
#     def three(cls):
#         """步骤描述 3333"""
#         print('obj1.three')
#
#     @staticmethod
#     def four():
#         """步骤描述 444444444"""
#         print('obj1.four')
#
#     def two(self):
#         """步骤描述 22222"""
#         print(self.pro)
#         print('obj1.two')
#         self.one()
#
#     @property
#     def pro(self):
#         return 1
#
#
# if __name__ == '__main__':
#     b = obj1()
#     b.one()
#     b.two()
#     b.three()
#     b.four()
#
#     a = obj1
#     a.four()
#     a.three()
