# -*- coding:utf-8  -*-
# @Time     : 2021-02-27 13:46
# @Author   : BGLB
# @Software : PyCharm
import os


import threading


from abc import abstractmethod

from config import BASE_DIR
from logger import BaseLog


class _CrawlerBase(threading.Thread):
    """
    爬取数据基类
    """
    def __init__(self, crawlerConfig:dict):
        super().__init__()
        root_sub_dir = crawlerConfig.get('CrawlerName')
        self.name = '{}{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get('CrawlerType'))
        self.crawlerDataDir = os.path.join(BASE_DIR, r'{}\crawler_data'.format(root_sub_dir))  # 数据保存根目录
        self.log = BaseLog('crawler', '{}_{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get(
            'CrawlerType')))

    @abstractmethod
    def main(self):
        pass

    def saver(self):

        pass

