#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:life_cycle.py
@time:2022/11/14
@email:tao.xu2008@outlook.com
@description: plugin load and destroy
"""

from testrunner.core.global_context import GlobalContext

__import__("testrunner.core.plugin.loader")


def load(context):
    """
    load plugin
    """
    GlobalContext.process("plugin_processor", context)


def destroy(context):
    """
    destroy plugin
    """
    raise Exception("not implement destroy")
