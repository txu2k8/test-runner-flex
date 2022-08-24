#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:xml_parse
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description: xml配置文件解析
"""
import json
import os
import re
import pathlib
from xml.etree import ElementTree
from loguru import logger

from testrunner.base.models import TestConf, Testbed, TestSet, TestEnv


class ConfigXml(object):
    """测试配置文件 xml解析"""
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.xml_path_posix = pathlib.Path(self.xml_path).as_posix()
        self.base_path = self.xml_path_posix.split('conf')[0]

    @property
    def project(self):
        rtn = re.findall(r'data/(.*)/conf', self.xml_path_posix)
        if len(rtn) > 0:
            project_name = rtn[0]
        else:
            raise Exception("项目名称解析失败：{}".format(self.xml_path))
        return project_name

    @staticmethod
    def parse_testbed(testbed_xml_path):
        """
        解析测试床配置文件 testbed
        :param testbed_xml_path:
        :return:
        """
        tree = ElementTree.parse(testbed_xml_path)
        testbed = tree.getroot()
        desc = testbed.attrib['desc']
        name = testbed.attrib['name']
        env_conf_list = []
        for env in testbed:
            # env
            env_conf = {}
            for child in env:
                # nodes
                if child.tag == "nodes":
                    env_conf['node_list'] = []
                    for node in child:
                        env_conf['node_list'].append(node.attrib)
                    continue
                # params
                elif child.tag == 'params':
                    env_conf[child.tag] = {}
                    for p in child:
                        env_conf[child.tag][p.tag] = p.text
                    continue
                # 其他
                env_conf[child.tag] = child.text

            env_conf_list.append(env_conf)

        tb = Testbed(
            xml_path=testbed_xml_path,
            name=name,
            description=desc,
            env_list=env_conf_list
        )
        # logger.debug("testbed: {}".format(json.dumps(tb.dict(), indent=2)))
        return tb

    @staticmethod
    def parse_test_set(test_set_xml_path):
        tree = ElementTree.parse(test_set_xml_path)
        test_set = tree.getroot()
        desc = test_set.attrib['desc']
        case_conf_list = []
        for case in test_set:
            case_conf_list.append(case.attrib)

        ts = TestSet(
            xml_path=test_set_xml_path,
            description=desc,
            case_list=case_conf_list
        )
        # logger.debug("test_set: {}".format(json.dumps(ts.dict(), indent=2)))
        return ts

    def parse_test_conf(self) -> TestConf:
        """
        解析测试配置文件
        :return:
        """
        # logger.debug(self.xml_path)
        tree = ElementTree.parse(self.xml_path)
        test_conf = tree.getroot()
        description = test_conf.attrib['desc']
        conf = {}
        testbed = {}
        test_set_list = []
        for child in test_conf:
            conf[child.tag] = child.text
            if child.tag == 'testset':
                test_set = self.parse_test_set(os.path.join(self.base_path, child.text))
                test_set_list.append(test_set)
                continue
            elif child.tag == 'testbed':
                testbed = self.parse_testbed(os.path.join(self.base_path, child.text))
                continue
        logger.debug(conf)

        tf = TestConf(
            project=self.project,
            base_path=self.base_path,
            full_path=self.xml_path,  # self.xml_path_posix
            description=description,
            testbed=testbed,
            test_set_list=test_set_list
        )
        # logger.debug("test_conf: {}".format(json.dumps(tf.dict(), indent=2)))
        return tf


if __name__ == '__main__':
    xtc = ConfigXml(r"D:\workspace\test-platform-flex\tpRunner\data\project1\conf\demo.xml")
    tc = xtc.parse_test_conf()
    print(tc.dict())
