#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:utils
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description:
"""

import os
import re
import shutil
import socket
import glob
import time
import json
import collections
import itertools
import uuid
from multiprocessing import Queue
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
from typing import Dict, List, Any

from loguru import logger
from pypinyin import lazy_pinyin


def json_loads(content: str):
    """加载json字符串为python object"""
    try:
        return json.loads(content, strict=False)
    except json.JSONDecodeError as e:
        err_msg = "JSONDecodeError: JSON Content: {}\n{}".format(content, str(e))
        logger.error(err_msg)
        # return {}
        raise Exception(err_msg)


def json_dumps(d):
    """python object序列化为json格式字符串"""
    try:
        return json.dumps(d, indent=2, ensure_ascii=False)
    except Exception as e:
        err_msg = "Object: {}\n{}".format(d, str(e))
        logger.error(err_msg)
        raise Exception(err_msg)


def is_contains_zh(content: str):
    """
    检查整个字符串是否包含中文
    :param content: 需要检查的字符串
    :return: bool
    """
    if content is None:
        content = ""
    if not isinstance(content, str):
        content = str(content)
    for ch in content:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def select_zh_item(content_list: list) -> str:
    """
    选择字符串列表中包含中文的字符串，如没有，返回第一个元素
    :param content_list:
    :return:
    """
    for string in content_list:
        if is_contains_zh(string):
            return string
    else:
        return content_list[0]


def to_safe_name(content: str):
    """
    中文转换为拼音，然后替换字符串中非字母、数字、下划线的字符为下划线，转换小写
    :param content: 原始字符串
    :return: 小写字母、数字、下划线组成的字符串
    """
    return str(re.sub("[^a-zA-Z0-9_]+", "", '_'.join(lazy_pinyin(content)))).lower()


def to_class_name(content: str):
    """
    中文转拼音，删除字符串中非字母、数字、下划线的字符，单词首字母大小，如："class-mall goods" --> ClassMallGoods
    :param content: 原始字符串
    :return: 字母、数字组合的字符串，驼峰格式
    """
    if is_contains_zh(content):
        content = '_'.join(lazy_pinyin(content)).title()
    if ' ' in content:
        content = content.title().replace(' ', '')
    return str(re.sub("[^a-zA-Z0-9]+", "", content))


def seconds_to_hms(seconds: int) -> str:
    """
    秒数转换为字符串 "时:分:秒"
    :param seconds:
    :return:时:分:秒，如 3:40:33
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def zfill(number, width=6):
    """
    转换数字为字符串，并以’0‘填充左侧
    :param number:
    :param width: 最小宽度，如实际数字小于最小宽度，左侧填0
    :return: str, __zfill(123, 6) -> '000123'
    """
    return str(number).zfill(width)


def omit_long_data(body, omit_len=512):
    """
    omit too long str/bytes  省略过长字符串
    :param body:
    :param omit_len:
    :return:
    """
    if not isinstance(body, (str, bytes)):
        return body

    body_len = len(body)
    if body_len <= omit_len:
        return body

    omitted_body = body[0:omit_len]

    appendix_str = f" ... OMITTED {body_len - omit_len} CHARACTORS ..."
    if isinstance(body, bytes):
        appendix_str = appendix_str.encode("utf-8")

    return omitted_body + appendix_str


def print_info(info_mapping: dict):
    """
    格式化输出映射数据
    :param info_mapping: 字典，i_mapping = {"var_a": "hello", "var_b": "world"}
    :return: print_info(i_mapping)
            ==================== Output ====================
            Key              :  Value
            ---------------- :  ----------------------------
            var_a            :  hello
            var_b            :  world
            ------------------------------------------------
    """
    if not info_mapping:
        return

    content_format = "{:<16} : {:<}\n"
    content = "\n==================== Output ====================\n"
    content += content_format.format("Variable", "Value")
    content += content_format.format("-" * 16, "-" * 29)

    for key, value in info_mapping.items():
        if isinstance(value, (tuple, collections.deque)):
            continue
        elif isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif value is None:
            value = "None"

        content += content_format.format(key, value)

    content += "-" * 48 + "\n"
    logger.info(content)


def print_progressbar(seconds: int):
    """
    打印进度条
    :param seconds: 秒
    :return:
    """
    widgets = ['Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker('-=>')), ' ', ETA()]
    pb = ProgressBar(widgets=widgets, maxval=seconds).start()
    for i in range(seconds):
        pb.update(1 * i + 1)
        time.sleep(1)
    pb.finish()


def get_local_ip():
    """
    获取本地IP地址 --linux/windows
    :return:(char) IP地址
    """
    return socket.gethostbyname(socket.gethostname())


def get_net_mac_address():
    """
    获取系统mac id
    ether 00:16:3e:17:7c:40  txqueuelen 1000  (Ethernet)
    ==> '00:16:3e:17:7c:40'
    :return:
    """
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])


def remove_files(base_dir, ext='test_*.py'):
    """
    使用通配符，获取文件并删除
    :return:
    """
    for f in glob.glob(os.path.join(base_dir, ext)):
        logger.info("remove {}".format(f))
        os.remove(f)


def rm_tree(base_dir, ext='test_*', max_rotation=0):
    """
    使用通配符，获取文件并删除
    :param base_dir:
    :param ext:
    :param max_rotation: 保留最大个数，0:不保留(按名字倒序排列后，删除列表尾部),
    如['test_01', 'test_02', 'test_03']，保留2个则删除test_01
    注意：文件夹名称排序，test3 > test11，所以最好数字补位成test_03<test_11
    :return:
    """
    targets = glob.glob(os.path.join(base_dir, ext))
    targets.sort(reverse=True)
    targets = targets[max_rotation:]

    for f in targets:
        if os.path.isdir(f):
            logger.info("remove tree dir {}".format(f))
            shutil.rmtree(f)
        elif os.path.isfile(f):
            logger.info("remove file {}".format(f))
            os.remove(f)
        else:
            logger.error("指定路径不存在！ - {}".format(f))


def get_list_intersection(list_a, list_b):
    """
    获取列表A、B的交集
    :param list_a:
    :param list_b:
    :return: 交集集合转换为列表
    """

    assert isinstance(list_a, list)
    assert isinstance(list_b, list)
    return list((set(list_a).union(set(list_b))) ^ (set(list_a) ^ set(list_b)))


def lower_dict_keys(origin_dict):
    """
    转换字典key为小写
    :param origin_dict:
    :return:
    Examples:
        >>> o_dict = {
            "Name": "",
            "URL": "",
        }
        >>> lower_dict_keys(o_dict)
            {
                "name": "",
                "url": "",
            }
    """
    if not origin_dict or not isinstance(origin_dict, dict):
        return origin_dict

    return {key.lower(): value for key, value in origin_dict.items()}


def gen_cartesian_product(*args: List[Dict]) -> List[Dict]:
    """
    根据输入的多个列表参数，生成笛卡尔积
    :param args:
    :return:
        >>> arg1 = [{"a": 1}, {"a": 2}]
        >>> arg2 = [{"x": 111, "y": 112}, {"x": 121, "y": 122}]
        >>> args = [arg1, arg2]
        >>> gen_cartesian_product(*args)
        >>> # same as below
        >>> gen_cartesian_product(arg1, arg2)
            [
                {'a': 1, 'x': 111, 'y': 112},
                {'a': 1, 'x': 121, 'y': 122},
                {'a': 2, 'x': 111, 'y': 112},
                {'a': 2, 'x': 121, 'y': 122}
            ]
    """
    if not args:
        return []
    elif len(args) == 1:
        return args[0]

    product_list = []
    for product_item_tuple in itertools.product(*args):
        product_item_dict = {}
        for item in product_item_tuple:
            product_item_dict.update(item)
        product_list.append(product_item_dict)
    return product_list


def sort_dict_by_custom_order(raw_dict: Dict, custom_order: List):
    """
    根据自定义列表顺序，为字典排序
    :param raw_dict:
    :param custom_order:
    :return:
    """
    def get_index_from_list(lst: List, item: Any):
        try:
            return lst.index(item)
        except ValueError:
            # item is not in lst
            return len(lst) + 1

    return dict(
        sorted(raw_dict.items(), key=lambda i: get_index_from_list(custom_order, i[0]))
    )


def is_support_multiprocessing() -> bool:
    """
    检查系统环境是否支持多进程
    :return:
    """
    try:
        Queue()
        return True
    except (ImportError, OSError):
        # 系统不支持 semaphores(依赖多进程), 如 Android termux
        return False


if __name__ == '__main__':
    pass
    # print(get_local_ip())
    # sleep_progressbar(3)
    # print(get_list_intersection([1, 2], [2, 3]))
    # print_info({"aaa": {"sd": 2}, "nbbb": 2})
    # print(get_platform())
    # print(to_safe_name("mall-goods搜索"))
    # print(to_class_name("mall-goods搜索"))
    # print(get_local_ip())
    # print(get_mac_address())
    # print(to_class_name("GetCustomerPool list A"))
    print(seconds_to_hms(300))
