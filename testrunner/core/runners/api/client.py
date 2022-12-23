#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:client
@time:2022/08/21
@email:tao.xu2008@outlook.com
@description:
"""
import json
import time
try:
    import allure
    USE_ALLURE = True
except ModuleNotFoundError:
    USE_ALLURE = False

from loguru import logger as default_logger
from prettytable import PrettyTable
import urllib3
from requests import Session, Request, Response
from requests.exceptions import (
    InvalidSchema,
    InvalidURL,
    MissingSchema,
    RequestException,
)

from testrunner.core.runners.api.models import RequestData, ResponseData, ReqRespData, SessionData
from testrunner.utils.util import lower_dict_keys, omit_long_data

# 禁用InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ApiResponse(Response):
    def raise_for_status(self):
        if hasattr(self, "error") and self.error:
            raise self.error
        Response.raise_for_status(self)


# 从响应对象获取到请求和响应信息
def get_req_resp_data(resp_obj: Response, logger=default_logger) -> ReqRespData:
    """
    get request and response info from Response() object.
    :param resp_obj:
    :param logger:
    :return:
    """

    def log_print(req_or_resp, r_type):
        msg = f"\n================== {r_type} details ==================\n"
        for key, value in req_or_resp.dict().items():
            if isinstance(value, dict) or isinstance(value, list):
                value = json.dumps(value, indent=4, ensure_ascii=False)

            msg += "{:<8} : {}\n".format(key, value)
        logger.debug(msg)
        if USE_ALLURE:
            allure.attach(msg, r_type)

    # record actual request info
    request_headers = dict(resp_obj.request.headers)
    request_cookies = resp_obj.request._cookies.get_dict()

    request_body = resp_obj.request.body
    if request_body is not None:
        try:
            request_body = json.loads(request_body)
        except json.JSONDecodeError:
            # str: a=1&b=2
            pass
        except UnicodeDecodeError:
            # bytes/bytearray: request body in protobuf
            pass
        except TypeError:
            # neither str nor bytes/bytearray, e.g. <MultipartEncoder>
            pass

        request_content_type = lower_dict_keys(request_headers).get("content-type")
        if request_content_type and "multipart/form-data" in request_content_type:
            # upload file type
            request_body = "upload file stream (OMITTED)"

    request_data = RequestData(
        method=resp_obj.request.method,
        url=resp_obj.request.url,
        headers=request_headers,
        cookies=request_cookies,
        body=request_body,
    )

    # log request details in debug mode
    log_print(request_data, "request")

    # record response info
    resp_headers = dict(resp_obj.headers)
    lower_resp_headers = lower_dict_keys(resp_headers)
    content_type = lower_resp_headers.get("content-type", "")

    if "image" in content_type:
        # response is image type, record bytes content only
        response_body = resp_obj.content
    else:
        try:
            # try to record json data
            response_body = resp_obj.json()
        except ValueError:
            # only record at most 512 text charactors
            resp_text = resp_obj.text
            response_body = omit_long_data(resp_text)

    response_data = ResponseData(
        status_code=resp_obj.status_code,
        cookies=resp_obj.cookies or {},
        encoding=resp_obj.encoding,
        headers=resp_headers,
        content_type=content_type,
        body=response_body,
    )

    # log response details in debug mode
    log_print(response_data, "response")

    req_resp_data = ReqRespData(request=request_data, response=response_data)
    return req_resp_data


class HttpSession(Session):
    """
    Class for performing HTTP requests and holding (session-) cookies between requests (in order
    to be able to log in and out of websites). Each request is logged so that HttpRunner can
    display statistics.

    This is a slightly extended version of `python-request <http://python-requests.org>`_'s
    :py:class:`requests.Session` class and mostly this class works exactly the same.
    """

    def __init__(self, logger=default_logger):
        super(HttpSession, self).__init__()
        self.data = SessionData()
        self.logger = logger
        self.step_table = []  # [('描述', 'Method', 'URL', 'Result')]

    def print_step_table(self, ps=""):
        field_names = ['序号', '描述', 'Method', 'URL', 'Result']
        p_table = PrettyTable(field_names)
        p_table.align['序号'] = 'l'
        p_table.align['描述'] = 'l'
        p_table.align['Method'] = 'l'
        p_table.align['URL'] = 'l'
        for idx, step in enumerate(self.step_table):
            p_table.add_row((idx + 1, *step))
        self.logger.info("{}测试请求列表:\n{}".format(ps, p_table))
        return True

    def request(self, method, url, **kwargs):
        """
        接口请求
        :param method:
        :param url:
        :param kwargs:
        :return:
        """
        self.data = SessionData()

        # timeout default to 120 seconds
        kwargs.setdefault("timeout", 120)

        # set stream to True, in order to get client/server IP/Port
        kwargs["stream"] = True
        self.logger.info("{} {}".format(method, url))
        start_timestamp = time.time()
        response = self._send_request_safe_mode(method, url, **kwargs)
        response_time_ms = round((time.time() - start_timestamp) * 1000, 2)

        # get length of the response content
        content_size = int(dict(response.headers).get("content-length") or 0)

        # record the consumed time
        self.data.stat.response_time_ms = response_time_ms
        self.data.stat.elapsed_ms = response.elapsed.microseconds / 1000.0
        self.data.stat.content_size = content_size

        # record request and response histories, include 30X redirection
        response_list = [response]  # response.history + [response]
        self.data.req_resp_datas = [
            get_req_resp_data(resp_obj, self.logger) for resp_obj in response_list
        ]

        try:
            response.raise_for_status()
        except RequestException as ex:
            self.logger.error(f"{str(ex)}")
        else:
            self.logger.info(
                f"status_code: {response.status_code}, "
                f"response_time(ms): {response_time_ms} ms, "
                f"response_length: {content_size} bytes"
            )

        return response

    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send a HTTP request, and catch any exception that might occur due to connection problems.
        Safe mode has been removed from requests 1.x.
        """
        try:
            return Session.request(self, method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL):
            raise
        except RequestException as ex:
            resp = ApiResponse()
            resp.error = ex
            resp.status_code = 0  # with this status_code, content returns None
            resp.request = Request(method, url).prepare()
            return resp


if __name__ == '__main__':
    pass
