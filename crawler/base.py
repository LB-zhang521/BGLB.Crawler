# -*- coding:utf-8  -*-
# @Time     : 2021-02-27 13:46
# @Author   : BGLB
# @Software : PyCharm
import requests
import threading
from logger import BaseLog


class _CrawlerBase(threading.Thread):
    """
    爬取数据基类
    """
    def __init__(self):
        super().__init__()
        self.name = 'Crawler'
        pass

    def start(self) -> None:

        pass

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

    def main(self):
        pass

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
        super(CrawlerBrower, self).__init__()
        self.driver = None
        self.log = BaseLog('crawlerBrower', '{}-{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get(
            'CrawlerType')))

    def __driver_init(self):
        pass

    def main(self):
        self.__driver_init()
        pass

