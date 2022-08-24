#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:utils
@time:2022/04/04
@email:tao.xu2008@outlook.com
@description:
"""
import copy
import platform

from testrunner import __version__
from testrunner.core.operator.api.models import VariablesMapping


def get_platform():
    """获取测试平台版本信息"""
    return {
        "runner_version": __version__,
        "python_version": "{} {}".format(
            platform.python_implementation(), platform.python_version()
        ),
        "platform": platform.platform(),
    }


def merge_variables(
        variables: VariablesMapping, variables_to_be_overridden: VariablesMapping
) -> VariablesMapping:
    """
    merge变量mapping
    :param variables:
    :param variables_to_be_overridden: 内容会被更新
    :return:
    """
    step_new_variables = {}
    for key, value in variables.items():
        if f"${key}" == value or "${" + key + "}" == value:
            # e.g. {"base_url": "$base_url"}
            # or {"base_url": "${base_url}"}
            continue

        step_new_variables[key] = value

    merged_variables = copy.copy(variables_to_be_overridden)
    merged_variables.update(step_new_variables)
    return merged_variables


if __name__ == '__main__':
    pass
