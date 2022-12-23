#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:exceptions
@time:2022/12/20
@email:tao.xu2008@outlook.com
@description: 自定义异常
"""


class RunnerException(Exception):
    """
    Base exception.
    """

    def __init__(self, msg: str = None, screen: str = None, stacktrace: str = None):
        self.msg = msg
        self.screen = screen
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = f"Message: {self.msg}\n"
        if self.screen is not None:
            exception_msg += "Screenshot: available via screen\n"
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += f"Stacktrace:\n{stacktrace}"
        return exception_msg


class NotFindElementError(RunnerException):
    """
    No element errors were found
    """
    pass


class TestFixtureRunError(RunnerException):
    """
    Test fixture run error
    """
    pass


class FileTypeError(RunnerException):
    """
    Data file type error
    """
    pass


if __name__ == '__main__':
    pass
