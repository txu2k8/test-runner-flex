#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:conftest
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description:
"""
import re
import time
import datetime
import pytest
from py._xmlgen import html
from loguru import logger

from testrunner.base.log import AllureLogger
from testrunner.base.db import TestDB
from testrunner.global_context import GlobalContext
from testrunner.base.models import TestStatusEnum, ReportSummary


# 自定义参数
def pytest_addoption(parser):
    parser.addoption("--log_path", action="store", default="", help="自定义参数，执行日志路径")
    parser.addoption("--log_level", action="store", default="DEBUG", help="自定义参数，执行日志level")
    parser.addoption("--report_id", action="store", default=None, help="自定义参数，测试报告ID")


@pytest.fixture
def time_str(request):
    return request.config.getoption("--time_str")


@pytest.fixture
def log_path(request):
    return request.config.getoption("--log_path")


@pytest.fixture
def log_level(request):
    return request.config.getoption("--log_level")


@pytest.fixture
def report_id(request):
    return request.config.getoption("--report_id")


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Description'))


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    try:
        cells.insert(1, html.td(report.description))
    except Exception as e:
        cells.insert(1, html.td(str(e)))
        logger.error(e)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    标记测试结果到 BaseAPI().step_table
    :param item:
    :param call:
    :return:
    """
    out = yield
    report = out.get_result()
    report.description = ''
    logger.trace('⋙ 测试报告：%s' % report)
    logger.trace('⋙ 步骤：%s' % report.when)
    logger.trace('⋙ nodeid：%s' % report.nodeid)
    logger.trace('⋙ description:%s' % str(item.function.__doc__))
    logger.trace(('⋙ 运行结果: %s' % report.outcome))

    if report.when == "setup" and report.outcome == "failed":
        GlobalContext.add_case_skipped(case=item.function.__doc__)
    elif report.when == "teardown" and report.outcome == "passed":
        GlobalContext.add_case_passed()


@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    """setup and teardown each task"""
    log_path = request.config.getoption("--log_path")
    log_level = request.config.getoption("--log_level")
    # 添加测试执行logger
    logger.add(
        log_path,
        rotation='100 MB',
        retention='7 days',
        enqueue=True,
        encoding="utf-8",
        level=log_level
    )

    logger.info(f"📌 Start running testcases ...")
    # 开始时间
    start_at = time.time()
    GlobalContext.report_summary.time.start_at = start_at
    GlobalContext.report_summary.time.start_at_format = datetime.datetime.utcfromtimestamp(start_at).isoformat()
    logger.info("📌 setup 前置操作")

    yield
    logger.info("📌 teardown 后置操作")

    logger.info(f"📌 Task finished, update test report summary...")
    # 连接数据库，写入测试结果
    try:
        db = TestDB()
    except Exception as e:
        logger.error(e)
        db = None

    # 结束时间
    end_at = time.time()
    GlobalContext.report_summary.time.duration = end_at - start_at

    # 总体结果
    testcases_stat = GlobalContext.report_summary.testcases_stat
    if testcases_stat.total == (testcases_stat.passed + testcases_stat.skipped):
        GlobalContext.report_summary.status = TestStatusEnum.PASSED
    else:
        GlobalContext.report_summary.status = TestStatusEnum.FAILED

    # 插入测试结果到TestReport表
    if db:
        logger.info("📌 更新测试结果到TestReport表...")
        update_keys = [
            "success", "status", "time", "testcases_stat", "teststeps_stat",
            "log_path", "report_allure_path", "report_html_path",
            "jenkins_job_name", "jenkins_build_number", "allure_url", "build_type", "build_status",
            "env_id"
        ]
        db.update_testreport(GlobalContext.report_summary, filter_keys=update_keys)

    # 发送测试报告到邮件 TODO
    logger.info("📌 发送测试报告到邮件...（TODO）")


if __name__ == '__main__':
    pass
