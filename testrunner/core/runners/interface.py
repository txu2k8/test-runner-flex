#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:interface
@time:2022/12/26
@email:tao.xu2008@outlook.com
@description: runner接口
"""
from abc import ABC, abstractmethod


class RunnerInterface(ABC):
    """定义所有 工作流 需要实现的接口"""

    @abstractmethod
    def start_class(self, *args, **kwargs):
        """
        Hook method for setting up class fixture before running tests in the class.
        """
        pass

    def end_class(self):
        """
        Hook method for deconstructing the class fixture after running all tests in the class.
        """
        pass

    @classmethod
    @abstractmethod
    def setup_class(cls):
        cls().start_class()

    @classmethod
    @abstractmethod
    def teardown_class(cls):
        cls().end_class()

    @abstractmethod
    def start(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        pass

    @abstractmethod
    def end(self):
        """
        Hook method for deconstructing the test fixture after testing it.
        """
        pass

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def teardown(self):
        pass


if __name__ == '__main__':
    pass
