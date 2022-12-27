#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:log_init
@time:2022/09/06
@email:tao.xu2008@outlook.com
@description:
# 日志级别
Level	    value	Logger method
TRACE	    5	    logger.trace
DEBUG	    10	    logger.debug
INFO	    20	    logger.info
SUCCESS	    25	    logger.success
WARNING	    30	    logger.warning
ERROR	    40	    logger.error
CRITICAL	50	    logger.critical

info_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <4}</level> | <level>{message}</level>"
"""
import os
import sys
import atexit
from enum import Enum
from typing import Text
from loguru import logger

from testrunner.config import LOG_DIR, FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL, MAX_ROTATION, MAX_RETENTION


class LogLevelEnum(Text, Enum):
    """logger级别枚举"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"


class LogFormatEnum(Text, Enum):
    """logger format枚举"""
    MINI = "{message}"
    SIMPLE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | <level>{message}</level>"
    DEFAULT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | " \
              "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
              "- <level>{message}</level>"
    DETAIL = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <7}</level> | " \
             "<cyan>P{process}</cyan>:<cyan>T{thread}</cyan>:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> " \
             "- <level>{message}</level>"


def init_logger(prefix='test', loglevel=None):
    """
    初始化logger日志配置
    :param prefix:
    :param loglevel: 日志等级
    :return:
    """
    # 获取配置
    console_loglevel = CONSOLE_LOG_LEVEL
    console_format = LogFormatEnum.SIMPLE
    file_loglevel = FILE_LOG_LEVEL
    file_format = LogFormatEnum.SIMPLE
    if loglevel:
        if loglevel == LogLevelEnum.TRACE:
            console_loglevel = loglevel.value
            console_format = LogFormatEnum.DETAIL
            file_loglevel = loglevel.value
            file_format = LogFormatEnum.DETAIL
        elif loglevel == LogLevelEnum.DEBUG:
            console_loglevel = loglevel.value
            console_format = LogFormatEnum.DEFAULT
            file_loglevel = loglevel.value
            file_format = LogFormatEnum.DEFAULT

    # 删除默认
    logger.remove()

    # 新增级别
    logger.level('STEP', no=21, color='<blue><bold>')  # INFO < STEP < ERROR
    logger.level('DESC', no=52)  # CRITICAL < DESC，打印描述信息到所有日志文件

    # 初始化控制台配置 - CONSOLE_LOG_LEVEL
    logger.add(sys.stderr, level=console_loglevel, format=console_format)

    logger.info(LOG_DIR)
    # 初始化日志配置 -- all日志文件
    logger.add(
        os.path.join(LOG_DIR, '{time}'+'_{prefix}.log'.format(prefix=prefix)),
        rotation=MAX_ROTATION,  # '100 MB',
        retention=MAX_RETENTION,  # '30 days',
        enqueue=True,
        encoding="utf-8",
        level=file_loglevel,
        format=file_format,
        backtrace=True,
        diagnose=True
    )

    atexit.register(logger.remove)


if __name__ == '__main__':
    pass
