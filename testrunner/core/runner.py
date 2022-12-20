#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:runner
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description: 测试框架执行器
"""

import json
import os
import copy
import time
import traceback
from datetime import datetime
from typing import List, Dict, Text, NoReturn

try:
    import allure

    USE_ALLURE = True
except ModuleNotFoundError:
    USE_ALLURE = False

from loguru import logger

from testrunner.config import global_cf
from testrunner.utils import util
from testrunner.core.plugins import exceptions
from testrunner.core.plugins.exceptions import ValidationFailure, StatusCodeValidationFailure, \
    ExtractFailure, ParamsError
from testrunner.core.plugins.api.client import HttpSession
from testrunner.core.plugins.api.ext.uploader import prepare_upload_step
from testrunner.core.plugins.api.builtin_loader import load_project_meta
from testrunner.core.plugins.api.parser import build_url, parse_data, parse_variables_mapping, call_func
from testrunner.core.plugins.api.response import ResponseObject
from testrunner.core.plugins.api.step import Config, ApiStep as Step
from testrunner.core.plugins.api.utils import merge_variables
from testrunner.base.models import TestTime
from testrunner.core.plugins.api.models import (
    ProjectMeta,
    TConfig,
    TCase,
    TStep,
    StepData,
    Hooks,
    VariablesMapping,
    TestCaseSummary,
    TestStatusEnum
)


class FlexRunner(object):
    config: Config
    teststeps: List[Step]
    case_id: int
    test_type: Text = ""

    success: bool = True  # indicate testcase execution result
    # __config: TConfig
    __teststeps: List[TStep]
    __project_meta: ProjectMeta = None
    __case_id: Text = ""
    __export: List[Text] = []
    __step_datas: List[StepData] = []
    __session: HttpSession = None
    __session_variables: VariablesMapping = {}
    # time
    __start_at: float = 0
    __duration: float = 0
    # log
    __log_path: Text = ""
    __log_handlers: List = []
    # exceptions
    __extract_failures: List[Text] = []  # 提取变量失败
    __status_code_validation_failures: List[Text] = []  # 校验失败
    __validation_failures: List[Text] = []  # 校验失败
    __session_exceptions: List[Text] = []  # 异常

    def __init_tests__(self) -> NoReturn:
        self.__config = self.config.perform()
        self.__teststeps = []
        self.__extract_failures = []
        self.__status_code_validation_failures = []
        self.__validation_failures = []
        self.__session_exceptions = []
        for step in self.teststeps:
            self.__teststeps.append(step.perform())

    @property
    def raw_testcase(self) -> TCase:
        if not hasattr(self, "__config"):
            self.__init_tests__()

        return TCase(config=self.__config, teststeps=self.__teststeps)

    def with_project_meta(self, project_meta: ProjectMeta) -> "FlexRunner":
        self.__project_meta = project_meta
        return self

    def with_session(self, session: HttpSession) -> "FlexRunner":
        self.__session = session
        return self

    def with_case_id(self, case_id: Text) -> "FlexRunner":
        self.__case_id = case_id
        return self

    def with_variables(self, variables: VariablesMapping) -> "FlexRunner":
        self.__session_variables = variables
        return self

    def with_export(self, export: List[Text]) -> "FlexRunner":
        self.__export = export
        return self

    def __call_hooks(
            self, hooks: Hooks, step_variables: VariablesMapping, hook_msg: Text,
    ) -> NoReturn:
        """ call hook actions.

        Args:
            hooks (list): each hook in hooks list maybe in two format.

                format1 (str): only call hook functions.
                    ${func()}
                format2 (dict): assignment, the value returned by hook function will be assigned to variable.
                    {"var": "${func()}"}

            step_variables: current step variables to call hook, include two special variables

                request: parsed request dict
                response: ResponseObject for current response

            hook_msg: setup/teardown request/testcase

        """
        logger.info(f"call hook actions: {hook_msg}")

        if not isinstance(hooks, List):
            logger.error(f"Invalid hooks format: {hooks}")
            return

        for hook in hooks:
            if isinstance(hook, Text):
                # format 1: ["${func()}"]
                logger.debug(f"call hook function: {hook}")
                parse_data(hook, step_variables, self.__project_meta.functions)
            elif isinstance(hook, Dict) and len(hook) == 1:
                # format 2: {"var": "${func()}"}
                var_name, hook_content = list(hook.items())[0]
                if not var_name:
                    continue
                hook_content_eval = parse_data(
                    hook_content, step_variables, self.__project_meta.functions
                )
                logger.debug(
                    f"call hook function: {hook_content}, got value: {hook_content_eval}"
                )
                logger.debug(f"assign variable: {var_name} = {hook_content_eval}")
                step_variables[var_name] = hook_content_eval
            else:
                logger.error(f"Invalid hook format: {hook}")

    def __prepare_request_data(self, step: TStep):
        """
        准备请求参数
        :param step:
        :return:
        """
        # 上传测试
        prepare_upload_step(step, self.__project_meta.functions)
        request_dict = step.request.dict()
        request_dict.pop("upload", None)

        # 参数解析（变量、函数）
        parsed_request_dict = parse_data(
            request_dict, step.variables, self.__project_meta.functions
        )
        # 添加默认请求头
        parsed_request_dict["headers"].setdefault(
            "User-Agent", global_cf.get_str("HEADERS", "User-Agent"),
        )
        parsed_request_dict["headers"].setdefault(
            "Authorization", self.__config.variables.get("session_id"),
        )
        # 保存request数据到 步骤变量
        step.variables["request"] = parsed_request_dict

        return parsed_request_dict

    def __run_step_request(self, step: TStep) -> StepData:
        """run teststep: request"""
        step_data = StepData(id=step.id, sid=step.sid, name=step.step_name, description=step.description)
        self.success = True

        # skip
        skipif = False
        if step.skipif:
            skipif = eval(parse_data(step.skipif, step.variables, self.__project_meta.functions))

        if step.is_skip or skipif:
            # pytest.skip()
            step_data.stat = TestStatusEnum.SKIPPED
            self.success = True
            self.__step_datas.append(step_data)
            return step_data

        # setup hooks
        if step.setup_hooks:
            try:
                self.__call_hooks(step.setup_hooks, step.variables, "setup request")
            except ValidationFailure as hooks_failure:
                self.success = False
                step_data.success = False
                step_data.stat = TestStatusEnum.FAILED
                self.__duration = time.time() - self.__start_at
                if USE_ALLURE:
                    allure.attach(str(hooks_failure), 'ValidationFailure')
                self.__validation_failures.append(str(hooks_failure))
                self.__step_datas.append(step_data)
                if USE_ALLURE:
                    allure.attach(str(hooks_failure), 'exception')
                raise

        # parse 参数、变量解析
        try:
            parsed_request_dict = self.__prepare_request_data(step)
        except Exception as e:
            self.success = False
            step_data.success = False
            step_data.stat = TestStatusEnum.ERROR
            self.__duration = time.time() - self.__start_at
            self.__step_datas.append(step_data)
            if USE_ALLURE:
                allure.attach('{}\n{}'.format(e, traceback.format_exc()), 'exception')
            raise e

        # prepare request arguments
        method = parsed_request_dict.pop("method")
        url_path = parsed_request_dict.pop("url")
        base_url = step.base_url or self.__config.base_url
        url = build_url(base_url, url_path)
        parsed_request_dict["verify"] = self.__config.verify
        parsed_request_dict["json"] = parsed_request_dict.pop("req_json", {})

        # request
        try:
            if method == 'CALL':
                resp = call_func(url_path, step.variables, self.__project_meta.functions, **(parsed_request_dict["json"]))
            else:
                resp = self.__session.request(method, url, **parsed_request_dict)
        except Exception as e:
            self.success = False
            step_data.success = False
            step_data.status = TestStatusEnum.ERROR
            self.__duration = time.time() - self.__start_at
            self.__step_datas.append(step_data)
            if USE_ALLURE:
                allure.attach('{}\n{}'.format(e, traceback.format_exc()), 'exception')
            raise e
        resp_obj = ResponseObject(
            resp,
            0,  # step.api_id,
            '',  # step.api_description,
            self.test_type,
            '',  # self.__config.department_name,
            self.__config.suite_name,
            self.__config.case_id,
            self.__config.case_name,
            "step{}".format(step.sid or step.id)
        )
        step.variables["response"] = resp_obj

        # teardown hooks
        if step.teardown_hooks:
            try:
                self.__call_hooks(step.teardown_hooks, step.variables, "teardown request")
            except StatusCodeValidationFailure as hooks_failure:
                self.success = False
                step_data.success = False
                step_data.stat = TestStatusEnum.FAILED
                self.__duration = time.time() - self.__start_at
                if USE_ALLURE:
                    allure.attach(str(hooks_failure), 'ValidationFailure')
                self.__validation_failures.append(str(hooks_failure))
                self.__step_datas.append(step_data)
                raise

        def log_req_resp_details():
            err_msg = "\n{} DETAILED REQUEST & RESPONSE {}\n".format("*" * 32, "*" * 32)

            # log request
            err_msg += "====== request details ======\n"
            err_msg += f"url: {url}\n"
            err_msg += f"method: {method}\n"
            headers = parsed_request_dict.pop("headers", {})
            err_msg += f"headers: {headers}\n"
            for k, v in parsed_request_dict.items():
                v = util.omit_long_data(v)
                err_msg += f"{k}: {repr(v)}\n"

            err_msg += "\n"

            # log response
            err_msg += "====== response details ======\n"
            err_msg += f"status_code: {resp.status_code}\n"
            err_msg += f"headers: {resp.headers}\n"
            err_msg += f"body: {repr(resp.text)}\n"
            logger.error(err_msg)

        # validate：结果校验
        variables_mapping = step.variables
        validators = step.validators
        session_success = False
        try:
            resp_obj.validate(
                validators, variables_mapping, self.__project_meta.functions
            )
            session_success = True
        except StatusCodeValidationFailure as rc_failure:
            session_success = False
            log_req_resp_details()
            # log testcase duration before raise ValidationFailure
            self.__duration = time.time() - self.__start_at
            if USE_ALLURE:
                allure.attach(str(rc_failure), 'StatusCodeValidationFailure')
            self.__validation_failures.append(str(rc_failure))
            self.__status_code_validation_failures.append(str(rc_failure))
            self.success = False
            raise
        except ValidationFailure as failure:
            session_success = False
            log_req_resp_details()
            # log testcase duration before raise ValidationFailure
            self.__duration = time.time() - self.__start_at
            if USE_ALLURE:
                allure.attach(str(failure), 'ValidationFailure')
            self.__validation_failures.append(str(failure))
            self.success = False
            raise
        except Exception as e:
            session_success = False
            self.__session_exceptions.append(str(e))
            self.success = False
            if USE_ALLURE:
                allure.attach('{}\n{}'.format(e, traceback.format_exc()), 'exception')
            raise
        finally:
            self.success = self.success and session_success
            step_data.success = session_success
            step_data.status = resp_obj.test_status
            step_data.blocker = resp_obj.blocker

            if hasattr(self.__session, "data"):
                # runner.core.client.HttpSession, not locust.clients.HttpSession
                # save request & response meta data
                self.__session.data.success = session_success
                self.__session.data.validators = resp_obj.validation_results
                # save step data
                step_data.data = self.__session.data

            self.__step_datas.append(step_data)

        # extract：变量提取
        extractors = step.extract
        try:
            extract_mapping = resp_obj.extract(extractors)
            step_data.export_vars = extract_mapping
        except ExtractFailure as ef:
            log_req_resp_details()
            self.__duration = time.time() - self.__start_at
            if USE_ALLURE:
                allure.attach(str(ef), 'ExtractFailure')
            self.__extract_failures.append(str(ef))
            self.success = False
            step_data.stat = resp_obj.test_status
            self.__step_datas.append(step_data)
            raise  # 如果不raise异常，变量提取失败仍然会pass

        self.__config.variables.update(extract_mapping)  # 更新步骤变量到用例配置变量
        variables_mapping.update(extract_mapping)

        return step_data

    def __run_step_testcase(self, step: TStep) -> StepData:
        """run teststep: referenced testcase"""
        step_data = StepData(name=step.name)
        step_variables = step.variables
        step_export = step.export

        # setup hooks
        if step.setup_hooks:
            self.__call_hooks(step.setup_hooks, step_variables, "setup testcase")

        if hasattr(step.testcase, "config") and hasattr(step.testcase, "teststeps"):
            testcase_cls = step.testcase
            case_result = (
                testcase_cls()
                    .with_session(self.__session)
                    .with_case_id(self.__case_id)
                    .with_variables(step_variables)
                    .with_export(step_export)
                    .run()
            )

        else:
            raise exceptions.ParamsError(
                f"Invalid teststep referenced testcase: {step.dict()}"
            )

        # teardown hooks
        if step.teardown_hooks:
            self.__call_hooks(step.teardown_hooks, step.variables, "teardown testcase")

        step_data.data = case_result.get_step_datas()  # list of step data
        step_data.export_vars = case_result.get_export_variables()
        step_data.success = case_result.success
        self.success = case_result.success

        if step_data.export_vars:
            logger.info(f"export variables: {step_data.export_vars}")

        return step_data

    def __run_step(self, step: TStep) -> StepData:
        """run teststep, teststep maybe a request or referenced testcase"""
        logger.info("Run step begin: {} {} - {} >>>>>>".format(step.sid, step.step_name, step.description))

        if step.request:
            step_data = self.__run_step_request(step)
        elif step.testcase:
            step_data = self.__run_step_testcase(step)
        else:
            raise ParamsError(
                f"teststep is neither a request nor a referenced testcase: {step.dict()}"
            )
        logger.info("Run step end: {} {} - {} <<<<<<\n".format(step.sid, step.step_name, step.description))
        return step_data

    def __parse_config(self, config: TConfig) -> NoReturn:
        config.variables.update(self.__session_variables)
        config.variables = parse_variables_mapping(
            config.variables, self.__project_meta.functions
        )
        # config.name = parse_data(
        #     config.name, config.variables, self.__project_meta.functions
        # )
        config.base_url = parse_data(
            config.base_url, config.variables, self.__project_meta.functions
        )

    def __raise_session_exception(self):
        """抛出异常，单独函数raise，避免控制台输出冗长traceback code"""
        if self.__session_exceptions:
            self.success = False
            raise Exception(json.dumps(self.__session_exceptions, indent=2, ensure_ascii=False))
        if self.__validation_failures:
            self.success = False
            if self.test_type == 'setup':
                t_type = 'Set up'
            elif self.test_type == 'teardown':
                t_type = 'Tear down'
            else:
                t_type = 'Test body'
            msg = "{} {}/{} steps assert failed!".format(t_type, len(self.__validation_failures), len(self.__teststeps))
            if self.__status_code_validation_failures:
                msg += " (status code error:{}/{})".format(
                    len(self.__status_code_validation_failures), len(self.__validation_failures))
            raise AssertionError(msg)
        if self.__extract_failures:
            self.success = False
            raise ExtractFailure(json.dumps(self.__extract_failures, indent=2, ensure_ascii=False))

    def __raise_step_exception(self, msg):
        """写异常信息到附件，并抛出步骤异常"""
        if USE_ALLURE:
            allure.attach(msg, 'exception')
        raise Exception(msg)

    def run_testcase(self, testcase: TCase) -> "FlexRunner":
        """run specified testcase

        Examples:
            >>> testcase_obj = TCase(config=TConfig(...), teststeps=[TStep(...)])
            >>> FlexRunner().with_project_meta(project_meta).run_testcase(testcase_obj)

        """
        self.__config = testcase.config
        self.__teststeps = testcase.teststeps

        # prepare
        self.__project_meta = self.__project_meta or load_project_meta(
            self.__config.path
        )
        self.__parse_config(self.__config)
        self.__start_at = time.time()
        self.__step_datas: List[StepData] = []
        self.__session = self.__session or HttpSession()
        # save extracted variables of teststeps
        extracted_variables: VariablesMapping = {}

        # run teststeps
        skipped_count = 0
        for step in self.__teststeps:
            # override variables
            # step variables > extracted variables from previous steps
            step.variables = merge_variables(step.variables, extracted_variables)
            # step variables > testcase config variables
            step.variables = merge_variables(step.variables, self.__config.variables)

            # parse variables
            step.variables = parse_variables_mapping(
                step.variables, self.__project_meta.functions
            )

            skip_msg = '跳过测试步骤：'
            skip_msg += "\nrequest:{}\n".format(step.request)
            if step.skipif:
                skip_msg += "\n{}".format(step.skipif)
            if step.is_skip:
                skip_msg += "\n测试步骤设计：跳过"
            # if not step.is_api_valid:
            #     skip_msg += "\n接口无效(status=False)"

            # 处理依赖
            depends_msg = '依赖步骤信息：'
            for depend_sid in step.depends:
                for __step_data in self.__step_datas:
                    if __step_data.sid == depend_sid:
                        depends_msg += "\nstep{}->{}-{}::{}".format(__step_data.sid, __step_data.name, __step_data.description, __step_data.stat.name)
                        if __step_data.status != TestStatusEnum.PASSED:
                            step.is_skip = True
                            break

            # run step
            try:
                if USE_ALLURE:
                    title = f"step{step.sid or step.id}({step.step_type}): {step.step_name}"
                    if step.description:
                        title += f"- {step.description}"
                    # if step.is_api_updated:
                    #     title += ":: UpdatedAPI"  # Updated API
                    # if not step.is_api_valid:
                    #     title += ":: InvalidAPI"  # Invalid API, skipped
                    #     step.is_skip = True
                    if step.is_skip:
                        skipped_count += 1
                        title += ":: Skipped"
                    with allure.step(title):
                        if step.depends:
                            allure.attach(depends_msg, 'depends')
                        if step.is_skip:
                            allure.attach(skip_msg, 'skipped')
                        step_data = self.__run_step(step)
                        extract_mapping = step_data.export_vars
                else:
                    extract_mapping = self.__run_step(step).export_vars
            except (ExtractFailure, StatusCodeValidationFailure, ValidationFailure) as e:
                logger.debug(self.test_type)
                if self.test_type in ['单接口测试']:
                    # 单接口测试，步骤之间无关联关系 遇到失败后继续执行下一步骤
                    continue
                # 场景测试，步骤直接有关联，遇到失败后退出
                raise
            except Exception as e:
                self.__session_exceptions.append(str(e))
                if self.test_type in ['单接口测试']:
                    # 单接口测试，步骤之间无关联关系 遇到失败后继续执行下一步骤
                    continue
                raise e

            # save extracted variables to session variables
            extracted_variables.update(extract_mapping)

        if skipped_count > 0 and USE_ALLURE:
            allure.dynamic.title("{}(Skipped:{})".format(testcase.description, skipped_count))

        self.__session_variables.update(extracted_variables)
        self.__duration = time.time() - self.__start_at
        self.__raise_session_exception()
        return self

    def run(self) -> "FlexRunner":
        """run current testcase"""
        self.__init_tests__()
        testcase_obj = TCase(config=self.__config, teststeps=self.__teststeps)
        return self.run_testcase(testcase_obj)

    def get_step_datas(self) -> List[StepData]:
        return self.__step_datas

    def get_export_variables(self) -> Dict:
        # override testcase export vars with step export
        export_var_names = self.__export or self.__config.export
        export_vars_mapping = {}
        for var_name in export_var_names:
            if var_name not in self.__session_variables:
                raise ParamsError(
                    f"failed to export variable {var_name} from session variables {self.__session_variables}"
                )

            export_vars_mapping[var_name] = self.__session_variables[var_name]

        return export_vars_mapping

    def get_summary(self) -> TestCaseSummary:
        """get testcase result summary"""
        start_at_timestamp = self.__start_at
        start_at_iso_format = datetime.utcfromtimestamp(start_at_timestamp).isoformat()
        return TestCaseSummary(
            success=self.success,
            id=self.__case_id,
            name=self.__config.case_name,
            description=self.__config.case_name,
            status=TestStatusEnum.PASSED if self.success else TestStatusEnum.FAILED,
            time=TestTime(
                start_at=self.__start_at,
                start_at_iso_format=start_at_iso_format,
                duration=self.__duration,
            ),
            step_datas=self.__step_datas,
            log=self.__log_path,
        )

    def __prepare_logger(self) -> NoReturn:
        """
        写用例日志到单独文件
        :return:
        """
        time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        self.__log_path = self.__log_path or os.path.join(
            self.__project_meta.RootDir,
            "test-platform/apps/api_test/runner/logs",
            f"{time_str}-{self.__config.case_name}.run.log"
        )
        # 单独写Case日志到文件
        self.__log_handlers.append(
            logger.add(
                self.__log_path,
                rotation='100 MB',
                retention='7 days',
                enqueue=True,
                encoding="utf-8",
                level=global_cf.get_str("LOGGER", "file_level") or "DEBUG"
            )
        )
        # 写日志到终端
        # self.__log_handlers.append(
        #     logger.add(sys.stdout, level=global_cf.get_str("LOGGER", "console_level"))
        # )

    def __prepare_run(self, param: Dict = None):
        self.__init_tests__()
        self.__project_meta = self.__project_meta or load_project_meta(
            self.__config.path
        )
        self.__case_id = str(self.case_id)

        # 写用例日志到单独文件
        # self.__prepare_logger()

        # parse config name
        config_variables = self.__config.variables
        if param:
            config_variables.update(param)
        config_variables.update(self.__session_variables)

        # if USE_ALLURE:
        #     # update allure report meta
        #     allure.dynamic.story(self.__config.suite_name)
        #     allure.dynamic.title(self.__config.description)
        #     allure.dynamic.description(self.__config.description)

        if self.test_type in ['setup']:
            logger.info('='*30 + ' SETUP ' + '='*30)
        elif self.test_type in ['teardown']:
            logger.info('=' * 30 + ' TEARDOWN ' + '=' * 30)
        logger.info("Start to run testcase: {}, ID: {}".format(self.__config.case_name, self.__case_id))

    def __complete_run(self):
        logger.info(f"generate testcase log: {self.__log_path}")
        # 删除log handler
        log_handlers = copy.deepcopy(self.__log_handlers)
        for log_handler in log_handlers:
            try:
                logger.remove(log_handler)
                logger.debug("删除log handler成功！handler_id:{}".format(log_handler))
                self.__log_handlers.remove(log_handler)
            except Exception as e:
                logger.debug("删除log handler失败！{}".format(e))

    def setup(self):
        """TestCase setup"""
        # setup 仅支持执行test_case，即前置用例
        # 由于class下只有一个test*，所以暂时忽略 setup
        pass

    def teardown(self):
        """TestCase teardown"""
        # teardown 仅支持执行test_case，即后置用例
        # 由于class下只有一个test*，所以暂时忽略 teardown
        pass

    def setup_class(self):
        """TestCase setup_class"""
        # setup_class 仅支持执行test_case，即前置用例
        pass

    def teardown_class(self):
        """TestCase teardown_class"""
        # setup_class 仅支持执行test_case，即后置用例
        pass

    def test_start(self, param: Dict = None) -> "FlexRunner":
        """主入口，pytest执行"""
        try:
            self.__prepare_run(param)
            return self.run_testcase(TCase(config=self.__config, teststeps=self.__teststeps))
        finally:
            # self.__complete_run()
            pass


if __name__ == '__main__':
    pass
