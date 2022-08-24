#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:case_loader
@time:2022/04/05
@email:tao.xu2008@outlook.com
@description:
"""
import os
from loguru import logger

from testrunner.config import TESTCASE_DIR
from testrunner.core.operator.api.data_loader.xmind_case_loader import XmindCaseLoader
from testrunner.core.operator.api.data_loader.csv_case_loader import CSVCaseLoader

supported_f_type = (
    ".xmind",
    ".xlsx",
    ".xls",
    ".csv",
)


class CaseLoader(object):
    """递归遍历用例设计文件目录，读取case数据"""
    def __init__(self, case_path: str, sub_dir=""):
        self.case_path = case_path
        if sub_dir:
            self.case_path = os.path.join(case_path, sub_dir)

    def get_all_case_files(self, f_types=supported_f_type) -> list:
        """
        返回cases 路径下全部case文件列表
        :return:
        """
        files_path = []
        if not os.path.isdir(self.case_path):
            logger.warning("{}路径不存在！！！".format(self.case_path))
            return files_path
        for file_name in os.listdir(self.case_path):
            for f_type in f_types:
                if file_name.lower().endswith(f_type):
                    f_path = os.path.join(self.case_path, file_name)
                    logger.info(f_path)
                    files_path.append(f_path)
        return files_path

    def get_all_case_files_recursion(self, f_types=supported_f_type) -> list:
        """
        返回cases 路径下全部case文件列表
        :return:
        """
        files_path = []
        if not os.path.isdir(self.case_path):
            logger.warning("{}: 路径不存在！！！".format(self.case_path))
            return files_path
        for root, dirs, files in os.walk(self.case_path):
            for file_name in files:
                for f_type in f_types:
                    if file_name.lower().endswith(f_type):
                        f_path = os.path.join(root, file_name)
                        logger.info(f_path)
                        files_path.append(f_path)
        return files_path

    @staticmethod
    def load_file_case_data(file_path: str) -> list:
        """
        读取case配置文件中的case信息 --xmind
        :param file_path: case配置文件路径
        :return:xmind中的case信息
        """
        if file_path.endswith(".xmind"):
            return XmindCaseLoader(file_path).get_xmind_data()
        elif file_path.endswith(".xlsx") or file_path.endswith(".xls") or file_path.endswith(".csv"):
            return CSVCaseLoader(file_path).get_csv_data()

    def load(self) -> list:
        """
        遍历测试用例配置文件，并为每个文件构造完整的测试用例信息集合
        :return:
        """
        for file in self.get_all_case_files_recursion():
            d, f = os.path.split(file)
            pd, pf = os.path.split(d)
            sf = f.split('.')[0].replace("-", "_")
            if TESTCASE_DIR == pd:
                suite_name = "{0}_{1}".format(pf, sf)
            else:
                suite_name = sf
            # {'suite': [{'case1':''}]}
            suite_data = {suite_name: self.load_file_case_data(file)}
            # logger.warning(json.dumps(suite_data, indent=2))
            yield suite_data


def load_testcase(root_data_dir: str, data_sub_dirs: list):
    case_data_list = []
    idx = 0
    for sub_dir in data_sub_dirs:
        logger.warning(root_data_dir)
        for item in CaseLoader(root_data_dir, sub_dir).load():
            for suite_name, suite_data in item.items():
                idx += 1
                case_data_list.append({
                    "id": idx,
                    "suite_name": suite_name,
                    "config": {
                        'base_url': 'http://httpbin.org/'
                    },
                    "testcases": suite_data,
                    "setup_tcs": [],
                    "teardown_tcs": [],
                    "setup_class_tcs": [],
                    "teardown_class_tcs": [],
                })
    return case_data_list


if __name__ == '__main__':
    from testrunner.config import BASE_DIR
    data_list = load_testcase(os.path.join(BASE_DIR, 'data/'), ['project_1'])
    print(data_list)
