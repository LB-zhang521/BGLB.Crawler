# -*- coding:utf-8  -*-
# @Time     : 2021-03-05 22:55
# @Author   : BGLB
# @Software : PyCharm
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

    def driver_init(self, proxy: dict = '') -> webdriver.Chrome():
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
        self.log.warn('爬虫主方法未实现')

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
        print(StaticPath.chromedriver)
        if not self.driver:
            self.driver = self.driver_init()
        self.main()
        if self.driver:
            self.driver.quit()
