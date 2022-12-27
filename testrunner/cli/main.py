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
from testrunner.utils.util import rm_tree, seconds_to_hms, json_dumps
from testrunner.core.runners.api.data_loader import load_testcase

# from django.conf import settings
# from applications.base_app.models import TestReport


def _rm_rotation_files(project_name):
    """
    删除指定项目的历史运行数据（日志、报告、临时用例） --max rotation
    :param project_name:
    :return:
    """
    tc_max_rotation = config.MAX_ROTATION
    testcase_path = os.path.join(config.TESTCASE_DIR, project_name)
    log_path = os.path.join(config.LOG_DIR, project_name)
    report_path = os.path.join(config.REPORT_DIR, project_name)

    # - 删除旧的测试构建文件
    # testcase/test_*
    rm_tree(testcase_path, "test_*", max_rotation=tc_max_rotation)
    # reports/*
    rm_tree(log_path, "*", max_rotation=tc_max_rotation)
    # logs/runner/*
    rm_tree(report_path, "*", max_rotation=tc_max_rotation)
    return True


def _load_testcase_data(test_conf_path_list):
    """
    根据测试配置文件路径，递归加载数据，生成用例数据列表
    :param test_conf_path_list:
    :return:用例数据列表
    """
    logger.info('加载用例数据（配置文件驱动）'.center(70, '>'))
    try:
        data_subdir_list = test_conf_path_list or [None]
        data_list = load_testcase(config.DATA_DIR, data_subdir_list)
    except Exception as e:
        raise e
    return data_list


def _conf2case(test_conf_path_list, testcase_path):
    """
    1、根据测试配置文件路径，递归加载数据，生成用例数据列表
    2、根据用例数据列表，构造生成pytest测试用例文件：*.py
    :param testcase_path:
    :return:
    """
    from testrunner.core.runners.api.maker import main_make

    # - 加载、解析用例数据
    tc_data_list = _load_testcase_data(test_conf_path_list)
    # - 生成测试py文件
    logger.info("生成测试pytest文件...")
    pytest_files_run_set = main_make(tc_data_list, testcase_path)
    len_pytest_files = len(pytest_files_run_set)
    logger.info("待执行pytest用例文件({})：\n".format(len_pytest_files, json_dumps(pytest_files_run_set)))
    if len_pytest_files == 0:
        logger.error("无测试用例被构造！")
    return pytest_files_run_set


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
    logger.debug("\n{}".format(json.dumps(pytest_files_set, indent=2)))

    # - 获取数据库信息，并传入pytest
    # default_db = settings.DATABASES.get('default')
    # db_info = {
    #     "ENGINE": default_db.get('ENGINE'),
    #     "DB_PATH": "",
    #     "USER": "",
    #     "PASSWORD": "",
    #     "HOST": "",
    #     "PORT": "",
    #     "NAME": "",
    # }
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
        '-v', '--ignore-unknown-dependency',  # '-s',
        '-W', 'ignore:Module already imported:pytest.PytestWarning',
        '--html={}'.format(context().html_report_path),
        '--self-contained-html',
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
    project_name: str = typer.Option(
            "demo",
            "--project",
            "-p",
            help="项目名称，对应目录：./{$project}"
        ),
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
    logger.info("执行 {}::{}".format(project_name, test_conf_path))

    # 参数解析
    GlobalContext.test_conf_path = test_conf_path
    GlobalContext.get_test_conf()
    GlobalContext.set_env(GlobalContext.test_conf.testbed.env_list[0])

    # - 删除旧的测试构建文件
    # _rm_rotation_files(project_name)

    # - 执行 pytest
    return run_pytest(GlobalContext)


if __name__ == '__main__':
    typer.run(main)
