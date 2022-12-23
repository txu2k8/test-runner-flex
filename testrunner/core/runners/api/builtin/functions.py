#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:functions.py
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 预置常用函数，测试设计中直接调用
"""
import time
import datetime
import arrow
import calendar
import random
import string
from typing import List, Tuple, Text
from faker import Faker

from testrunner.core.runners.exceptions import ParamsError


faker = Faker(['zh_CN'])


def gen_random_string(str_len: int) -> str:
    """
    生成指定长度的随机字符串
    :param str_len: 字符串长度
    :return:
    """
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(str_len)
    )


def get_timestamp(str_len: int = 13) -> str:
    """
    获取时间戳，长度 0~16
    :param str_len: 时间戳长度，0~16，默认13
    :return:
    """
    if isinstance(str_len, int) and 0 < str_len < 17:
        return str(time.time()).replace(".", "")[:str_len]

    raise ParamsError("timestamp length can only between 0 and 16.")


def get_current_date(fmt: str = "%Y-%m-%d") -> str:
    """
    获取当前时间，格式自定义，默认：年-月-日
    :param fmt: 时间格式
    :return:
    """
    return datetime.datetime.now().strftime(fmt)


def sleep(n_secs: int):
    """
    sleep n 秒
    :param n_secs: sleep时间，单位：秒
    :return:
    """
    time.sleep(n_secs)


def uuid4() -> str:
    """0d1072bf-5d0f-4216-bea6-4df9deb8dae9"""
    return faker.uuid4()


def uuid4_list(n=1) -> List[Text]:
    """['1727b3fa-1fc4-4849-aeb3-60790624fcbe']"""
    return [faker.uuid4() for _ in range(n)]


def name() -> str:
    """生成模拟姓名（人名，中文），如：fake_吴秀荣"""
    return "fake_" + faker.name()


def phone_number() -> str:
    """生成模拟电话号码，如：13766160522 """
    return faker.phone_number()


def city() -> str:
    """生成模拟城市名，如：惠州县"""
    return faker.city()


def address() -> str:
    """生成模拟地址，如：辽宁省成都市静安西安路G座33"""
    return faker.address()


def time_stamp_int() -> int:
    """生成时间戳，如：1640313339"""
    return int(time.time())


def time_stamp_str() -> str:
    """生成时间戳，如：1640313339"""
    return str(int(time.time()))


def now_strftime(fmt="%Y-%m-%d") -> str:
    """生成当前时间，fmt自定义，如：%Y-%m-%d ==> 2021-11-30"""
    return datetime.datetime.now().strftime(fmt)


def date_now_str() -> str:
    """生成当前日期，如：2021-11-30"""
    return datetime.datetime.now().strftime(fmt="%Y-%m-%d")


def datetime_now_str() -> str:
    """生成当前时间，如：2021-12-22 15:58:17"""
    return datetime.datetime.now().strftime(fmt="%Y-%m-%d %H:%M:%S")


def date_yesterday_str() -> str:
    """获取昨日日期，如：2021-12-22"""
    return arrow.now().shift(days=-1).format("YYYY-MM-DD")


def date_month_ago_str() -> str:
    """获取一个月前的日期，如：2021-11-22"""
    return arrow.now().shift(months=-1).format("YYYY-MM-DD")


def last_week_date() -> Tuple[str, str]:
    """获取上周的日期，（星期一日期，星期日日期），如：["2021-12-13","2021-12-19"]"""
    weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
    mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
    sun = mon.shift(days=6)
    return mon.format("YYYY-MM-DD"), sun.format("YYYY-MM-DD")


def last_week_monday() -> str:
    """获取上周星期一日期，如：2021-12-13"""
    weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
    mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
    return mon.format("YYYY-MM-DD")


def last_week_sunday() -> str:
    """获取上周星期日日期，如：2021-12-19"""
    weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
    mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
    sun = mon.shift(days=6)
    return sun.format("YYYY-MM-DD")


def last_month_date() -> datetime.date:
    """获取上月的日期，返回数据格式为datetime.date，获取年：obj.year"""
    return arrow.now().shift(months=-1).date()


def last_month_start_end_date() -> Tuple[str, str]:
    """获取上月的日期，（月初日期，月底日期），如：["2021-12-01","2021-12-31"]"""
    date_obj = last_month_date()
    year, month = date_obj.year, date_obj.month
    end = calendar.monthrange(int(year), int(month))[1]
    start_date = '%s-%s-01' % (year, month)
    end_date = '%s-%s-%s' % (year, month, end)
    return start_date, end_date


def last_month_start_date():
    """获取上月的开始日期，如：2021-12-01"""
    date_obj = last_month_date()
    year, month = date_obj.year, date_obj.month
    start_date = '%s-%s-01' % (year, month)
    return start_date


def last_month_end_date():
    """获取上月的结束日期，如：2021-12-31"""
    date_obj = last_month_date()
    year, month = date_obj.year, date_obj.month
    end = calendar.monthrange(int(year), int(month))[1]
    end_date = '%s-%s-%s' % (year, month, end)
    return end_date


if __name__ == '__main__':
    pass
