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
    def spider(self):
        super().spider()

    @abstractmethod
    def saver(self):
        pass