#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:runner
@time:2022/12/26
@email:tao.xu2008@outlook.com
@description: 
"""
import time
from unittest import TestCase
from urllib.parse import unquote

from loguru import logger
from prettytable import PrettyTable
from selenium.webdriver.common.by import By

from testrunner.base.models import StepType
from testrunner.global_context import GlobalContext
from testrunner.core.runners.web.exceptions import NotFindElementError
from testrunner.core.runners.web.webdriver import WebDriver


class WebRunner(TestCase, WebDriver):
    """Web测试执行引擎入口"""
    step_type = StepType.WEB.value  # 约定：指定测试类型，meta_class.py step需要使用

    def assertTitle(self, title: str = None, msg: str = None) -> None:
        """断言：当前页面title为指定字符串
        Asserts whether the current title is in line with expectations.

        Usage:
        self.assertTitle("title")
        """
        if title is None:
            raise AssertionError("The assertion title cannot be empty.")

        logger.info(f"👀 assertTitle -> {title}.")
        for _ in range(GlobalContext.timeout + 1):
            try:
                self.assertEqual(title, GlobalContext.driver.title)
                break
            except AssertionError:
                time.sleep(1)
        else:
            self.assertEqual(title, GlobalContext.driver.title, msg=msg)

    def assertInTitle(self, title: str = None, msg: str = None) -> None:
        """断言：当前页面title包含指定字符串
        Asserts whether the current title is in line with expectations.

        Usage:
        self.assertInTitle("title")
        """
        if title is None:
            raise AssertionError("The assertion title cannot be empty.")

        logger.info(f"👀 assertInTitle -> {title}.")
        for _ in range(GlobalContext.timeout + 1):
            try:
                self.assertIn(title, GlobalContext.driver.title)
                break
            except AssertionError:
                time.sleep(1)
        else:
            self.assertIn(title, GlobalContext.driver.title, msg=msg)

    def assertUrl(self, url: str = None, msg: str = None) -> None:
        """
        Asserts whether the current URL is in line with expectations.

        Usage:
        self.assertUrl("url")
        """
        if url is None:
            raise AssertionError("The assertion URL cannot be empty.")

        logger.info(f"👀 assertUrl -> {url}.")
        for _ in range(GlobalContext.timeout + 1):
            current_url = unquote(GlobalContext.driver.current_url)
            try:
                self.assertEqual(url, current_url)
                break
            except AssertionError:
                time.sleep(1)
        else:
            self.assertEqual(url, GlobalContext.driver.current_url, msg=msg)

    def assertInUrl(self, url: str = None, msg: str = None) -> None:
        """断言：当前URL包含指定url字符"""
        if url is None:
            raise AssertionError("The assertion URL cannot be empty.")

        logger.info(f"👀 assertInUrl -> {url}.")
        for _ in range(GlobalContext.timeout + 1):
            current_url = unquote(GlobalContext.driver.current_url)
            try:
                self.assertIn(url, current_url)

                break
            except AssertionError:
                time.sleep(1)
        else:
            self.assertIn(url, GlobalContext.driver.current_url, msg=msg)

    def assertText(self, text: str = None, msg: str = None) -> None:
        """
        Asserts whether the text of the current page conforms to expectations.

        Usage:
        self.assertText("text")
        """
        if text is None:
            raise AssertionError("The assertion text cannot be empty.")

        elem = GlobalContext.driver.find_element(By.TAG_NAME, "html")
        logger.info(f"👀 assertText -> {text}.")
        for _ in range(GlobalContext.timeout + 1):
            if elem.is_displayed():
                try:
                    self.assertIn(text, elem.text)
                    break
                except AssertionError:
                    time.sleep(1)
        else:
            self.assertIn(text, elem.text, msg=msg)

    def assertNotText(self, text: str = None, msg: str = None) -> None:
        """
        Asserts that the current page does not contain the specified text.

        Usage:
        self.assertNotText("text")
        """
        if text is None:
            raise AssertionError("The assertion text cannot be empty.")

        elem = GlobalContext.driver.find_element(By.TAG_NAME, "html")

        logger.info(f"👀 assertNotText -> {text}.")
        for _ in range(GlobalContext.timeout + 1):
            if elem.is_displayed():
                try:
                    self.assertNotIn(text, elem.text)
                    break
                except AssertionError:
                    time.sleep(1)
        else:
            self.assertNotIn(text, elem.text, msg=msg)

    def assertAlertText(self, text: str = None, msg: str = None) -> None:
        """断言：警告提示文本中包含指定字符串"""
        if text is None:
            raise NameError("Alert text cannot be empty.")

        logger.info(f"👀 assertAlertText -> {text}.")
        alert_text = GlobalContext.driver.switch_to.alert.text
        for _ in range(GlobalContext.timeout + 1):
            try:
                self.assertEqual(alert_text, text, msg=msg)
                break
            except AssertionError:
                time.sleep(1)
        else:
            self.assertEqual(alert_text, text, msg=msg)

    def assertElement(self, index: int = 0, msg: str = None, **kwargs) -> None:
        """
        Asserts whether the element exists.

        Usage:
        self.assertElement(css="#id")
        """
        logger.info("👀 assertElement.")
        if msg is None:
            msg = "No element found"

        elem = True
        for _ in range(GlobalContext.timeout + 1):
            try:
                self.get_element(index=index, **kwargs)
                elem = True
                break
            except NotFindElementError:
                elem = False
                time.sleep(1)

        self.assertTrue(elem, msg=msg)

    def assertNotElement(self, index: int = 0, msg: str = None, **kwargs) -> None:
        """
        Asserts if the element does not exist.

        Usage:
        self.assertNotElement(css="#id")
        """
        logger.info("👀 assertNotElement.")
        if msg is None:
            msg = "Find the element"

        timeout_backups = GlobalContext.timeout
        GlobalContext.timeout = 2
        try:
            self.get_element(index=index, **kwargs)
            elem = True
        except NotFindElementError:
            elem = False

        GlobalContext.timeout = timeout_backups

        self.assertFalse(elem, msg=msg)

    def assertInElement(self, index: int = 0, text: str = None, msg: str = None, **kwargs) -> None:
        """断言element存在且text包含指定字符串"""
        if text is None:
            raise AssertionError("The assertion text cannot be empty.")

        logger.info(f"👀 assertInElement -> {text}.")
        if msg is None:
            msg = "No element found"
        elem = None
        for _ in range(GlobalContext.timeout + 1):
            try:
                elem = self.get_element(index=index, **kwargs)
                break
            except NotFindElementError:
                time.sleep(1)

        self.assertIn(text, elem.text, msg=msg)


if __name__ == '__main__':
    pass
