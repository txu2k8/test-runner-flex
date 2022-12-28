#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:decorator_class
@time:2022/12/28
@email:tao.xu2008@outlook.com
@description: 
"""
import functools
import allure
from loguru import logger


class DecorateClass(object):
    def decorate(self):
        for name, fn in self.iter():
            if callable(fn):
                self.operate(name, fn)


class AllureStepDecorator(DecorateClass):
    def __init__(self, obj):
        self.obj = obj

    def iter(self):
        return [(name, getattr(self.obj, name)) for name in dir(self.obj) if not name.startswith('_')]

    def operate(self, name, fn):
        @functools.wraps(fn)
        def step(*args, **kv):
            logger.info(f'🔖   {fn.__doc__}')
            with allure.step(title=fn.__doc__):
                return fn(*args, **kv)

        setattr(self.obj, name, step)


class mylocker:
    def __init__(self):
        print("mylocker.__init__() called.")

    def acquire(self):
        print("mylocker.acquire() called.")

    def release(self):
        print("  mylocker.unlock() called.")


class Foo(object):
    def __init__(self):
        # Enable one or more decorators for each method:
        AllureStepDecorator(self).decorate()

    def interface1(self):
        """interface1"""
        print(" interface1() called.")

    def interface2(self):
        """interface2"""
        print(" interface2() called.")

    def _interface3(self):
        """_interface3"""
        print("_interface3() called.")


if __name__ == '__main__':
    obj = Foo()
    obj.interface1()
    obj.interface2()
    obj.interface1()
    obj.interface2()
    obj._interface3()
    print(obj.interface1.__name__)
