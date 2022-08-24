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
import json
import pytest
from py._xmlgen import html
from loguru import logger

from testrunner.base.models import TestStatusEnum, ReportSummary
from testrunner.cli.session import TestSession
from testrunner.libs.mysql_opt import MysqlOperation
from testrunner.libs.sqlite_opt import Sqlite3Operation


# 自定义参数
def pytest_addoption(parser):
    parser.addoption("--log_path", action="store", default="", help="自定义参数，执行日志路径")
    parser.addoption("--log_level", action="store", default="DEBUG", help="自定义参数，执行日志level")
    parser.addoption("--db_info", action="store", default="", help="自定义参数，数据库信息")
    parser.addoption("--project_name", action="store", default=None, help="自定义参数，测试项目名称")
    parser.addoption("--test_conf_path", action="store", default=None, help="自定义参数，测试配置")
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
def db_info(request):
    return request.config.getoption("--db_info")


@pytest.fixture
def project_name(request):
    return request.config.getoption("--project_name")


@pytest.fixture
def test_conf_path(request):
    return request.config.getoption("--test_conf_path")


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
    outcome = yield
    report = outcome.get_result()
    report.description = ''

    # pytest-html报告新增用例 描述 字段
    try:
        func_name = item.nodeid.split("::")[-1]
        step_idx = int(re.findall(r".*\[(\d+)\]", func_name)[0])
        steps = item.function.pytestmark[0].args[1]
        for step in steps:
            if step.idx == step_idx:
                step_desc = step.description or step.name
                break
        else:
            step_desc = item.function.__doc__
        report.description = '{}::{}'.format(item.cls.__doc__, step_desc)
    except Exception as e:
        report.description = '{}'.format(item.cls.__doc__)
    report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")  # 设置编码显示中文

    # pytest_html = item.config.pluginmanager.getplugin('html')
    # extra = getattr(report, 'extra', [])

    '''
    report_summary = {
        'case': {
            'Passed': 2,
            'Failed': 1,
            'Total': 3
        },
        'step': {
            'Passed': 2,
            'Failed': 1,
            'Error': 1,
            'Total': 4
        },
        'api': {
            '404': [
                'GET /api/path/1'
            ]
        }
    }
    '''
    # if report.when == "teardown":
    #     report_summary = get_global_value("report_summary", defaultdict(dict))
    #     summary = item.cls.case_results.summary
    #     if summary.result:
    #         report_summary['case'][summary.result] += 1
    #     for step_data in summary.step_datas:
    #         if step_data.result:
    #             report_summary['step'][step_data.result] += 1
    #         if step_data.blocker:
    #             report_summary['step'][step_data.blocker].append(step_data.data.address)
    #     logger.error("执行结果：{}".format(summary.step_datas))

    # logger.error("item：{}".format(item.keywords))
    # logger.error("item：{}".format(item.__dict__))
    # logger.error("item：{}".format(item.module))


@pytest.fixture(scope="session", autouse=True)
def session_fixture(request):
    """setup and teardown each task"""
    log_path = request.config.getoption("--log_path")
    log_level = request.config.getoption("--log_level")
    db_info = json.loads(request.config.getoption("--db_info"))
    project_name = request.config.getoption("--project_name")
    test_conf_path = request.config.getoption("--test_conf_path")
    report_id = request.config.getoption("--report_id")
    # 添加测试执行logger
    logger.add(
        log_path,
        rotation='100 MB',
        retention='7 days',
        enqueue=True,
        encoding="utf-8",
        level=log_level
    )

    logger.info(f"start running testcases ...")
    start_at = time.time()

    yield

    logger.info(f"task finished, generate task summary")
    # 连接数据库，写入测试结果
    db = None
    try:
        if db_info.get('ENGINE') == 'django.db.backends.sqlite3':
            db_path = db_info.get('DB_PATH')  # os.path.abspath(os.path.join(root_dir, '../db.sqlite3'))
            db = Sqlite3Operation(db_path, logger=logger, show=True)
        elif db_info.get('ENGINE') == 'django.db.backends.mysql':
            user = db_info.get('USER')
            password = db_info.get('PASSWORD')
            host = db_info.get('HOST')
            port = db_info.get('PORT')
            name = db_info.get('NAME')
            db = MysqlOperation(host, port, user, password, name, logger=logger, show=True)
        else:
            logger.critical("错误的数据库类型，跳过结果写入！")
    except Exception as e:
        logger.error(e)

    report_summary = ReportSummary()
    # 时间
    report_summary.time.start_at = start_at
    report_summary.time.start_at_format = datetime.datetime.utcfromtimestamp(start_at).isoformat()
    report_summary.time.duration = time.time() - start_at

    # 遍历用例
    if db:
        logger.info("更新测试结果状态到testcase+teststep表...")
    for item in request.node.items:
        testcase_summary = item.instance.get_summary()
        # 总结果：成功 | 失败
        report_summary.success = report_summary.success and testcase_summary.success
        # 用例统计
        case_info = {
            'stat': testcase_summary.status,
            'case_id': testcase_summary.id,
            'case_name': testcase_summary.name,
            'case_desc': testcase_summary.description,
            'step_id': '',
            'step_name': '',
            'step_desc': ''
        }
        report_summary.testcases_stat.total += 1
        if testcase_summary.status == TestStatusEnum.PASSED:
            report_summary.testcases_stat.passed += 1
        elif testcase_summary.status == TestStatusEnum.FAILED:
            report_summary.testcases_stat.failed += 1
            report_summary.testcases_stat.failed_list.append(case_info)
        elif testcase_summary.status == TestStatusEnum.ERROR:
            report_summary.testcases_stat.error += 1
            report_summary.testcases_stat.error_list.append(case_info)
        elif testcase_summary.status == TestStatusEnum.SKIPPED:
            report_summary.testcases_stat.skipped += 1
            report_summary.testcases_stat.skipped_list.append(case_info)
        else:
            logger.error("无效的测试结果状态！")
        # if db:
        #     data = [(testcase_summary.status.value, testcase_summary.id)]
        #     if db.__class__.__name__ == 'MysqlOperation':
        #         db.insert_update_delete('UPDATE api_test_testcase SET result = %s WHERE ID = %s', data)
        #     else:
        #         db.insert_update_delete('UPDATE api_test_testcase SET result = ? WHERE ID = ?', data)

        # 步骤统计
        step_datas = testcase_summary.step_datas
        for step_data in step_datas:
            # 步骤测试结果统计
            step_info = {
                'stat': step_data.status,
                'case_id': testcase_summary.id,
                'case_name': testcase_summary.name,
                'case_desc': testcase_summary.description,
                'step_id': step_data.id,
                'step_name': step_data.name,
                'step_desc': step_data.description,
            }
            report_summary.teststeps_stat.total += 1
            if step_data.status == TestStatusEnum.PASSED:
                report_summary.teststeps_stat.passed += 1
            elif step_data.status == TestStatusEnum.FAILED:
                report_summary.teststeps_stat.failed += 1
                report_summary.teststeps_stat.failed_list.append(step_info)
            elif step_data.status == TestStatusEnum.ERROR:
                report_summary.teststeps_stat.error += 1
                report_summary.teststeps_stat.error_list.append(step_info)
            elif step_data.status == TestStatusEnum.SKIPPED:
                report_summary.teststeps_stat.skipped += 1
                report_summary.teststeps_stat.skipped_list.append(step_info)
            else:
                logger.error("无效的测试结果状态！")
            # if db:
            #     data = [(step_data.status.value, step_data.id)]
            #     if db.__class__.__name__ == 'MysqlOperation':
            #         db.insert_update_delete('UPDATE api_test_teststep SET result = %s WHERE ID = %s', data)
            #     else:
            #         db.insert_update_delete('UPDATE api_test_teststep SET result = ? WHERE ID = ?', data)

            # 步骤请求接口阻塞统计
            if step_data.blocker:
                status_code, method, url, api_id, api_desc, test_type, dept_desc, suite_desc, case_id, case_desc, step_desc = step_data.blocker
                broken_api = {
                    "report_id": report_id,
                    "rc": status_code,
                    "method": method,
                    "url": url,
                    "api_id": api_id,
                    "api_desc": api_desc,
                    "test_type": test_type,
                    "dept_desc": dept_desc,
                    "suite_desc": suite_desc,
                    "case_id": case_id,
                    "case_desc": case_desc,
                    "step_desc": step_desc,
                    "is_bug": None,
                    "description": ""
                }
                broken_api_ids = [item['api_id'] for item in report_summary.broken_apis]
                if api_id not in broken_api_ids:
                    report_summary.broken_apis.append(broken_api)

    report_summary.status = TestStatusEnum.PASSED if report_summary.success else TestStatusEnum.FAILED

    # 结果报告路径
    test_session = TestSession(test_conf_path)
    report_summary.allure_xml_path = test_session.xml_report_path
    report_summary.html_report_path = test_session.html_report_path
    # 插入测试结果到TestReport表
    logger.info("插入测试结果到TestReport表...")
    report = {
        "build_status": 'build-status-static',  # 已执行完成
        "status": report_summary.success,
        "case_total": report_summary.testcases_stat.total,
        "case_passed": report_summary.testcases_stat.passed,
        "case_failed": report_summary.testcases_stat.failed,
        "case_skipped": report_summary.testcases_stat.skipped,
        "case_error": report_summary.testcases_stat.error,
        "case_failed_list": json.dumps(report_summary.testcases_stat.failed_list),
        "case_error_list": json.dumps(report_summary.testcases_stat.error_list),
        "case_skipped_list": json.dumps(report_summary.testcases_stat.skipped_list),
        "case_pass_rate": round(report_summary.testcases_stat.passed / (report_summary.testcases_stat.total - report_summary.testcases_stat.skipped), 3),
        "step_total": report_summary.teststeps_stat.total,
        "step_passed": report_summary.teststeps_stat.passed,
        "step_failed": report_summary.teststeps_stat.failed,
        "step_skipped": report_summary.teststeps_stat.skipped,
        "step_error": report_summary.teststeps_stat.error,
        "step_failed_list": json.dumps(report_summary.teststeps_stat.failed_list),
        "step_error_list": json.dumps(report_summary.teststeps_stat.error_list),
        "step_skipped_list": json.dumps(report_summary.teststeps_stat.skipped_list),
        "step_pass_rate": round(report_summary.teststeps_stat.passed/(report_summary.teststeps_stat.total-report_summary.teststeps_stat.skipped), 3),
        "duration": int(report_summary.time.duration),
        "allure_xml_path": report_summary.allure_xml_path,
        "html_report_path": report_summary.html_report_path,
    }

    if db:
        keys = report.keys()
        # keys_str = ','.join(keys)
        # values_str = ','.join(['%s']*len(keys)) if db.__class__.__name__ == 'MysqlOperation' else ','.join('?'*len(keys))
        # insert_sql = 'INSERT INTO api_test_testreport({}) values ({})'.format(keys_str, values_str)
        place_str = '%s' if db.__class__.__name__ == 'MysqlOperation' else '?'
        set_str = ','.join(['{}={}'.format(k, place_str) for k in keys])
        update_sql = 'UPDATE api_test_testreport SET {} WHERE id ={}'.format(set_str, report_id)
        data = [tuple(report.values())]
        db.insert_update_delete(update_sql, data)
    # ReportQWChat(report_summary).send_report()


if __name__ == '__main__':
    pass
