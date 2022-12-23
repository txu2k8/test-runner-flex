#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:comparators.py
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: validate comparators校验比较器
"""

import re
from typing import Text, Any, Union

# 支持的比较器规则、描述
comparators_define = (
    ('equal', ('eq', 'equal', 'equals'), '验证元素值等于'),
    ('not_equal', ('ne', 'neq', 'not_equal'), '验证元素值不等于'),

    ('greater_than', ('gt', 'greater_than'), '验证元素值大于'),
    ('less_than', ('lt', 'less_than'), '验证元素值小于'),

    ('greater_or_equals', ('ge', 'greater_or_equals'), '验证元素值大于等于'),
    ('less_or_equals', ('le', 'less_or_equals'), '验证元素值小于等于'),

    ('string_equals', ('str_eq', 'string_equals'), '验证元素值转换为string后等于'),
    ('length_equal', ('len_eq', 'length_equal'), '验证元素长度不等于'),
    ('length_greater_than', ('len_gt', 'length_greater_than'), '验证元素长度大于'),
    ('length_greater_or_equals', ('len_ge', 'length_greater_or_equals'), '验证元素长度大于等于'),
    ('length_less_than', ('len_lt', 'length_less_than'), '验证元素长度小于'),
    ('length_less_or_equals', ('len_le', 'length_less_or_equals'), '验证元素长度小于等于'),

    ('contains', ('contain', 'contains'), '验证元素的值中包含xxx'),
    ('not_contains', ('not_contain', 'not_contains'), '验证元素的值不包含xxx'),
    ('contains_if_exist', ('contain_if_exist', 'contains_if_exist'), '如果获取到元素不为空，验证元素的值中包含xxx'),
    ('contained_by', ('contained_by', 'in_list'), '验证元素的值包含于xxx'),
    ('not_contained_by', ('not_contained_by', 'not_in_list'), '验证元素的值不包含于xxx'),

    ('has_key', ('has_key', ), '验证字典元素包含key或key列表'),

    ('type_match', ('type_match', ), '验证元素的值类型为xxx（python数据类型名）'),
    ('regex_match', ('regex_match', ), '验证元素的值匹配正则表达式'),

    ('startswith', ('startswith', ), '验证元素的值转字符串后以xxx开头'),
    ('endswith', ('endswith', ), '验证元素的值转字符串后以xxx结尾'),
)


# 统一比较器名称
def get_uniform_comparator(comparator: Text):
    """统一比较器名称"""
    for cmp, keys, desc in comparators_define:
        if comparator in keys:
            return cmp
    else:
        return comparator


def equal(check_value: Any, expect_value: Any, message: Text = ""):
    assert check_value == expect_value, message


def not_equal(check_value: Any, expect_value: Any, message: Text = ""):
    assert check_value != expect_value, message


def greater_than(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    assert check_value > expect_value, message


def less_than(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    assert check_value < expect_value, message


def greater_or_equals(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    assert check_value >= expect_value, message


def less_or_equals(
    check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    assert check_value <= expect_value, message


def string_equals(check_value: Text, expect_value: Any, message: Text = ""):
    assert str(check_value) == str(expect_value), message


def length_equal(check_value: Text, expect_value: int, message: Text = ""):
    assert isinstance(expect_value, int), "expect_value should be int type"
    assert len(check_value) == expect_value, message


def length_greater_than(
    check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) > expect_value, message


def length_greater_or_equals(
    check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) >= expect_value, message


def length_less_than(
    check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) < expect_value, message


def length_less_or_equals(
    check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value should be int/float type"
    assert len(check_value) <= expect_value, message


def contains_if_exist(check_value: Any, expect_value: Any, message: Text = ""):
    if check_value:
        assert isinstance(
            check_value, (list, tuple, dict, str, bytes)
        ), "check_value should be list/tuple/dict/str/bytes type"
        assert expect_value in check_value, message


def contains(check_value: Any, expect_value: Any, message: Text = ""):
    assert isinstance(
        check_value, (list, tuple, dict, str, bytes)
    ), "check_value should be list/tuple/dict/str/bytes type"
    assert expect_value in check_value, message


def not_contains(check_value: Any, expect_value: Any, message: Text = ""):
    assert isinstance(
        check_value, (list, tuple, dict, str, bytes)
    ), "check_value should be list/tuple/dict/str/bytes type"
    assert expect_value not in check_value, message


def contained_by(check_value: Any, expect_value: Any, message: Text = ""):
    assert isinstance(
        expect_value, (list, tuple, dict, str, bytes)
    ), "expect_value should be list/tuple/dict/str/bytes type"
    assert check_value in expect_value, message


def not_contained_by(check_value: Any, expect_value: Any, message: Text = ""):
    assert isinstance(
        expect_value, (list, tuple, dict, str, bytes)
    ), "expect_value should be list/tuple/dict/str/bytes type"
    assert check_value not in expect_value, message


def type_match(check_value: Any, expect_value: Any, message: Text = ""):
    def get_type(name):
        if isinstance(name, type):
            return name
        elif isinstance(name, str):
            try:
                return __builtins__[name]
            except KeyError:
                raise ValueError(name)
        else:
            raise ValueError(name)

    if expect_value in ["None", "NoneType", None]:
        assert check_value is None, message
    else:
        assert type(check_value) == get_type(expect_value), message


def regex_match(check_value: Text, expect_value: Any, message: Text = ""):
    assert isinstance(expect_value, str), "expect_value should be Text type"
    assert isinstance(check_value, str), "check_value should be Text type"
    assert re.match(expect_value, check_value), message


def startswith(check_value: Any, expect_value: Any, message: Text = ""):
    assert str(check_value).startswith(str(expect_value)), message


def endswith(check_value: Text, expect_value: Any, message: Text = ""):
    assert str(check_value).endswith(str(expect_value)), message


def has_key(check_value: Any, expect_value: Any, message: Text = ""):
    assert isinstance(
        check_value, (list, tuple, dict, str, bytes)
    ), "check_value should be dict type"
    assert isinstance(
        expect_value, (list, tuple, str, bytes)
    ), "expect_value should be list/tuple/dict/str/bytes type"

    if isinstance(expect_value, (list, tuple)):
        for ev in expect_value:
            assert ev in check_value, message
    else:
        assert str(expect_value) in check_value, message


if __name__ == '__main__':
    pass
