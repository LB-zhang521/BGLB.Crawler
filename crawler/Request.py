# -*- coding:utf-8  -*-
# @Time     : 2021-03-05 22:57
# @Author   : BGLB
# @Software : PyCharm
from abc import abstractmethod
import requests
from crawler._base import _CrawlerBase


class CrawlerRequest(_CrawlerBase):
    """
    接口爬虫
    """
    def __init__(self, crawlerConfig:dict):
        super().__init__(crawlerConfig)
        self.sesscion = None
        self.cookie_dict = None

    def post(self, url, **kw):
        return self.sesscion.post(url, **kw)

    def get(self, url, **kw):
        return self.sesscion.get(url, **kw)

    def save_cookie(self):
        pass

    @abstractmethod
    def main(self):
        self.log.warn('爬虫主方法未实现')

    def run(self) -> None:
        self.sesscion = requests.session()
        self.main()
        if self.sesscion:
            self.sesscion.close()