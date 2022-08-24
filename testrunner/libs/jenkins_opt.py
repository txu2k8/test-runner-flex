#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:jenkins_opt
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description:
"""
import unittest

import jenkins
from loguru import logger as default_logger
# from common.singleton import Singleton


JENKINS_URL = 'http://10.99.145.123:6666/'
JENKINS_USER = 'tester'
JENKINS_PWD = 'Abcd1234'


class JenkinsOperation(object):
    """Jenkins操作"""

    def __init__(self, url=JENKINS_URL, user=JENKINS_USER, password=JENKINS_PWD, logger=default_logger):
        self.url = url
        self.user = user
        self.password = password
        self.logger = logger
        self.conn = None
        self.connect()

    def connect(self):
        try:
            self.conn = jenkins.Jenkins(self.url, username=self.user, password=self.password)
            self.logger.info("Jenkins server available")
        except Exception as e:
            self.logger.error("Jenkins server not available")
            raise e

    def get_next_build_number(self, job_name):
        job_info = self.conn.get_job_info(job_name)
        last_build_number = job_info['lastBuild']['number']
        return last_build_number+1

    def get_build_allure_url(self, job_name, build_number):
        build_info = self.conn.get_build_info(job_name, build_number)
        allure_url = build_info['url'] + "allure"
        return allure_url

    def set_next_build_number(self, job_name, build_number):
        return self.conn.set_next_build_number(job_name, build_number)

    def trigger_build_job(self, name, parameters=None, token=None):
        number = self.conn.build_job(name, parameters, token)
        return number


class JenkinsTestCase(unittest.TestCase):
    """docstring for Jenkins"""

    def test_1(self):
        """测试读取表"""
        jks = JenkinsOperation(JENKINS_URL, JENKINS_USER, JENKINS_PWD)
        allure_url = jks.get_build_allure_url('api_test_report', 105)
        print(allure_url)
        parameters = {
            'allure_results': "ssssxxxxxxx"
        }
        number = jks.trigger_build_job('api_test_report', parameters,
                                       token='api_test_allure_report_GwNyLBEvbOZpmbWailbUwyEqqKhx1SkP')
        allure_url = jks.get_build_allure_url('api_test_report', number)
        print(allure_url)


if __name__ == '__main__':
    pass
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(JenkinsTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
