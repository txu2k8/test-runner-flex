#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:response
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 响应内容处理，断言逻辑
"""
import json

try:
    import allure
    USE_ALLURE = True
except ModuleNotFoundError:
    USE_ALLURE = False
from typing import Dict, Text, List, Any, NoReturn

import requests
import jsonpath
import jmespath
from jmespath.exceptions import JMESPathError
from loguru import logger

from testrunner.core.runners import exceptions
from testrunner.core.runners.exceptions import ValidationFailure, StatusCodeValidationFailure, \
    ExtractFailure, ParamsError
from testrunner.base.models import TestStatusEnum
from testrunner.core.runners.api.models import VariablesMapping, Validators, FunctionsMapping
from testrunner.core.runners.api.parser import parse_data, parse_string_value, get_mapping_function
from testrunner.core.runners.api.builtin.comparators import get_uniform_comparator


# 统一验证器
def uniform_validator(validator):
    """ 统一验证器
    Args:
        validator (dict): validator maybe in two formats:

            format1: this is kept for compatibility with the previous versions.
                {"check": "status_code", "comparator": "eq", "expect": 201}
                {"check": "$resp_body_success", "comparator": "eq", "expect": True}
            format2: recommended new version, {assert: [check_item, expected_value]}
                {'eq': ['status_code', 201]}
                {'eq': ['$resp_body_success', True]}

    Returns
        dict: validator info

            {
                "check": "status_code",
                "expect": 201,
                "assert": "equals"
            }

    """
    if not isinstance(validator, dict):
        raise ParamsError(f"invalid validator: {validator}")

    if "check" in validator and "expect" in validator:
        # format1
        check_item = validator["check"]
        expect_value = validator["expect"]
        message = validator.get("message", "")
        comparator = validator.get("comparator", "eq")

    elif len(validator) == 1:
        # format2
        comparator = list(validator.keys())[0]
        compare_values = validator[comparator]

        if not isinstance(compare_values, list) or len(compare_values) not in [2, 3]:
            raise ParamsError(f"invalid validator: {validator}")

        check_item = compare_values[0]
        expect_value = compare_values[1]
        if len(compare_values) == 3:
            message = compare_values[2]
        else:
            # len(compare_values) == 2
            message = ""

    else:
        raise ParamsError(f"invalid validator: {validator}")

    # uniform comparator, e.g. lt => less_than, eq => equals
    assert_method = get_uniform_comparator(comparator)

    return {
        "check": check_item,
        "expect": expect_value,
        "assert": assert_method,
        "message": message,
    }


class ResponseObject(object):
    def __init__(self, resp_obj: requests.Response,
                 api_id=0, api_desc="",
                 test_type="", dept_desc="", suite_desc="", case_id=0, case_desc="", step_desc=""):
        """ initialize with a requests.Response object

        Args:
            resp_obj (instance): requests.Response instance
            api_id(int): api ID
            api_desc(str): api description
            test_type(str): 单接口测试 | 场景测试 ...
            dept_desc(str): department description
            suite_desc(str): suite description
            case_id(int): case ID
            case_desc(str): case description
            step_desc(str): step description

        """
        self.resp_obj = resp_obj
        self.api_id = api_id
        self.api_desc = api_desc
        self.test_type = test_type
        self.dept_desc = dept_desc
        self.suite_desc = suite_desc
        self.case_id = case_id
        self.case_desc = case_desc
        self.step_desc = step_desc
        self.validation_results: Dict = {}
        self.test_status: Text = TestStatusEnum.PASSED  # 测试步骤执行结果：pass | fail | error | skip
        self.blocker: List = []

    def __getattr__(self, key):
        # 查找属性时调用 实例对象.属性名
        if key in ["json", "content", "body"]:
            try:
                value = self.resp_obj.json()
            except ValueError:
                value = self.resp_obj.content
        elif key == "cookies":
            value = self.resp_obj.cookies.get_dict()
        else:
            try:
                value = getattr(self.resp_obj, key)
            except AttributeError:
                err_msg = "ResponseObject does not have attribute: {}".format(key)
                logger.error(err_msg)
                raise exceptions.ParamsError(err_msg)

        self.__dict__[key] = value
        return value

    def _search_jmespath(self, expr: Text) -> Any:
        """
        根据jmespath语法搜索提取实际结果值, FYI: https://jmespath.org/tutorial.html
        :param expr:
        :return:
        """
        resp_obj_meta = {
            "status_code": self.status_code,
            "headers": self.headers,
            "cookies": self.cookies,
            "body": self.body,
        }
        if not expr.startswith(tuple(resp_obj_meta.keys())):
            return expr

        try:
            check_value = jmespath.search(expr, resp_obj_meta)
        except JMESPathError as ex:
            logger.error(
                f"failed to search with jmespath\n"
                f"expression: {expr}\n"
                f"data: {resp_obj_meta}\n"
                f"exception: {ex}"
            )
            raise

        return check_value

    def _search_jsonpath(self, expr: Text) -> Any:
        """
        根据jsonpath语法搜索提取实际结果值, FYI: https://goessner.net/articles/JsonPath/
        注：此处强行要求、仅支持jsonpath表达式以 "$.."开头，以降低解析难度
        :param expr:
        :return:
        """
        resp_obj_meta = {
            "status_code": self.status_code,
            "headers": self.headers,
            "cookies": self.cookies,
            "body": self.body,
        }

        try:
            values = jsonpath.jsonpath(resp_obj_meta, expr)
            if values is False:
                err_msg = f"failed to search with jsonpath\n"\
                          f"expression: {expr}\n"\
                          f"data: {resp_obj_meta}\n"\
                          f"return: {values}"
                raise Exception(err_msg)
            check_value = values[0] if isinstance(values, list) else values  # $..深层扫描，只取结果第一个元素
        except exceptions.JSONPathError as ex:
            logger.error(
                f"failed to search with jsonpath\n"
                f"expression: {expr}\n"
                f"data: {resp_obj_meta}\n"
                f"exception: {ex}"
            )
            raise
        except exceptions.MyBaseFailure as e:
            logger.error(e)
            raise

        return check_value

    # 提取并写入字典
    def extract(self, extractors: Dict[Text, Text]) -> Dict[Text, Any]:
        """根据jmespath语法找到值 放入 提取参数字典中"""
        if not extractors:
            return {}
        msg = "\n================== extract details ==================\n"
        extract_mapping = {}
        extract_pass = True
        failures = []
        for key, field in extractors.items():
            extract_msg = ""
            try:
                field_value = self._search_jsonpath(field) if field.startswith('$..') else self._search_jmespath(field)
                extract_mapping[key] = field_value
                extract_msg = "{:<30}\t==>{}\n".format(field, json.dumps({key: field_value}))
                if not field.startswith('$..') and field_value is None:
                    extract_pass = False
                    failures.append(extract_msg)
                    logger.error(extract_msg)
                else:
                    logger.info(extract_msg)
            except Exception as e:
                extract_pass = False
                extract_msg = "{:<30}\t==>{}\n".format(field, e)
                logger.error(extract_msg)
                failures.append(extract_msg)
            finally:
                msg += "{}\n".format(extract_msg)

        logger.info("extract mapping: {}".format(json.dumps(extract_mapping, indent=2, ensure_ascii=False)))
        if USE_ALLURE:
            allure.attach(msg, "extract")
        if not extract_pass:
            failures_string = "\n".join([failure for failure in failures])
            self.test_status = TestStatusEnum.ERROR
            raise ExtractFailure(failures_string)
        return extract_mapping

    # 验证
    def validate(
            self,
            validators: Validators,
            variables_mapping: VariablesMapping = None,
            functions_mapping: FunctionsMapping = None,
    ) -> NoReturn:

        variables_mapping = variables_mapping or {}
        functions_mapping = functions_mapping or {}

        self.validation_results = {}
        if not validators:
            return

        validate_pass = True
        failures = []
        msg = "\n================== validate details ==================\n"
        for v in validators:
            if "validate_extractor" not in self.validation_results:
                self.validation_results["validate_extractor"] = []

            u_validator = uniform_validator(v)

            # check item
            check_item = u_validator["check"]
            if "$" in check_item:
                # check_item is variable or function
                check_item = parse_data(
                    check_item, variables_mapping, functions_mapping
                )
                check_item = parse_string_value(check_item)

            if check_item and isinstance(check_item, Text):
                check_value = self._search_jsonpath(check_item) if check_item.startswith('$..') else self._search_jmespath(check_item)
            else:
                # variable or function evaluation result is "" or not text
                check_value = check_item

            # comparator
            assert_method = u_validator["assert"]
            assert_func = get_mapping_function(assert_method, functions_mapping)

            # expect item
            expect_item = u_validator["expect"]
            # parse expected value with config/teststep/extracted variables
            expect_value = parse_data(expect_item, variables_mapping, functions_mapping)

            # message
            message = u_validator["message"]
            # parse message with config/teststep/extracted variables
            message = parse_data(message, variables_mapping, functions_mapping)

            validate_msg = f"assert {check_item} {assert_method} {expect_value}({type(expect_value).__name__})"

            validator_dict = {
                "comparator": assert_method,
                "check": check_item,
                "check_value": check_value,
                "expect": expect_item,
                "expect_value": expect_value,
                "message": message,
            }

            try:
                assert_func(check_value, expect_value, message)
                validate_msg += "\t==> pass"
                logger.info(validate_msg)
                validator_dict["check_result"] = "pass"
            except AssertionError as ex:
                if check_item in ['$..status_code', 'status_code']:
                    self.blocker = [
                        str(check_value),
                        self.resp_obj.request.method,
                        self.resp_obj.request.url,
                        self.api_id,
                        self.api_desc,
                        self.test_type,
                        self.dept_desc,
                        self.suite_desc,
                        self.case_id,
                        self.case_desc,
                        self.step_desc
                    ]
                validate_pass = False
                validator_dict["check_result"] = "fail"
                validate_msg += "\t==> fail"
                validate_msg += (
                    f"\n"
                    f"检查项: {check_item}\n"
                    f"比较器: {assert_method}\n"
                    f"实际值: {check_value}({type(check_value).__name__})\n"
                    f"期望值: {expect_value}({type(expect_value).__name__})"
                )
                message = str(ex)
                if message:
                    validate_msg += f"\nmessage: {message}"

                logger.error(validate_msg)
                failures.append(validate_msg)
            finally:
                msg += "{}\n".format(validate_msg)
            self.validation_results["validate_extractor"].append(validator_dict)

        if USE_ALLURE:
            allure.attach(msg, "validate")

        if not validate_pass:
            self.test_status = TestStatusEnum.FAILED
            failures_string = "\n".join([failure for failure in failures])
            if self.blocker:
                raise StatusCodeValidationFailure(failures_string)
            raise ValidationFailure(failures_string)
        self.test_status = TestStatusEnum.PASSED


if __name__ == '__main__':
    pass
