#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:qw_chat
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 发送测试结果消息，概览
"""
import requests
from loguru import logger

from tpRunner.base_models import ReportSummary

# 企微群机器人key
QW_TEST_KEY = 'c6ca03de-d689-4ab8-bd3b-421682501a77'  # 测试群
QW_DEV_KEY = 'dd9446c9-4d1a-4adb-99db-194ffa0d7279'  # 研发群


class ReportQWChat(object):
    """发送测试结果到企业微信群"""

    def __init__(self, summary: ReportSummary = ReportSummary()):
        self.summary = summary

    @property
    def report_text_content(self):
        def _stat_msg(stat):
            stat_msg = ''
            for k, v in stat.__dict__.items():
                if k == 'total':
                    stat_msg = '{}:{}'.format(k, v) + stat_msg
                elif v > 0:
                    stat_msg += ', {}:{}'.format(k, v)
            return stat_msg

        def _blocker_msg(broken_apis):
            broken_apis = sorted(broken_apis, key=lambda x: x['rc'])
            blocker_msg = '\n' if broken_apis else ''
            for idx, broken_api in enumerate(broken_apis):
                blocker_msg += "{}. {}:{} {}".format(idx+1, broken_api['rc'], broken_api['method'], broken_api['url'])
            return blocker_msg

        content = "测试构建执行完成 - {}\n".format(self.summary.status.value)
        content += "测试用例：{}\n".format(_stat_msg(self.summary.testcases_stat))
        content += "测试步骤：{}\n".format(_stat_msg(self.summary.teststeps_stat))

        content += "故障接口：{}".format(_blocker_msg(self.summary.broken_apis))
        return content

    @property
    def default_data(self):
        data = {
            "msgtype": "text",
            "text": {
                "content": self.report_text_content
            }
        }
        return data

    def send_report(self, data: dict = None, qw_robot_key_list=None):
        """
        发送企微群消息通知
        :return:
        """
        if qw_robot_key_list is None:
            qw_robot_key_list = [QW_TEST_KEY]  # QW_DEV_KEY
        if data is None:
            data = self.default_data
        headers = {'Content-Type': 'application/json'}
        logger.debug(data)
        for qw_robot_key in qw_robot_key_list:
            url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + qw_robot_key
            try:
                res = requests.post(url, json=data, headers=headers)  # 群消息通知
                print(res.json())
            except Exception as e:
                print(e)


if __name__ == '__main__':
    pass
