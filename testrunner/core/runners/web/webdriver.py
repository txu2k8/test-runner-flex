#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author:TXU
@file:webdriver
@time:2022/12/20
@email:tao.xu2008@outlook.com
@description: selenium webdriver API
"""
import os
import time
import platform
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webdriver import WebDriver as SeleniumWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as cService
from loguru import logger

from testrunner.core.runners.models import Settings
from testrunner.core.runners.web.exceptions import NotFindElementError
from testrunner.core.runners.web.asserts import WebAsserts
from testrunner.core.runners.web.webdriver_manager_extend import ChromeDriverManager
from testrunner.core.data_factory.random_func import get_timestamp


__all__ = ["WebDriver", "WebElement"]


# 提供8中定位方式，与Selenium保持一致。
LOCATOR_LIST = {
    'css': By.CSS_SELECTOR,
    'id_': By.ID,
    'name': By.NAME,
    'xpath': By.XPATH,
    'link_text': By.LINK_TEXT,
    'partial_link_text': By.PARTIAL_LINK_TEXT,
    'tag': By.TAG_NAME,
    'class_name': By.CLASS_NAME,
}


class WebElement(object):
    """web element API：查找元素"""

    def __init__(self, **kwargs) -> None:
        if not kwargs:
            raise ValueError("Please specify a locator")
        if len(kwargs) > 1:
            raise ValueError("Please specify only one locator")

        self.by, self.value = next(iter(kwargs.items()))
        try:
            LOCATOR_LIST[self.by]
        except KeyError:
            raise ValueError(f"Element positioning of type '{self.by}' is not supported. ")
        self.find_elem_info = None
        self.find_elem_warn = None

    def __find_element(self, elem: tuple) -> None:
        """
        Find if the element exists.
        """
        for _ in range(Settings.timeout):
            elems = Settings.driver.find_elements(by=elem[0], value=elem[1])
            if len(elems) >= 1:
                self.find_elem_info = f"Find {len(elems)} element: {elem[0]}={elem[1]} "
                break
            time.sleep(1)
        else:
            self.find_elem_warn = f"❌ Find 0 element through: {elem[0]}={elem[1]}"

    def get_elements(self, index: int = None):
        """
        Judge element positioning way, and returns the element.
        """

        if self.by == "id_":
            self.__find_element((By.ID, self.value))
            elem = Settings.driver.find_elements(By.ID, self.value)
        elif self.by == "name":
            self.__find_element((By.NAME, self.value))
            elem = Settings.driver.find_elements(By.NAME, self.value)
        elif self.by == "class_name":
            self.__find_element((By.CLASS_NAME, self.value))
            elem = Settings.driver.find_elements(By.CLASS_NAME, self.value)
        elif self.by == "tag":
            self.__find_element((By.TAG_NAME, self.value))
            elem = Settings.driver.find_elements(By.TAG_NAME, self.value)
        elif self.by == "link_text":
            self.__find_element((By.LINK_TEXT, self.value))
            elem = Settings.driver.find_elements(By.LINK_TEXT, self.value)
        elif self.by == "partial_link_text":
            self.__find_element((By.PARTIAL_LINK_TEXT, self.value))
            elem = Settings.driver.find_elements(By.PARTIAL_LINK_TEXT, self.value)
        elif self.by == "xpath":
            self.__find_element((By.XPATH, self.value))
            elem = Settings.driver.find_elements(By.XPATH, self.value)
        elif self.by == "css":
            self.__find_element((By.CSS_SELECTOR, self.value))
            elem = Settings.driver.find_elements(By.CSS_SELECTOR, self.value)
        else:
            raise NameError(
                "Please enter the correct targeting elements,'id_/name/class_name/tag/link_text/xpath/css'.")

        if index is None:
            return elem

        if len(elem) == 0:
            raise NotFindElementError(self.find_elem_warn)

        return elem[index]

    @staticmethod
    def show_element(elem) -> None:
        """
        Show the elements of the operation
        :param elem:
        """
        if (Settings.app_server is not None) and (Settings.app_info is not None):
            return None
        style_red = 'arguments[0].style.border="2px solid #FF0000"'
        style_blue = 'arguments[0].style.border="2px solid #00FF00"'
        style_null = 'arguments[0].style.border=""'
        if Settings.debug is True:
            for _ in range(2):
                Settings.driver.execute_script(style_red, elem)
                time.sleep(0.2)
                Settings.driver.execute_script(style_blue, elem)
                time.sleep(0.2)
            Settings.driver.execute_script(style_blue, elem)
            time.sleep(0.2)
            Settings.driver.execute_script(style_null, elem)
        else:
            for _ in range(2):
                Settings.driver.execute_script(style_red, elem)
                time.sleep(0.1)
                Settings.driver.execute_script(style_blue, elem)
                time.sleep(0.1)
            Settings.driver.execute_script(style_blue, elem)
            time.sleep(0.3)
            Settings.driver.execute_script(style_null, elem)

    @property
    def info(self):
        """return element info"""
        return self.find_elem_info

    @property
    def warn(self):
        """return element warn"""
        return self.find_elem_warn


class WebDriver(WebAsserts):
    """selenium封装，使用例写作更简单"""

    def __init__(self):
        self.images = []

    # 键盘操作
    class Keys:
        """
        Achieve keyboard shortcuts：实现键盘操作

        Usage:
            self.Keys(id_="kw").enter()
        """

        def __init__(self, index: int = 0, **kwargs) -> None:
            self.web_elem = WebElement(**kwargs)
            self.elem = self.web_elem.get_elements(index)
            self.web_elem.show_element(self.elem)

        def input(self, text="") -> None:
            logger.info(f"✅ {self.web_elem.info}, input '{text}'.")
            self.elem.send_keys(text)

        def enter(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, enter.")
            self.elem.send_keys(Keys.ENTER)

        def select_all(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, ctrl+a.")
            if platform.system().lower() == "darwin":
                self.elem.send_keys(Keys.COMMAND, "a")
            else:
                self.elem.send_keys(Keys.CONTROL, "a")

        def cut(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, ctrl+x.")
            if platform.system().lower() == "darwin":
                self.elem.send_keys(Keys.COMMAND, "x")
            else:
                self.elem.send_keys(Keys.CONTROL, "x")

        def copy(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, ctrl+c.")
            if platform.system().lower() == "darwin":
                self.elem.send_keys(Keys.COMMAND, "c")
            else:
                self.elem.send_keys(Keys.CONTROL, "c")

        def paste(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, ctrl+v.")
            if platform.system().lower() == "darwin":
                self.elem.send_keys(Keys.COMMAND, "v")
            else:
                self.elem.send_keys(Keys.CONTROL, "v")

        def backspace(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, backspace.")
            self.elem.send_keys(Keys.BACKSPACE)

        def delete(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, delete.")
            self.elem.send_keys(Keys.DELETE)

        def tab(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, tab.")
            self.elem.send_keys(Keys.TAB)

        def space(self) -> None:
            logger.info(f"✅ {self.web_elem.info}, space.")
            self.elem.send_keys(Keys.SPACE)

    @staticmethod
    def visit(url: str) -> None:
        """
        visit url.

        Usage:
            self.visit("https://www.baidu.com")
        """
        logger.info(f"📖 {url}")
        if isinstance(Settings.driver, SeleniumWebDriver) is False:
            Settings.driver = Chrome(service=cService(ChromeDriverManager().install()))
        Settings.driver.get(url)

    def open(self, url: str) -> None:
        """
        open url.

        Usage:
            self.open("https://www.baidu.com")
        """
        self.visit(url)

    @staticmethod
    def max_window() -> None:
        """
        Set browser window maximized.

        Usage:
            self.max_window()
        """
        Settings.driver.maximize_window()

    @staticmethod
    def set_window(wide: int = 0, high: int = 0) -> None:
        """
        Set browser window wide and high.

        Usage:
            self.set_window(wide,high)
        """
        Settings.driver.set_window_size(wide, high)

    @staticmethod
    def get_windows() -> dict:
        """
         Gets the width and height of the current window.

        :Usage:
            driver.get_windows()
        """
        return Settings.driver.get_window_size()

    def type(self, text: str, clear: bool = False, enter: bool = False, index: int = 0, **kwargs) -> None:
        """
        Operation input box.

        Usage:
            self.type(css="#el", text="selenium")
        """
        if clear is True:
            self.clear(index, **kwargs)
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        if enter is True:
            logger.info(f"✅ {web_elem.info} -> input '{text}' and enter.")
        else:
            logger.info(f"✅ {web_elem.info} -> input '{text}'.")
        elem.send_keys(text)
        if enter is True:
            elem.send_keys(Keys.ENTER)

    def type_enter(self, text: str, clear: bool = False, index: int = 0, **kwargs) -> None:
        """
        Enter text and enter directly.

        Usage:
            self.type_enter(css="#el", text="selenium")
        """
        self.type(text, clear, enter=True, index=index, ** kwargs)

    @staticmethod
    def clear(index: int = 0, **kwargs) -> None:
        """
        Clear the contents of the input box.

        Usage:
            self.clear(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> clear input.")
        elem.clear()

    @staticmethod
    def click(index: int = 0, **kwargs) -> None:
        """
        It can click any text / image can be clicked
        Connection, check box, radio buttons, and even drop-down box etc..

        Usage:
            self.click(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> click.")
        elem.click()

    @staticmethod
    def slow_click(index: int = 0, **kwargs) -> None:
        """
        Moving the mouse to the middle of an element. and click element.

        Usage:
            self.slow_click(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> slow click.")
        ActionChains(Settings.driver).move_to_element(elem).click(elem).perform()

    @staticmethod
    def right_click(index: int = 0, **kwargs) -> None:
        """
        Right click element.

        Usage:
            self.right_click(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> right click.")
        ActionChains(Settings.driver).context_click(elem).perform()

    @staticmethod
    def move_to_element(index: int = 0, **kwargs) -> None:
        """
        Mouse over the element.

        Usage:
            self.move_to_element(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> move to element.")
        ActionChains(Settings.driver).move_to_element(elem).perform()

    @staticmethod
    def click_and_hold(index: int = 0, **kwargs) -> None:
        """
        Mouse over the element.

        Usage:
            self.move_to_element(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> click and hold.")
        ActionChains(Settings.driver).click_and_hold(elem).perform()

    @staticmethod
    def drag_and_drop_by_offset(index: int = 0, x: int = 0, y: int = 0, **kwargs) -> None:
        """
        Holds down the left mouse button on the source element,
           then moves to the target offset and releases the mouse button.

        :Args:
         - source: The element to mouse down.
         - x: X offset to move to.
         - y: Y offset to move to.
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        action = ActionChains(Settings.driver)
        logger.info(f"✅ {web_elem.info} -> drag and drop by offset.")
        action.drag_and_drop_by_offset(elem, x, y).perform()

    @staticmethod
    def double_click(index: int = 0, **kwargs) -> None:
        """
        Double click element.

        Usage:
            self.double_click(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> double click.")
        ActionChains(Settings.driver).double_click(elem).perform()

    @staticmethod
    def click_text(text: str, index: int = 0) -> None:
        """
        Click the element by the link text

        Usage:
            self.click_text("新闻")
        """
        web_elem = WebElement(link_text=text)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> click link.")
        elem.click()

    @staticmethod
    def close() -> None:
        """
        Closes the current window.

        Usage:
            self.close()
        """
        if isinstance(Settings.driver, SeleniumWebDriver) is True:
            Settings.driver.close()
            Settings.driver = None

    @staticmethod
    def quit() -> None:
        """
        Quit the driver and close all the windows.

        Usage:
            self.quit()
        """
        Settings.driver.quit()

    @staticmethod
    def submit(index: int = 0, **kwargs) -> None:
        """
        Submit the specified form.

        Usage:
            driver.submit(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> submit.")
        elem.submit()

    @staticmethod
    def refresh() -> None:
        """
        Refresh the current page.

        Usage:
            self.refresh()
        """
        logger.info("🔄️ refresh page.")
        Settings.driver.refresh()

    @staticmethod
    def execute_script(script: str, *args):
        """
        Execute JavaScript scripts.

        Usage:
            self.execute_script("window.scrollTo(200,1000);")
        """
        return Settings.driver.execute_script(script, *args)

    def window_scroll(self, width: int = 0, height: int = 0) -> None:
        """
        Setting width and height of window scroll bar.

        Usage:
            self.window_scroll(width=300, height=500)
        """
        js = f"window.scrollTo({width},{height});"
        self.execute_script(js)

    def element_scroll(self, css: str, width: int = 0, height: int = 0) -> None:
        """
        Setting width and height of element scroll bar.

        Usage:
            self.element_scroll(css=".class", width=300, height=500)
        """
        scroll_life = f'document.querySelector("{css}").scrollLeft = {width};'
        scroll_top = f'document.querySelector("{css}").scrollTop = {height};'
        self.execute_script(scroll_life)
        self.execute_script(scroll_top)

    @staticmethod
    def get_attribute(attribute=None, index: int = 0, **kwargs) -> str:
        """
        Gets the value of an element attribute.

        Usage:
            self.get_attribute(css="#el", attribute="type")
        """
        if attribute is None:
            raise ValueError("attribute is not None")
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> get attribute：{attribute}.")
        return elem.get_attribute(attribute)

    @staticmethod
    def get_text(index: int = 0, **kwargs) -> str:
        """
        Get element text information.

        Usage:
            self.get_text(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> get text: {elem.text}.")
        return elem.text

    @staticmethod
    def get_display(index: int = 0, **kwargs) -> bool:
        """
        Gets the element to display,The return result is true or false.

        Usage:
            self.get_display(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        result = elem.is_displayed()
        logger.info(f"✅ {web_elem.info} -> element is display: {result}.")
        return result

    @property
    def get_title(self) -> str:
        """
        Get window title.

        Usage:
            self.get_title()
        """
        logger.info(f"✅ get title: {Settings.driver.title}.")
        return Settings.driver.title

    @property
    def get_url(self) -> str:
        """
        Get the URL address of the current page.

        Usage:
            self.get_url()
        """
        logger.info(f"✅ get current url: {Settings.driver.current_url}.")
        return Settings.driver.current_url

    @property
    def get_alert_text(self) -> str:
        """
        Gets the text of the Alert.

        Usage:
            self.get_alert_text()
        """
        logger.info(f"✅ alert text: {Settings.driver.switch_to.alert.text}.")
        return Settings.driver.switch_to.alert.text

    @staticmethod
    def wait(secs: int = 10) -> None:
        """
        Implicitly wait.All elements on the page.

        Usage:
            self.wait(10)
        """
        logger.info(f"⌛️ implicitly wait: {secs}s.")
        Settings.driver.implicitly_wait(secs)

    @staticmethod
    def accept_alert() -> None:
        """
        Accept warning box.

        Usage:
            self.accept_alert()
        """
        logger.info("✅ accept alert.")
        Settings.driver.switch_to.alert.accept()

    @staticmethod
    def dismiss_alert() -> None:
        """
        Dismisses the alert available.

        Usage:
            self.dismiss_alert()
        """
        logger.info("✅ dismiss alert.")
        Settings.driver.switch_to.alert.dismiss()

    @staticmethod
    def switch_to_frame(index: int = 0, **kwargs) -> None:
        """
        Switch to the specified frame.

        Usage:
            self.switch_to_frame(css="#el")
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> switch to frame.")
        Settings.driver.switch_to.frame(elem)

    @staticmethod
    def switch_to_frame_parent() -> None:
        """
        Switches focus to the parent context. If the current context is the top
        level browsing context, the context remains unchanged.

        Usage:
            self.switch_to_frame_parent()
        """
        logger.info("✅ switch to parent frame.")
        Settings.driver.switch_to.parent_frame()

    @staticmethod
    def switch_to_frame_out() -> None:
        """
        Returns the current form machine form at the next higher level.
        Corresponding relationship with switch_to_frame () method.

        Usage:
            self.switch_to_frame_out()
        """
        logger.info("✅ switch to frame out.")
        Settings.driver.switch_to.default_content()

    @staticmethod
    def switch_to_window(window: int) -> None:
        """
        Switches focus to the specified window.

        :Args:
         - window: window index. 1 represents a newly opened window (0 is the first one)

        :Usage:
            self.switch_to_window(1)
        """
        logger.info(f"✅ switch to the {window} window.")
        all_handles = Settings.driver.window_handles
        Settings.driver.switch_to.window(all_handles[window])

    @staticmethod
    def switch_to_new_window(type_hint=None) -> None:
        """
        Switches to a new top-level browsing context.

        The type hint can be one of "tab" or "window". If not specified the
        browser will automatically select it.

        :Usage:
            self.switch_to_new_window('tab')
        """
        logger.info("✅ switch to new window.")
        Settings.driver.switch_to.new_window(type_hint=type_hint)

    def screenshots(self, file_path: str = None) -> None:
        """
        Saves a screenshots of the current window to a PNG image file.

        Usage:
            self.screenshots()
            self.screenshots('/Screenshots/foo.png')
        """
        if file_path is None:
            img_dir = os.path.join(os.getcwd(), "reports", "images")
            if os.path.exists(img_dir) is False:
                os.mkdir(img_dir)
            file_path = os.path.join(img_dir, get_timestamp() + ".png")
        if Settings.debug is True:
            logger.info(f"📷️  screenshot -> ({file_path}).")
            Settings.driver.save_screenshot(file_path)
        else:
            logger.info("📷️  screenshot -> HTML report.")
            self.images.append(Settings.driver.get_screenshot_as_base64())

    def element_screenshot(self, file_path: str = None, index: int = 0, **kwargs) -> None:
        """
        Saves a element screenshot of the element to a PNG image file.

        Usage:
            self.element_screenshot(css="#id")
            self.element_screenshot(css="#id", file_path='/Screenshots/foo.png')
        """

        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        if file_path is None:
            img_dir = os.path.join(os.getcwd(), "reports", "images")
            if os.path.exists(img_dir) is False:
                os.mkdir(img_dir)
            file_path = os.path.join(img_dir, get_timestamp() + ".png")
        if Settings.debug is True:
            logger.info(f"📷️ element screenshot -> ({file_path}).")
            elem.screenshot(file_path)
        else:
            logger.info("📷️ element screenshot -> HTML Report.")
            self.images.append(elem.screenshot_as_base64)

    @staticmethod
    def select(value: str = None, text: str = None, index: int = None, **kwargs) -> None:
        """
        Constructor. A check is made that the given element is, indeed, a SELECT tag. If it is not,
        then an UnexpectedTagNameException is thrown.

        :Args:
         - css - element SELECT element to wrap
         - value - The value to match against

        Usage:
            <select name="NR" id="nr">
                <option value="10" selected="">每页显示10条</option>
                <option value="20">每页显示20条</option>
                <option value="50">每页显示50条</option>
            </select>

            self.select(css="#nr", value='20')
            self.select(css="#nr", text='每页显示20条')
            self.select(css="#nr", index=2)
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(0)
        web_elem.show_element(elem)
        logger.info(f"✅ {web_elem.info} -> select option.")
        if value is not None:
            Select(elem).select_by_value(value)
        elif text is not None:
            Select(elem).select_by_visible_text(text)
        elif index is not None:
            Select(elem).select_by_index(index)
        else:
            raise ValueError(
                '"value" or "text" or "index" options can not be all empty.')

    @staticmethod
    def get_cookies() -> list:
        """
        Returns a set of dictionaries, corresponding to cookies visible in the current session.
        Usage:
            self.get_cookies()
        """
        return Settings.driver.get_cookies()

    @staticmethod
    def get_cookie(name: str) -> dict:
        """
        Returns information of cookie with ``name`` as an object.
        Usage:
            self.get_cookie("name")
        """
        return Settings.driver.get_cookie(name)

    @staticmethod
    def add_cookie(cookie_dict: dict) -> None:
        """
        Adds a cookie to your current session.
        Usage:
            self.add_cookie({'name' : 'foo', 'value' : 'bar'})
        """
        if isinstance(cookie_dict, dict):
            Settings.driver.add_cookie(cookie_dict)
        else:
            raise TypeError("Wrong cookie type.")

    @staticmethod
    def add_cookies(cookie_list: list) -> None:
        """
        Adds a cookie to your current session.
        Usage:
            cookie_list = [
                {'name' : 'foo', 'value' : 'bar'},
                {'name' : 'foo', 'value' : 'bar'}
            ]
            self.add_cookies(cookie_list)
        """
        if isinstance(cookie_list, list):
            for cookie in cookie_list:
                if isinstance(cookie, dict):
                    Settings.driver.add_cookie(cookie)
                else:
                    raise TypeError("Wrong cookie type.")
        else:
            raise TypeError("Wrong cookie type.")

    @staticmethod
    def delete_cookie(name: str) -> None:
        """
        Deletes a single cookie with the given name.
        Usage:
            self.delete_cookie('my_cookie')
        """
        Settings.driver.delete_cookie(name)

    @staticmethod
    def delete_all_cookies() -> None:
        """
        Delete all cookies in the scope of the session.
        Usage:
            self.delete_all_cookies()
        """
        Settings.driver.delete_all_cookies()

    @staticmethod
    def sleep(sec: int) -> None:
        """
        Usage:
            self.sleep(seconds)
        """
        logger.info(f"💤️ sleep: {sec}s.")
        time.sleep(sec)

    @staticmethod
    def check_element(css: str = None) -> None:
        """
        Check that the element exists

        Usage:
        self.check_element(css="#el")
        """
        if css is None:
            raise NameError("Please enter a CSS selector")

        logger.info("👀 check element.")
        js = f'return document.querySelectorAll("{css}")'
        ret = Settings.driver.execute_script(js)
        if len(ret) > 0:
            for i in range(len(ret)):
                js = f'return document.querySelectorAll("{css}")[{i}].outerHTML;'
                ret = Settings.driver.execute_script(js)
                logger.info(f"{i} -> {ret}")
        else:
            logger.warning("No elements were found.")

    @staticmethod
    def get_elements(**kwargs):
        """
        Get a set of elements

        Usage:
        ret = self.get_elements(css="#el")
        print(len(ret))
        """
        web_elem = WebElement(**kwargs)
        elems = web_elem.get_elements()
        if len(elems) == 0:
            logger.warning(f"{web_elem.warn}.")
        else:
            logger.info(f"✅ {web_elem.info}.")
        return elems

    @staticmethod
    def get_element(index: int = 0, **kwargs):
        """
        Get a set of elements

        Usage:
        elem = self.get_element(index=1, css="#el")
        elem.click()
        """
        web_elem = WebElement(**kwargs)
        elem = web_elem.get_elements(index)
        logger.info(f"✅ {web_elem.info}.")
        return elem

    @staticmethod
    def switch_to_app() -> None:
        """
        appium API
        Switch to native app.
        """
        logger.info("🔀 switch to native app.")
        current_context = Settings.driver.current_context
        if current_context != "NATIVE_APP":
            Settings.driver.switch_to.context('NATIVE_APP')

    @staticmethod
    def switch_to_web(context=None) -> None:
        """
        appium API
        Switch to web view.
        """
        logger.info("🔀 switch to webview.")
        current_context = Settings.driver.current_context
        if context is not None:
            Settings.driver.switch_to.context(context)
        elif "WEBVIEW" in current_context:
            return
        else:
            all_context = Settings.driver.contexts
            for context in all_context:
                if "WEBVIEW" in context:
                    Settings.driver.switch_to.context(context)
                    break
            else:
                raise NameError("No WebView found.")

    @staticmethod
    def switch_to_flutter() -> None:
        """
        appium API
        Switch to flutter app.
        """
        logger.info("🔀 switch to flutter.")
        current_context = Settings.driver.current_context
        if current_context != "NATIVE_APP":
            Settings.driver.switch_to.context('FLUTTER')


if __name__ == '__main__':
    pass
