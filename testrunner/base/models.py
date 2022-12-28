#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:models
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description: 基础数据模型
"""
from enum import Enum
from typing import Dict, List, Text, Union, Any

from pydantic import BaseModel, HttpUrl

Url = Union[HttpUrl, Text]


# 输入参数 - 环境 （cf_xml.py解析）
class TestEnv(BaseModel):
    """测试环境配置 - 数据模型"""
    description: Text = ''
    node_list: List[Dict[Text, Text]] = []
    endpoint: Text = ""
    endpoint_user: Text = ""
    endpoint_pass: Text = ""
    params: Dict[Text, Any] = {}
    web_url: Url
    web_user: Text = ""
    web_pass: Text = ""


# 输入参数 - 测试床 （cf_xml.py解析）
class Testbed(BaseModel):
    """测试床配置 - 数据模型"""
    xml_path: Text  # xml配置文件路径
    name: Text = ''
    description: Text = ''
    env_list: List[TestEnv]


# 输入参数 - 测试集 （cf_xml.py解析）
class TestSet(BaseModel):
    """测试集配置 - 数据模型"""
    xml_path: Text  # xml配置文件路径
    description: Text = ''
    case_list: List[Dict]


# 输入参数 - 配置 （cf_xml.py解析）
class TestConf(BaseModel):
    """测试执行配置 - 数据模型"""
    project: Text
    base_path: Text
    full_path: Text
    description: Text = ''
    testbed: Testbed
    test_set_list: List[TestSet]


# 测试步骤类型 - 枚举
class StepType(Text, Enum):
    """测试步骤类型枚举"""
    UNKNOWN = ''  # 未知、未定义
    API = 'API'  # rest_api 测试
    WEB = 'WEB'  # Web UI 测试
    SDK = 'SDK'  # SDK 调用
    CMD = 'CMD'  # OS CMD 命令执行
    UC = 'UC'  # UC 命令执行
    CASE_REF = 'CASE_REF'  # 步骤为测试用例引用


# 测试结果状态 - 枚举
class TestStatusEnum(Text, Enum):
    """测试结果状态枚举"""
    UNKNOWN = ''
    PASSED = 'passed'
    FAILED = 'failed'
    ERROR = 'error'
    SKIPPED = 'skipped'
    BROKEN = 'broken'


# 测试结果统计
class TestStat(BaseModel):
    """测试结果统计"""
    total: int = 0
    passed: int = 0
    failed: int = 0
    error: int = 0
    skipped: int = 0
    # 记录失败、故障、跳过的用例/步骤详情
    failed_list: List[Dict] = []  # [{},{}]
    error_list: List[Dict] = []  # [{},{}]
    skipped_list: List[Dict] = []  # [{},{}]


# 测试执行时间
class TestTime(BaseModel):
    """测试用例执行时间"""
    start_at: float = 0
    end_at: float = 0
    duration: float = 0
    start_at_format: Text = ""
    end_at_format: Text = ""
    duration_format: Text = ""


# 测试报告 - 结果概览
class ReportSummary(BaseModel):
    """测试报告概要收集"""
    id: int = 0
    name: Text = "xxx测试报告"
    description: Text = "xxx测试报告"
    success: bool = True
    status: TestStatusEnum = TestStatusEnum.UNKNOWN
    time: TestTime = TestTime()
    testcases_stat: TestStat = TestStat()
    teststeps_stat: TestStat = TestStat()
    log_path: Text = ''
    report_allure_path: Text = ''
    report_html_path: Text = ''
    jenkins_job_name: Text = ''
    jenkins_build_number: int = 0
    allure_url: Text = ''
    build_type: Text = 0
    build_status: Text = 'build-status-static'
    env_id: int = 0


# 数据库连接信息
class DBInfo(BaseModel):
    """数据库连接信息"""
    ENGINE: Text = "django.db.backends.sqlite3",  # django.db.backends.mysql
    NAME: Text = "",  # sqlite3: sqlite3.db path, mysql:database_name
    USER: Text = "",
    PASSWORD: Text = "",
    HOST: Text = "",
    PORT: int = 0,


# 测试平台信息
class PlatformInfo(BaseModel):
    runner_name: Text
    runner_version: Text
    python_version: Text
    platform: Text


if __name__ == '__main__':
    pass
