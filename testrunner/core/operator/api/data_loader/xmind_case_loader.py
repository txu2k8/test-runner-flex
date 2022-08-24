#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:xmind_loader
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description:
"""
import re
import os

from loguru import logger
from xmindparser import xmind_to_dict

from testrunner.utils import util
from testrunner import config

PRIORITY_TAG_CHOICE = ["critical", "blocker", "normal"]


class XmindCaseLoader(object):
    """读取xmind内容，返回字典列表（list[dict1,dict2]）"""
    def __init__(self, file_path, canvas=""):
        """
        读取xmind文件内容，如果指定了画布名称，则只读取指定画布的内容
        :param file_path:
        :param canvas:
        """
        self.file_path = file_path
        self.canvas = canvas
        self.xmind_dict_list = xmind_to_dict(file_path)
        self.file_name = os.path.basename(file_path).split('.xmind')[0]
        logger.info("loading File:{0}".format(file_path))

    def get_canvas_name_list(self):
        return [self.canvas] if self.canvas else [cv.get('title') for cv in self.xmind_dict_list]

    def get_canvas_topic(self, canvas="画布 1"):
        """
        根据初始指定的画布名称（对应于excel的sheel表），返回该画布的数据
        :return: {'title': '', 'topics': []}
        """
        for cv in self.xmind_dict_list:
            if cv.get('title') == canvas:
                return cv.get('topic')
        else:
            raise Exception("Xmind中画布<{}>不存在!".format(canvas))

    def get_canvas_data(self, canvas, idx=0):
        """
        获取画布数据，画布对应test_case
        :return: {
        'api-1':[
            {'suite':'', 'name': 'case1', 'desc': '描述', 'method': 'get', 'path': '/api/xxx/s', 'data': {}, 'res': ''},
            {case2},
            ],
        'api-2': [],
        }
        """
        # 一级主题：用例描述+优先级+禅道ID
        topic_1 = self.get_canvas_topic(canvas)
        case_name = topic_1.get('title')  # 用例标题（简单描述）
        case_desc = topic_1.get('note') or case_name  # 用例详细描述
        case_labels = topic_1.get('labels')  # 1级主题-标签：优先级、用例ID

        canvas_data = {
            "id": idx,
            "case_name": case_name,
            "case_safe_name": util.to_class_name(case_name),
            'description': case_desc,
            'config': {
                "project_name": config.get_global_value("project_name"),
                "module_name": "",
                "suite_name": self.file_name
            },
            'test_type': '',
            'tags': [],
            'priority': '',
            'teststeps': [],
            'setups': [],
            'teardowns': []
        }
        for lb in case_labels:
            if re.match(r'P\d$', lb):
                canvas_data['priority'] = lb
                canvas_data['tags'].append(lb)
                continue
            case_id_lb = lb.split('case_id=')
            if len(case_id_lb) == 2:
                case_id = int(case_id_lb[1])
                canvas_data['id'] = case_id
                canvas_data['case_safe_name'] = str(case_id)
                continue
            module_lb = lb.split('module=')
            if len(module_lb) == 2:
                canvas_data['config']['module_name'] = module_lb[1]
                continue
            type_lb = lb.split('type=')
            if len(type_lb) == 2:
                canvas_data['test_type'] = type_lb[1]
                continue

        step_idx = 0
        step_list = []

        # 2级主题：接口列表
        topic_2_list = topic_1.get('topics') or []
        for idx2, api in enumerate(topic_2_list):
            # 2级主题
            api_desc = api.get('title') if api.get('title') else ""  # 2级主题-描述
            api_name = api.get('note') if api.get('note') else ""  # 2级主题-注释
            api_labels = api.get('labels')  # 2级主题-标签：depends、host、sleep
            api_dict = {
                'depends': [],
                'sleep': 0,
                'skipif': ""
            }
            if api_labels:
                for alb in api_labels:
                    lb_dps = alb.split("depends=")
                    lb_sleep = alb.split("sleep=")
                    lb_skipif = alb.split("skipif=")
                    if len(lb_dps) == 2:
                        api_dict['depends'].append(lb_dps[-1])
                    if len(lb_sleep) == 2:
                        api_dict['sleep'] = int(lb_sleep[-1])
                    if len(lb_skipif) == 2:
                        api_dict['skipif'] = lb_skipif[-1]

            # 3级主题：path+method
            topic_3 = api.get('topics')[0]
            path = topic_3.get('title') or ""  # path
            try:
                method = topic_3.get('labels')[0]  # method
            except Exception as e:
                raise Exception("3级主题：path+method，method未设置！\n".format(e))

            # 4级主题列表：步骤描述+优先级
            topic_4 = topic_3.get('topics')
            if api_name.startswith('#'):  # 被注释掉的接口，不解析用例步骤参数
                continue
            for idx4, step in enumerate(topic_4):
                step_idx += 1
                if step.get('title').startswith('#'):  # 被注释掉的用例步骤
                    continue
                logger.info("loading Canvas:{0}->API:{1}->{2} ...".format(canvas, api_desc, idx4))
                step_dict = {
                    'id': step_idx,
                    'sid': '{0}_{1}'.format(idx2+1, idx4+1),
                    'step_name': str(idx2+1).zfill(2) + f"_{api_name}_" + str(idx4+1).zfill(3),  # 步骤名称=idx2_接口名称_idx4
                    'description': "{0}（{1}）".format(api_desc, step.get('title')),  # 步骤描述= 接口描述（步骤描述）
                    'priority': 'P0'
                }
                step_dict.update(**api_dict)  # 接口信息更新到步骤中

                case_labels = step.get('labels')  # priority 优先级
                if case_labels:
                    for clb in case_labels:
                        if clb in PRIORITY_TAG_CHOICE:
                            step_dict['priority'] = clb
                            break

                # 5级主题：输入参数
                topic_5 = step.get('topics')[0]
                req_data_str = topic_5.get('title')  # 接口请求输入
                try:
                    req_data = util.json_loads(req_data_str)  # 期望输出
                except Exception as e:
                    logger.error("API:{0}->{1}\nJSON Content:{2}".format(case_desc, api_name, req_data_str))
                    raise e
                step_dict['request'] = {
                    'method': method,
                    'url': path,
                    'params': {},
                    'headers': {},
                    'req_json': {},
                    'data': {},
                    'cookies': {},
                }
                if "headers" in req_data:
                    step_dict['request']['headers'] = req_data.pop("headers")
                if "cookies" in req_data:
                    step_dict['request']['cookies'] = req_data.pop("cookies")
                if "params" in req_data:
                    step_dict['request']['params'] = req_data.pop("params")
                if "json" in req_data:
                    step_dict['request']['req_json'] = req_data.pop("json")
                if "data" in req_data:
                    step_dict['request']['data'] = req_data.pop("data")
                if "upload" in req_data:
                    pass
                    # TODO
                if req_data:
                    # 未指定参数类型
                    step_dict['request'].update({"params" if method == "GET" else "req_json": req_data})

                # 6级主题列表：期望输出+结果提取
                topic_6 = topic_5.get('topics')
                str_validators = topic_6[0].get('title')  # 6级主题 第一项为期望输出，必填
                try:
                    step_dict['validators'] = util.json_loads(str_validators)  # 期望输出
                except Exception as e:
                    logger.error("API:{0}->{1}\nJSON Content:{2}".format(case_desc, api_name, str_validators))
                    raise e

                # 6级主题 第二项为结果提取，非必填
                step_dict['extract'] = {}
                if len(topic_6) > 1:
                    extract = topic_6[1].get('title')
                    try:
                        step_dict['extract'] = util.json_loads(extract)
                    except Exception as e:
                        logger.error("API:{0}->{1}\nJSON Content:{2}".format(case_desc, api_name, extract))
                        raise e

                step_list.append(dict(step_dict))

        canvas_data['teststeps'] = step_list
        return canvas_data

    def get_xmind_data(self):
        return [self.get_canvas_data(cv) for cv in self.get_canvas_name_list()]


if __name__ == '__main__':
    from testrunner.config import BASE_DIR
    xmind = XmindCaseLoader(os.path.join(BASE_DIR, 'data/project_1/demo.xmind'))
    case_data = xmind.get_canvas_data('case-378')
    print(util.json_dumps(case_data))
