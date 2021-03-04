# -*- coding:utf-8  -*-
# @Time     : 2021-02-27 13:46
# @Author   : BGLB
# @Software : PyCharm
import requests
import threading

from selenium import webdriver
from abc import abstractmethod
from logger import BaseLog
from utils.common.constant import StaticPath


class _CrawlerBase(threading.Thread):
    """
    爬取数据基类
    """
    def __init__(self):
        super().__init__()
        pass

    def run(self) -> None:

        pass

    @abstractmethod
    def main(self):

        pass

    def saver(self):

        pass


class CrawlerAndroid(_CrawlerBase):
    """
    安卓爬虫
    """
    def __init__(self, crawlerConfig):
        super(CrawlerAndroid, self).__init__()
        self.adb_commond = None
        self.log = BaseLog('crawlerAndroid', '{}-{}'.format(crawlerConfig.get('CrawlerName'),crawlerConfig.get(
            'CrawlerType')))
        pass

    @abstractmethod
    def main(self):
        pass

    @abstractmethod
    def saver(self):
        pass


class CrawlerRequest(_CrawlerBase):
    """
    接口爬虫
    """
    def __init__(self, crawlerConfig):
        super(CrawlerRequest, self).__init__()
        self.sesscion = requests.session()
        self.cookie_dict = None
        self.log = BaseLog('crawlerRequest', '{}-{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get(
            'CrawlerType')))

    def post(self, url, **kw):
        return self.sesscion.post(url, **kw)

    def get(self, url, **kw):
        return self.sesscion.get(url, **kw)

    def save_cookie(self):
        pass

    def main(self):
        self.sesscion = requests.session()
        pass


class CrawlerBrower(_CrawlerBase):
    """
    pc浏览器爬虫
    """

    def __init__(self, crawlerConfig):
        super().__init__()
        self.name = 'CrawlerBrowler'
        self.driver = None
        self.log = BaseLog('crawlerBrower', '{}-{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get(
            'CrawlerType')))

    @staticmethod
    def driver_init(proxy: dict = '') -> webdriver.Chrome():
        """
        初始化chrome driver
        :type  proxy: dict
        :param proxy: 代理配置 dict{'ip': '_ip', 'port': '_port'}
        :return: webdriver.Chrome()

        """
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-infobars')  # 除去“正受到自动测试软件的控制”
        # 添加代理
        if not proxy and 'ip' in proxy.keys() and 'port' in proxy.keys() \
                and proxy.get('ip', '') and proxy.get('port', ''):
            options.add_argument("--proxy-server=http://{}:{}".format(proxy['ip'], proxy['_port']))

        # 设置为开发者模式
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        driver = webdriver.Chrome(executable_path=StaticPath.chromedriver, options=options)
        script = '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                '''
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})
        return driver

    @abstractmethod
    def main(self):
        """
        抽象方法，所有爬虫类必须实现
        :return:
        """
        self.driver = self.driver_init()

    def load_cookie(self):
        """
        加载历史cookie
        :return:
        """

    def save_cookie(self):
        """
        保存cookie
        :return:
        """
        if self.driver:
            self.driver.get_cookie()

    def run(self) -> None:
        self.main()
        if self.driver:
            self.driver.quit()

