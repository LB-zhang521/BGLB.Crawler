# -*- coding:utf-8  -*-
# @Time     : 2021-03-05 22:55
# @Author   : BGLB
# @Software : PyCharm
import traceback
from abc import abstractmethod
from selenium import webdriver
from crawler._base import _CrawlerBase
from utils.common.constant import StaticPath


class CrawlerBrower(_CrawlerBase):
    """
    pc浏览器爬虫
    """

    def __init__(self, crawlerConfig:dict):
        super().__init__(crawlerConfig)
        self.name = 'CrawlerBrower'
        self.driver = None
        self.__driver_init = False

    def driver_init(self, proxy: dict = None) -> webdriver:
        """
        初始化chrome driver
        :type  proxy: dict
        :param proxy: 代理配置 dict{'ip': '_ip', 'port': '_port'}
        :return: webdriver.Chrome()

        """
        if self.driver:
            return self.driver
        else:
            options = webdriver.ChromeOptions()
            pres = {'credentials_enable_service': False, 'profile.password_manager_enabled': False}

            # 添加代理
            if proxy:
                options.add_argument("--proxy-server=http://{}:{}".format(proxy['ip'], proxy['port']))
            if not StaticPath.chromedriver.endswith('exe'):
                options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败

            options.add_argument("--disable-blink-features=AutomationControlled")  # 88版本过检测
            options.add_argument('lang=zh_CN.UTF-8')  # 设置语言
            options.add_argument('--disable-infobars')  # 除去“正受到自动测试软件的控制”
            # options.add_argument("--auto-open-devtools-for-tabs") # 相当于 F12

            options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])  # 过检测
            options.add_experimental_option('useAutomationExtension', False)
            options.add_experimental_option('prefs', pres)  # 禁用保存密码弹框

            # options.add_extension('')  # 添加插件

            driver = webdriver.Chrome(executable_path=StaticPath.chromedriver, options=options)

            # 屏蔽浏览器中的window.navigator.webdriver = true
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                                        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"})

            driver.maximize_window()
            self.__driver_init = True
        return driver

    @abstractmethod
    def spider(self):
        """
        抽象方法，所有爬虫类必须实现
        :return:
        """
        super().spider()

    def load_cookie(self, cookies: dict = None):
        """
        加载历史cookie 给self.cookies_dict 赋值
        :return:
        """
        super()._load_cookie(cookies)

    def save_cookie(self, cookies: dict = None):
        """
            保存cookie
        :param cookies:
        :return:
        """
        self.cookie_dict.update(self.driver.get_cookie())
        self._save_cookie(cookies)

    def run(self) -> None:
        super().run()

    def __del__(self):
        if self.driver:
            self.driver.quit()
