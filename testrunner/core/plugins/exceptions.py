#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:exceptions
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 自定义异常
"""
import traceback
from datetime import datetime
from functools import wraps

from loguru import logger


# 异常信息输出
def except_output(msg='异常描述'):
    # msg用于自定义函数的提示信息
    def except_execute(func):
        @wraps(func)
        def execept_print(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                sign = '=' * 60 + '\n'
                logger.error(f'{sign}>>>异常时间：\t{datetime.now()}\n>>>异常函数：\t{func.__name__}\n>>>{msg}：\t{e}')
                logger.error(f'{sign}{traceback.format_exc()}{sign}')
        return execept_print
    return except_execute


# =============== Failure异常: 标记用例失败 ===============
class MyBaseFailure(Exception):
    pass


class JSONPathError(MyBaseFailure):
    pass


class ParseTestsFailure(MyBaseFailure):
    pass


class ValidationFailure(AssertionError):
    pass


class StatusCodeValidationFailure(ValidationFailure):
    pass


class ExtractFailure(MyBaseFailure):
    pass


class SetupHooksFailure(MyBaseFailure):
    pass


class TeardownHooksFailure(MyBaseFailure):
    pass


# =============== Error异常: 标记用例故障 ===============


class MyBaseError(Exception):
    pass


class FileFormatError(MyBaseError):
    pass


class TestCaseFormatError(FileFormatError):
    pass


class TestSuiteFormatError(FileFormatError):
    pass


class ParamsError(MyBaseError):
    pass


class NotFoundError(MyBaseError):
    pass


class FileNotFound(FileNotFoundError, NotFoundError):
    pass


class FunctionNotFound(NotFoundError):
    pass


class VariableNotFound(NotFoundError):
    pass


class EnvNotFound(NotFoundError):
    pass


class CSVNotFound(NotFoundError):
    pass


class ApiNotFound(NotFoundError):
    pass


class TestCaseNotFound(NotFoundError):
    pass


class SummaryEmpty(MyBaseError):
    """test result summary data is empty"""


if __name__ == '__main__':
    pass
