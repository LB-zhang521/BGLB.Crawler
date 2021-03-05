# -*- coding:utf-8  -*-
# @Time     : 2021-03-05 22:54
# @Author   : BGLB
# @Software : PyCharm
from abc import abstractmethod

from crawler._base import _CrawlerBase


class CrawlerAndroid(_CrawlerBase):
    """
    安卓爬虫
    """
    def __init__(self, crawlerConfig:dict):
        super().__init__(crawlerConfig)
        self.adb_commond = None
        pass

    @abstractmethod
    def main(self):
        self.log.warn('爬虫主方法未实现')

    @abstractmethod
    def saver(self):
        pass