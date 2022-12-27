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
from loguru import logger

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
        '--log_path={}'.format(context().html_report_path),
        '--log_level={}'.format(context.log_level),
        '--db_info={}'.format(json_dumps(db_info)),
        '--project_name={}'.format(test_conf.project),
        '--test_conf_path={}'.format(test_conf.full_path),
        '--report_id={}'.format(context.report_id),
        '-v', '-s',
        # '--show-capture=no',  # 不显示捕获日志
        '--ignore-unknown-dependency',
        '-W', 'ignore:Module already imported:pytest.PytestWarning',
        # pytest-html
        # '--html={}'.format(context().html_report_path),
        # '--self-contained-html',
        # pytest-testreport
        '--report=_{}_report_{}.html'.format(test_conf.project, context.report_id),
        '--title=测试报告：{}（ID={}）'.format(test_conf.project, context.report_id),
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

    return
    # - 获取结果并返回
    reports = TestReport.objects.filter(id=test_session.report_id)
    if reports.count() == 0:
        raise Exception("未找到测试报告：{}".format(test_session.report_id))

    report = reports.first()
    report_id = report.id

    summary = {
        "status": report.status,
        "total": report.step_total,
        "pass": report.step_passed,
        "failed": report.step_failed,
        "error": report.step_error,
        "skipped": report.step_skipped,
        "pass_rate": "{}%".format(report.step_pass_rate * 100),
        "duration": seconds_to_hms(report.duration)
    }
    return report_id, summary


def main(
    test_conf_path: str = typer.Option(
            "./demo/conf/demo.xml",
            "--test_conf_path",
            "-f",
            help="配置文件路径，对应目录：./{$project}/conf/{$test_conf}",
        ),
    loglevel: LogLevelEnum = typer.Option(LogLevelEnum.TRACE, help="日志等级"),
):
    """FlexRunner 命令行 CLI"""
    init_logger(prefix='test', loglevel=loglevel)
    test_conf_path = os.path.abspath(os.path.join(config.BASE_DIR, test_conf_path))
    logger.info("执行 {}".format(test_conf_path))

    # 参数解析
    GlobalContext.test_conf_path = test_conf_path
    GlobalContext().init_data()

    # - 执行 pytest
    return run_pytest(GlobalContext)


if __name__ == '__main__':
    typer.run(main)
