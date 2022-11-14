#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:config_manage.py
@time:20:03
@email:tao.xu2008@outlook.com
@description: step extend manage
"""
import os
from loguru import logger

from testrunner.utils.pkg_helper import load_pkg_by_ns


def load_steps():
    try:
        if os.environ.get("extend_pkg_list") is not None:
            extend_pkg = os.environ.get("extend_pkg_list")
            extend_pkg_list = extend_pkg.split(",")
            if len(extend_pkg_list) > 0:
                for pkg in extend_pkg_list:
                    if pkg is not None and pkg != "":
                        logger.info(f"load extend package:{pkg}")
                        load_pkg_by_ns(f"{pkg}.dsl.step")
    except Exception as load_ex:
        logger.info(f"load extend package error :f{load_ex}")
