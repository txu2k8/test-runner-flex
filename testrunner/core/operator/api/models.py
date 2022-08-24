#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:models
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description: 接口测试 - 数据模型定义

typing[类型提示]: https://docs.python.org/zh-cn/3/library/typing.html
pydantic[类型校验]: https://pydantic-docs.helpmanual.io/
用上这两个库就有点强类型语言的味儿了
泛型: https://docs.python.org/zh-cn/3/library/typing.html#generics
枚举: https://docs.python.org/zh-cn/3/library/enum.html
"""
import os
from enum import Enum
from typing import Any
from typing import Dict, Text, Union, Callable
from typing import List

from pydantic import BaseModel, Field
from pydantic import HttpUrl

from testrunner.base.models import TestStatusEnum, StepType, TestTime

Name = Text
Desc = Text
Url = Text
BaseUrl = Union[HttpUrl, Text]
VariablesMapping = Dict[Text, Any]
FunctionsMapping = Dict[Text, Callable]
Headers = Dict[Text, Text]
Cookies = Dict[Text, Text]
Verify = bool
Hooks = List[Union[Text, Dict[Text, Text]]]
Export = List[Text]
Validators = List[Dict]
Env = Dict[Text, Any]


# 接口请求方法枚举
class MethodEnum(Text, Enum):
    """接口请求方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"
    CALL = "CALL"


# 项目配置
class ProjectMeta(BaseModel):
    """项目配置数据模型"""
    name: Text = ""
    debugtalk_py: Text = ""  # debugtalk.py file content
    debugtalk_path: Text = ""  # debugtalk.py file path
    functions: FunctionsMapping = {}  # functions defined in debugtalk.py
    dot_env_path: Text = ""  # .env file path
    env: Env = {}
    RootDir: Text = os.getcwd()  # project root directory (ensure absolute), the path debugtalk.py located


# 测试配置模型
class TConfig(BaseModel):
    """测试配置模型"""
    project_name: Text = ''  # 项目名称
    module_name: Text = ''  # 模块名称
    suite_name: Text = ''  # 用例集名称
    case_id: int = 0  # 用例ID
    case_name: Text = ''  # 用例名称

    verify: Verify = False
    base_url: BaseUrl = ""
    variables: Union[VariablesMapping, Text] = {}
    parameters: Union[VariablesMapping, Text] = {}
    export: Export = []
    path: Text = None


# 接口请求参数设计
class TRequest(BaseModel):
    """接口请求模型"""
    method: MethodEnum
    url: Url
    params: Dict[Text, Text] = {}
    headers: Headers = {}
    req_json: Union[Dict, List, Text] = Field(None, alias="json")
    data: Union[Text, Dict[Text, Any]] = None
    cookies: Cookies = {}
    timeout: float = 120
    allow_redirects: bool = True
    verify: Verify = False
    upload: Dict = {}  # 上传数据接口需特殊封包处理


class TStep(BaseModel):
    """测试步骤模型"""
    id: int = 0
    sid: Text = ''
    step_name: Name
    step_type: StepType = StepType.API  # 测试类型 - API
    description: Desc = ''  # 步骤描述
    is_skip: bool = False  # 是否跳过改测试步骤
    skipif: Union[Text, None] = None  # 条件表达式，是否跳过当前步骤
    depends: List[int] = []  # 依赖的测试步骤id，如果依赖步骤失败，跳过当前步骤
    sleep: int = 0  # 执行当前步骤前sleep seconds
    base_url: BaseUrl = ""  # 指定 base_url，如未指定则使用TConfig里的base_url
    request: Union[TRequest, None] = None
    variables: VariablesMapping = {}
    setup_hooks: Hooks = []
    teardown_hooks: Hooks = []
    extract: VariablesMapping = {}
    validators: Validators = Field([], alias="validate")
    validate_script: List[Text] = []


class TCase(BaseModel):
    """测试用例模型 = 测试配置 + 测试步骤"""
    id: int = 0
    case_name: Name = ''
    case_safe_name: Name = ''
    description: Desc = ''
    config: TConfig
    test_type: Text = ''  # allure.feature
    tags: List[Text] = []  # allure.tag
    teststeps: List[TStep]
    setups: List[Text] = []  # setup 类名列表
    teardowns: List[Text] = []  # teardown 类名列表


class TSuite(BaseModel):
    """测试套件"""
    id: int = 0
    suite_name: Name = ''
    description: Desc = ''
    config: TConfig
    testcases: List[TCase]
    setup_tcs: List[TCase] = []
    teardown_tcs: List[TCase] = []
    setup_class_tcs: List[TCase] = []
    teardown_class_tcs: List[TCase] = []


# 请求 数据模型
class RequestData(BaseModel):
    """请求数据模型"""
    method: MethodEnum = MethodEnum.GET
    url: Url
    headers: Headers = {}
    cookies: Cookies = {}
    body: Union[Text, bytes, List, Dict, None] = {}


# 响应 数据模型
class ResponseData(BaseModel):
    """响应数据模型"""
    status_code: int
    headers: Dict
    cookies: Cookies
    encoding: Union[Text, None] = None
    content_type: Text
    body: Union[Text, bytes, List, Dict]


# 请求+响应 数据模型
class ReqRespData(BaseModel):
    """请求响应数据模型"""
    request: RequestData
    response: ResponseData


# 请求会话数据 统计
class RequestStat(BaseModel):
    """请求数据统计"""
    content_size: float = 0
    response_time_ms: float = 0
    elapsed_ms: float = 0


# 请求会话数据
class SessionData(BaseModel):
    """请求会话数据：请求+响应、请求状态、地址、校验器"""
    success: bool = False
    # req_resp_datas一般情况包含一条请求+响应数据，当发生重定向时，可能会有多条请求+响应数据
    req_resp_datas: List[ReqRespData] = []
    stat: RequestStat = RequestStat()
    validators: Dict = {}


# 步骤过程数据
class StepData(BaseModel):
    """测试步骤数据模型"""
    success: bool = True
    id: int = 0
    sid: Text = ""
    name: Text = ""
    description: Text = ""
    status: TestStatusEnum = TestStatusEnum.UNKNOWN
    blocker: List = []  # ['404', 'GET', '/api/path/1']
    data: Union[SessionData, List['StepData']] = None
    export_vars: VariablesMapping = {}


StepData.update_forward_refs()


# 测试用例 - 结果概览
class TestCaseSummary(BaseModel):
    """测试用例结果"""
    success: bool = True
    id: Text = ""
    name: Text = ""
    description: Text = ""
    status: TestStatusEnum = TestStatusEnum.UNKNOWN
    time: TestTime
    step_datas: List[StepData] = []
    log: Text = ""


if __name__ == '__main__':
    pass
