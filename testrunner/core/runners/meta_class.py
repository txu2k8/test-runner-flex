#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:meta_class
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description: 利用元类批量给所有继承类增加装饰器
"""
import re
import allure
import types
import inspect
import unittest
from functools import wraps
from collections import OrderedDict
from loguru import logger
from testrunner.global_context import GlobalContext


def step(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        step_type = args[0].step_type
        step_desc = func.__doc__.split("\n")[0]
        step_id = GlobalContext.get_global_step_id()
        title = f'Step{step_id}：({step_type}){step_desc}'
        logger.info(f'🚩 {title}')
        with allure.step(title=title):
            GlobalContext.count_global_step_id()
            return func(*args, **kwargs)
    return wrap


def dynamic(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        case_desc = func.__doc__
        case_ids = re.findall(r"-?[0-9]\d*", func.__name__)
        case_id = case_ids[0] if case_ids else ''
        case_ids_str = ','.join(case_ids)
        logger.debug(f'📌 Case：{case_desc}')
        allure.dynamic.title(f'(ID:{case_ids_str}){case_desc}')
        allure.dynamic.description(case_desc)
        allure.dynamic.testcase(f"https://chandao.cn/zendao/testcase-view-{case_id}.html", f"禅道用例: {case_ids_str}")
        res = func(*args, **kwargs)
        GlobalContext.reset_step_id()
        return res
    return wrap


class MetaClass(type):
    func = None

    def __new__(cls, name, bases, attrs):
        """
        name:类名,
        bases:类所继承的父类
        attrs:类所有的属性
        """
        cls.func = attrs.get('meta_decoator') or step
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
                if key in ('setup', 'teardown', 'setup_class', 'teardown_class'):
                    continue
                elif isinstance(value, staticmethod):
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
                        if key in ('setup', 'teardown', 'setup_class', 'teardown_class'):
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


if __name__ == '__main__':
    pass
