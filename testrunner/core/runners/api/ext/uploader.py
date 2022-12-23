#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:uploader
@time:2022/04/03
@email:tao.xu2008@outlook.com
@description: 扩展支持 - 上传文件
"""

import os
from typing import Text, NoReturn

from loguru import logger
from testrunner.config import BASE_DIR
from testrunner.core.runners.api.models import TStep, FunctionsMapping
from testrunner.core.runners.api.parser import parse_variables_mapping

try:
    import filetype
    from requests_toolbelt import MultipartEncoder

    UPLOAD_READY = True
except ModuleNotFoundError:
    UPLOAD_READY = False


def ensure_upload_ready():
    if UPLOAD_READY:
        return

    msg = """
    需要安装uploader依赖包：requests_toolbelt和filetype
    install with pip:
    $ pip install requests_toolbelt filetype
    """
    logger.error(msg)
    raise Exception(msg)


def prepare_upload_step(step: TStep, functions: FunctionsMapping) -> "NoReturn":
    """ preprocess for upload test
        replace `upload` info with MultipartEncoder

    Args:
        step: teststep
            {
                "variables": {},
                "request": {
                    "url": "http://httpbin.org/upload",
                    "method": "POST",
                    "headers": {
                        "Cookie": "session=AAA-BBB-CCC"
                    },
                    "upload": {
                        "file": "data/file_to_upload"
                        "md5": "123"
                    }
                }
            }
        functions: functions mapping

    """
    if not step.request.upload:
        return

    ensure_upload_ready()
    params_list = []
    for key, value in step.request.upload.items():
        step.variables[key] = value
        params_list.append(f"{key}=${key}")

    params_str = ", ".join(params_list)
    step.variables["m_encoder"] = "${multipart_encoder(" + params_str + ")}"

    # parse variables
    step.variables = parse_variables_mapping(step.variables, functions)

    step.request.headers["Content-Type"] = "${multipart_content_type($m_encoder)}"

    step.request.data = "$m_encoder"


def multipart_encoder(**kwargs):
    """
    初始化MultipartEncoder
    :param kwargs:
    :return: MultipartEncoder对象
    """

    def get_filetype(file_path):
        file_type = filetype.guess(file_path)
        if file_type:
            return file_type.mime
        else:
            return "text/html"

    ensure_upload_ready()
    fields_dict = {}
    for key, value in kwargs.items():
        _file_path = os.path.join(BASE_DIR, value)
        is_exists_file = os.path.isfile(value)
        if is_exists_file:
            # value：待上传的文件
            filename = os.path.basename(_file_path)
            mime_type = get_filetype(_file_path)
            # TODO: 这里文件句柄打开后，未关闭
            file_handler = open(_file_path, "rb")
            fields_dict[key] = (filename, file_handler, mime_type)
        else:
            # value：其他变量参数
            fields_dict[key] = value

    return MultipartEncoder(fields=fields_dict)


def multipart_content_type(m_encoder) -> Text:
    """
    准备请求头 Content-Type
    :param m_encoder:
    :return: Content-Type内容
    """
    ensure_upload_ready()
    return m_encoder.content_type


if __name__ == '__main__':
    pass
