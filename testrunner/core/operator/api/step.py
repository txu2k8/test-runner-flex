#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:step
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import inspect
from typing import Text, Any, Union
from loguru import logger

from testrunner.base.models import StepType
from testrunner.core.operator.api.models import (
    TConfig,
    TStep,
    TRequest,
    MethodEnum,
)


class Config(object):
    """测试步骤自定义配置"""
    def __init__(self):
        self.__suite_name = ""
        self.__case_id = 0
        self.__case_name = ""
        self.__variables = {}
        self.__base_url = ""
        self.__verify = False
        self.__export = []
        self.__weight = 1

        caller_frame = inspect.stack()[1]
        self.__path = caller_frame.filename

    def perform(self) -> TConfig:
        return TConfig(
            suite_name=self.__suite_name,
            case_id=self.__case_id,
            case_name=self.__case_name,
            base_url=self.__base_url,
            verify=self.__verify,
            variables=self.__variables,
            export=list(set(self.__export)),
            path=self.__path,
            weight=self.__weight,
        )

    @property
    def path(self) -> Text:
        return self.__path

    @property
    def weight(self) -> int:
        return self.__weight

    def suite_name(self, suite_name: Text) -> "Config":
        self.__suite_name = suite_name
        return self

    def case_id(self, case_id: int) -> "Config":
        self.__case_id = case_id
        return self

    def case_name(self, case_name: Text) -> "Config":
        self.__case_name = case_name
        return self

    def variables(self, **variables) -> "Config":
        self.__variables.update(variables)
        return self

    def base_url(self, base_url: Text) -> "Config":
        self.__base_url = base_url
        return self

    def verify(self, verify: bool) -> "Config":
        self.__verify = verify
        return self

    def export(self, *export_var_name: Text) -> "Config":
        self.__export.extend(export_var_name)
        return self

    def locust_weight(self, weight: int) -> "Config":
        self.__weight = weight
        return self


class StepRequestValidation(object):
    """接口请求后，数据校验方法"""

    def __init__(self, step_context: TStep):
        self.__step_context = step_context

    def perform(self) -> TStep:
        return self.__step_context

    def assert_equal(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"equal": [json_path, expected_value, message]}
        )
        return self

    def assert_not_equal(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"not_equal": [json_path, expected_value, message]}
        )
        return self

    def assert_greater_than(
            self, json_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"greater_than": [json_path, expected_value, message]}
        )
        return self

    def assert_less_than(
            self, json_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"less_than": [json_path, expected_value, message]}
        )
        return self

    def assert_greater_or_equals(
            self, json_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"greater_or_equals": [json_path, expected_value, message]}
        )
        return self

    def assert_less_or_equals(
            self, json_path: Text, expected_value: Union[int, float], message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"less_or_equals": [json_path, expected_value, message]}
        )
        return self

    def assert_length_equal(
            self, json_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_equal": [json_path, expected_value, message]}
        )
        return self

    def assert_length_greater_than(
            self, json_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_greater_than": [json_path, expected_value, message]}
        )
        return self

    def assert_length_less_than(
            self, json_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_less_than": [json_path, expected_value, message]}
        )
        return self

    def assert_length_greater_or_equals(
            self, json_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_greater_or_equals": [json_path, expected_value, message]}
        )
        return self

    def assert_length_less_or_equals(
            self, json_path: Text, expected_value: int, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"length_less_or_equals": [json_path, expected_value, message]}
        )
        return self

    def assert_string_equals(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"string_equals": [json_path, expected_value, message]}
        )
        return self

    def assert_startswith(
            self, json_path: Text, expected_value: Text, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"startswith": [json_path, expected_value, message]}
        )
        return self

    def assert_endswith(
            self, json_path: Text, expected_value: Text, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"endswith": [json_path, expected_value, message]}
        )
        return self

    def assert_regex_match(
            self, json_path: Text, expected_value: Text, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"regex_match": [json_path, expected_value, message]}
        )
        return self

    def assert_contains_if_exist(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"contains_if_exist": [json_path, expected_value, message]}
        )
        return self

    def assert_contains(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"contains": [json_path, expected_value, message]}
        )
        return self

    def assert_not_contains(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"not_contains": [json_path, expected_value, message]}
        )
        return self

    def assert_contained_by(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"contained_by": [json_path, expected_value, message]}
        )
        return self

    def assert_not_contained_by(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"not_contained_by": [json_path, expected_value, message]}
        )
        return self

    def assert_has_key(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"has_key": [json_path, expected_value, message]}
        )
        return self

    def assert_type_match(
            self, json_path: Text, expected_value: Any, message: Text = ""
    ) -> "StepRequestValidation":
        self.__step_context.validators.append(
            {"type_match": [json_path, expected_value, message]}
        )
        return self


class StepRequestExtraction(object):
    """提取响应数据中的内容"""
    def __init__(self, step_context: TStep):
        self.__step_context = step_context

    def perform(self) -> TStep:
        return self.__step_context

    def with_jmespath(self, jmes_path: Text, var_name: Text) -> "StepRequestExtraction":
        """
        jmespath 提取响应数据：获取 jmes_path 提取的对应数据，并保存到变量 var_name
        :param jmes_path:
        :param var_name:
        :return:
        """
        self.__step_context.extract[var_name] = jmes_path
        return self

    def with_regex(self):
        # TODO: 正则表达式 提取响应数据，暂未实现
        pass

    def with_jsonpath(self, json_path: Text, var_name: Text) -> "StepRequestExtraction":
        """
        jsonpath 提取响应数据：获取 json_path 提取的对应数据，并保存到变量 var_name
        :param json_path:
        :param var_name:
        :return:
        """
        self.__step_context.extract[var_name] = json_path
        return self

    def validate(self) -> StepRequestValidation:
        return StepRequestValidation(self.__step_context)


class StepRequestWithOptionalArgs(object):
    """接口请求可选参数配置"""

    def __init__(self, step_context: TStep):
        self.__step_context = step_context

    def perform(self) -> TStep:
        return self.__step_context

    def with_params(self, **params) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.params.update(params)
        return self

    def with_headers(self, **headers) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.headers.update(headers)
        return self

    def with_cookies(self, **cookies) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.cookies.update(cookies)
        return self

    def with_data(self, data) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.data = data
        return self

    def with_json(self, req_json) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.req_json = req_json
        return self

    def set_timeout(self, timeout: float) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.timeout = timeout
        return self

    def set_verify(self, verify: bool) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.verify = verify
        return self

    def set_allow_redirects(self, allow_redirects: bool) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.allow_redirects = allow_redirects
        return self

    def upload(self, **file_info) -> "StepRequestWithOptionalArgs":
        self.__step_context.request.upload.update(file_info)
        return self

    def teardown_hook(
            self, hook: Text, assign_var_name: Text = None
    ) -> "StepRequestWithOptionalArgs":
        if assign_var_name:
            self.__step_context.teardown_hooks.append({assign_var_name: hook})
        else:
            self.__step_context.teardown_hooks.append(hook)

        return self

    def extract(self) -> StepRequestExtraction:
        return StepRequestExtraction(self.__step_context)

    def validate(self) -> StepRequestValidation:
        return StepRequestValidation(self.__step_context)


class RunRequest(object):
    def __init__(self, step_name: Text):
        self.__step_context = TStep(step_name=step_name)
        self.step_type = StepType.API

    def with_id(self, step_id) -> "RunRequest":
        self.__step_context.id = step_id
        return self

    def with_sid(self, step_sid) -> "RunRequest":
        self.__step_context.sid = step_sid
        return self

    def with_is_skip(self, is_skip) -> "RunRequest":
        self.__step_context.is_skip = is_skip
        return self

    def with_is_api_valid(self, is_api_valid) -> "RunRequest":
        self.__step_context.is_api_valid = is_api_valid
        return self

    def with_is_api_updated(self, is_api_updated) -> "RunRequest":
        self.__step_context.is_api_updated = is_api_updated
        return self

    def with_skipif(self, skipif) -> "RunRequest":
        self.__step_context.skipif = skipif
        return self

    def with_depends(self, depends) -> "RunRequest":
        self.__step_context.depends = depends
        return self

    def with_base_url(self, base_url) -> "RunRequest":
        self.__step_context.base_url = base_url
        return self

    def with_description(self, description) -> "RunRequest":
        self.__step_context.description = description
        return self

    def with_api_id(self, api_id) -> "RunRequest":
        self.__step_context.api_id = api_id
        return self

    def with_api_description(self, api_description) -> "RunRequest":
        self.__step_context.api_description = api_description
        return self

    def with_variables(self, **variables) -> "RunRequest":
        self.__step_context.variables.update(variables)
        return self

    def setup_hook(self, hook: Text, assign_var_name: Text = None) -> "RunRequest":
        if assign_var_name:
            self.__step_context.setup_hooks.append({assign_var_name: hook})
        else:
            self.__step_context.setup_hooks.append(hook)

        return self

    def get(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.GET, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)

    def post(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.POST, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)

    def put(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.PUT, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)

    def head(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.HEAD, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)

    def delete(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.DELETE, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)

    def options(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.OPTIONS, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)

    def patch(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.PATCH, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)

    def call(self, url: Text) -> StepRequestWithOptionalArgs:
        self.__step_context.request = TRequest(method=MethodEnum.CALL, url=url)
        return StepRequestWithOptionalArgs(self.__step_context)


class ApiStep(object):
    """API测试步骤封装"""
    def __init__(
        self,
        step_context: Union[
            StepRequestValidation,
            StepRequestExtraction,
            StepRequestWithOptionalArgs,
        ],
    ):
        self.__step_context = step_context.perform()
        self.run()

    def perform(self) -> TStep:
        return self.__step_context

    def run(self):
        logger.info("执行API步骤xxxxx")
        logger.info(self.__step_context.step_name)

    @property
    def step_name(self):
        return self.__step_context.step_name

    @property
    def request(self) -> TRequest:
        return self.__step_context.request


if __name__ == '__main__':
    pass
