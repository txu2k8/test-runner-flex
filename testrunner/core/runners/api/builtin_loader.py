#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:buildin_loader
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description:
    1. 预置函数加载成方法字典
    2. 路径加载
"""
import importlib
import os
import sys
import types
from typing import Tuple, Dict, Union, Text, Callable
from pydantic import ValidationError
from loguru import logger

from testrunner.core.runners import exceptions
from testrunner.core.runners.api import builtin
from testrunner.core.runners.api.models import ProjectMeta, TCase, TSuite

project_meta: Union[ProjectMeta, None] = None


def load_testcase(testcase: Dict) -> TCase:
    """将用例数据（字典）转成 TestCase对象"""
    try:
        # validate with pydantic TestCase model
        testcase_obj = TCase.parse_obj(testcase)
    except ValidationError as ex:
        err_msg = f"TestCase ValidationError:\nerror: {ex}\ncontent: {testcase}"
        raise exceptions.TestCaseFormatError(err_msg)

    return testcase_obj


def load_testsuite(testsuite: Dict) -> TSuite:
    """将用例集数据（字典）转成 TestSuite对象"""
    name = testsuite["suite_name"]
    try:
        # validate with pydantic TestSuite model
        testsuite_obj = TSuite.parse_obj(testsuite)
    except ValidationError as ex:
        err_msg = f"TestSuite ValidationError:\nTestSuite: {name}\nerror: {ex}"
        raise exceptions.TestSuiteFormatError(err_msg)

    return testsuite_obj


# 加载一个模块的方法，返回一个方法字典， 自定义函数实现的一部分
def load_module_functions(module) -> Dict[Text, Callable]:
    """
    加载模块方法
    :param module:
    :return: {"func1_name": func1}
    """
    module_functions = {}
    # vars(module) 返回模块的对象
    for name, item in vars(module).items():
        # types.FunctionType 函数类型
        if isinstance(item, types.FunctionType):
            # 映射关系：方法名称作为key，函数对象作为value
            module_functions[name] = item

    return module_functions


# 加载预置方法：core.builtin
def load_builtin_functions() -> Dict[Text, Callable]:
    """加载builtin模块的方法"""
    return load_module_functions(builtin)


# 定位文件，找到向上查找根目录
def locate_file(start_path: Text, file_name: Text) -> Text:
    """
    定位文件位置
    :param start_path: 文件起始位置，可以是文件path或目录
    :param file_name: 文件名
    :return: 文件绝对路径
    :exception: 如果没找到，raise异常FileNotFound
    """
    if os.path.isfile(start_path):
        start_dir_path = os.path.dirname(start_path)
    elif os.path.isdir(start_path):
        start_dir_path = start_path
    else:
        raise exceptions.FileNotFound(f"invalid path: {start_path}")

    file_path = os.path.join(start_dir_path, file_name)
    if os.path.isfile(file_path):
        # 确保绝对路径
        return os.path.abspath(file_path)

    # system root dir
    # Windows, e.g. 'D:\\'
    # Linux/Darwin, '/'
    parent_dir = os.path.dirname(start_dir_path)
    if parent_dir == start_dir_path:
        raise exceptions.FileNotFound(f"{file_name} not found in {start_path}")

    # 递归向上定位
    return locate_file(parent_dir, file_name)


# 找到debugtalk.py 绝对路径 TODO
def locate_debugtalk_py(start_path: Text) -> Text:
    """ locate debugtalk.py file

    Args:
        start_path (str): start locating path,
            maybe testcase file path or directory path

    Returns:
        str: debugtalk.py file path, None if not found

    """
    try:
        # locate debugtalk.py file.
        debugtalk_path = locate_file(start_path, "debugtalk.py")
    except exceptions.FileNotFound:
        debugtalk_path = None

    return debugtalk_path


# 找到项目根目录路径和debugtalk.py路径
def locate_project_root_directory(test_path: Text) -> Tuple[Text, Text]:
    """ locate debugtalk.py path as project root directory

    Args:
        test_path: specified testfile path

    Returns:
        (str, str): debugtalk.py path, project_root_directory

    """

    def prepare_path(path):
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        return path

    test_path = prepare_path(test_path)

    # locate debugtalk.py file
    debugtalk_path = locate_debugtalk_py(test_path)

    if debugtalk_path:
        # The folder contains debugtalk.py will be treated as project RootDir.
        project_root_directory = os.path.dirname(debugtalk_path)
    else:
        # debugtalk.py not found, use os.getcwd() as project RootDir. ../
        project_root_directory = os.getcwd()  # os.path.dirname(os.getcwd())

    return debugtalk_path, project_root_directory


# 加载debugtalk方法
def load_debugtalk_functions() -> Dict[Text, Callable]:
    """ load project debugtalk.py module functions
        debugtalk.py should be located in project root directory.

    Returns:
        dict: debugtalk module functions mapping
            {
                "func1_name": func1,
                "func2_name": func2
            }

    """
    # load debugtalk.py module
    try:
        # 动态导入包
        imported_module = importlib.import_module("debugtalk")
    except Exception as ex:
        logger.error(f"error occurred in debugtalk.py: {ex}")
        # sys.exit(1)
        raise Exception(f"error occurred in debugtalk.py: {ex}")

    # reload to refresh previously loaded module，避免有修改的情况 重载包
    imported_module = importlib.reload(imported_module)
    return load_module_functions(imported_module)


# 加载/赋值ProjectMeta数据
def load_project_meta(test_path: Text, reload: bool = False) -> ProjectMeta:
    """ load testcases, .env, debugtalk.py functions.
        testcases folder is relative to project_root_directory
        by default, project_meta will be loaded only once, unless set reload to true.

    Args:
        test_path (str): test file/folder path, locate project RootDir from this path.
        reload: reload project meta if set true, default to false

    Returns:
        project loaded api/testcases definitions,
            environments and debugtalk.py functions.

    """
    global project_meta
    if project_meta and (not reload):
        return project_meta

    project_meta = ProjectMeta()

    if not test_path:
        return project_meta

    debugtalk_path, project_root_directory = locate_project_root_directory(test_path)

    # add project RootDir to sys.path
    sys.path.insert(0, project_root_directory)

    # load .env file
    # NOTICE:
    # environment variable maybe loaded in debugtalk.py
    # thus .env file should be loaded before loading debugtalk.py
    # dot_env_path = os.path.join(project_root_directory, ".env")
    # dot_env = load_dot_env_file(dot_env_path)
    # if dot_env:
    #     project_meta.env = dot_env
    #     project_meta.dot_env_path = dot_env_path

    if debugtalk_path:
        # load debugtalk.py functions
        debugtalk_functions = load_debugtalk_functions()
    else:
        debugtalk_functions = {}

    # debugtalk_functions.update(load_customized_functions())

    # locate project RootDir and load debugtalk.py functions
    project_meta.RootDir = project_root_directory
    project_meta.functions = debugtalk_functions
    project_meta.debugtalk_path = debugtalk_path

    return project_meta


# 绝对路径转为相对(项目根目录)路径
def convert_relative_project_root_dir(abs_path: Text) -> Text:
    """ convert absolute path to relative path, based on project_meta.RootDir

    Args:
        abs_path: absolute path

    Returns: relative path based on project_meta.RootDir

    """
    _project_meta = load_project_meta(abs_path)
    if not abs_path.startswith(_project_meta.RootDir):
        raise exceptions.ParamsError(
            f"failed to convert absolute path to relative path based on project_meta.RootDir\n"
            f"abs_path: {abs_path}\n"
            f"project_meta.RootDir: {_project_meta.RootDir}"
        )

    return abs_path[len(_project_meta.RootDir) + 1:]


if __name__ == '__main__':
    pass
