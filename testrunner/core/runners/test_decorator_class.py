#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:test_decorator_class
@time:2022/12/29
@email:tao.xu2008@outlook.com
@description: 
"""
from testrunner.core.runners.decorator_class import AllureStepDecorator


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

