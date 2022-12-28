#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:main
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import os
import json
import typer
import subprocess
from loguru import logger

from testrunner.base.db import TestDB
from testrunner.base.log import LogLevelEnum, init_logger
from testrunner import config
from testrunner.global_context import GlobalContext
from testrunner.utils.util import seconds_to_hms, json_dumps


def run_pytest(context):
    """
    执行pytest
    :param context:
    :return:
    """
    # 解析pytest 文件
    test_conf = context.test_conf
    pytest_files_set = []
    for ts in test_conf.test_set_list:
        for case in ts.case_list:
            pytest_files_set.append(os.path.join(test_conf.base_path, case['location']))
    logger.info("\n{}".format(json.dumps(pytest_files_set, indent=2)))

    db_info = config.DB_INFO
    if db_info.get('ENGINE') == 'django.db.backends.sqlite3':
        db_info["DB_PATH"] = str(db_info.get('NAME'))
    elif db_info.get('ENGINE') == 'django.db.backends.mysql':
        db_info["USER"] = db_info.get('USER')
        db_info["PASSWORD"] = db_info.get('PASSWORD')
        db_info["HOST"] = db_info.get('HOST')
        db_info["PORT"] = db_info.get('PORT')
        db_info["NAME"] = db_info.get('NAME')
    # - 构建pytest 参数
    logger.info("构建pytest 参数...")
    argv = pytest_files_set + [
        '--log_path={}'.format(context.report_summary.log_path),
        '--log_level={}'.format(context.log_level),
        '-v', '-s',
        # '--show-capture=no',  # 不显示捕获日志
        '--ignore-unknown-dependency',
        '-W', 'ignore:Module already imported:pytest.PytestWarning',
        # pytest-html
        # '--html={}'.format(context().html_report_path),
        # '--self-contained-html',
        # pytest-testreport
        '--report=_{}_report_{}.html'.format(test_conf.project, context.report_summary.id),
        '--title=测试报告：{}（ID={}）'.format(test_conf.project, context.report_summary.id),
        '--template=2',
        # '--capture=sys',
        '--allure-no-capture',  # 取消添加程序中捕获到控制台或者终端的log日志或者print输出到allure测试报告的Test Body中
        '--alluredir={}'.format(context().xml_report_path), '--clean-alluredir',  # 生成allure xml结果
    ]
    # -q test_01.py
    logger.info("pytest 命令：{}\n".format(json.dumps(argv, indent=2)))

    # - 执行pytest

    # 执行方式一
    import pytest
    pytest.main(argv)
    # err_msg = ''
    # exit_code = 0

    # 执行方式二
    # p = subprocess.Popen(['pytest'] + argv)
    # p.wait()

    # - 获取结果并返回
    db = TestDB()
    filter_keys = ["status", "time", "testcases_stat", "teststeps_stat"]
    report_id = context.report_summary.id
    reports = db.get_report(report_id, filter_keys)
    if len(reports) == 0:
        raise Exception("未找到测试报告：{}".format(report_id))

    report_dict = {}
    for report in reports:
        for idx, k in enumerate(filter_keys):
            report_dict[k] = report[idx]
        break
    testcases_stat = json.loads(report_dict["testcases_stat"])
    total = testcases_stat["total"]
    passed = testcases_stat["passed"]
    failed = testcases_stat["failed"]
    error = testcases_stat["error"]
    skipped = testcases_stat["skipped"]
    pass_rate = round((passed+skipped)/total if total > 0 else 0, 3)

    time_dict = json.loads(report_dict["time"])
    duration = time_dict["duration"]

    summary = {
        "status": report_dict["status"],
        "total": total,
        "passed": passed,
        "failed": failed,
        "error": error,
        "skipped": skipped,
        "pass_rate": "{}%".format(pass_rate * 100),
        "duration": seconds_to_hms(duration,)
    }
    logger.info("测试结果：\n{}".format(json_dumps(summary)))
    return report_id, summary


def generate_allure_report(context):
    """
    从测试报告中读取测试结果数据，生成allure报告。
    服务器运行：通过Jenkins生成allure报告
    本地运行：allure serve命令立即生成allure报告
    :param context:
    :return:
    """
    try:
        logger.info("generate allure report...")
        # 本地调试
        allure_serve_cmd = 'D:\\allure-2.20.1\\bin\\allure serve {}'.format(context.report_summary.report_allure_path)
        logger.info(allure_serve_cmd)
        subprocess.Popen(allure_serve_cmd, shell=True, close_fds=True)
        # p.wait()
    except Exception as e:
        logger.error(e)


def main(
    test_conf_path: str = typer.Option(
            "./demo/conf/demo.xml",
            "--test_conf_path",
            "-f",
            help="配置文件路径，对应目录：./{$project}/conf/{$test_conf}",
        ),
    loglevel: LogLevelEnum = typer.Option(LogLevelEnum.INFO, help="日志等级"),
):
    """FlexRunner 命令行 CLI"""
    init_logger(prefix='test', loglevel=loglevel)
    test_conf_path = os.path.abspath(os.path.join(config.BASE_DIR, test_conf_path))
    logger.info("执行 {}".format(test_conf_path))

    # 参数解析
    GlobalContext.test_conf_path = test_conf_path
    GlobalContext().init_data()

    # - 执行 pytest
    try:
        return run_pytest(GlobalContext)
    except Exception as e:
        raise e
    finally:
        logger.info("test log: {}".format(GlobalContext.log_path))
        logger.info("result data: {}".format(GlobalContext.xml_report_path))
        generate_allure_report(GlobalContext)


if __name__ == '__main__':
    typer.run(main)
