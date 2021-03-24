# -*- coding:utf-8  -*-
# @Time     : 2021-03-05 22:57
# @Author   : BGLB
# @Software : PyCharm
import json
from abc import abstractmethod
import requests
from crawler._base import _CrawlerBase


class CrawlerRequest(_CrawlerBase):
    """
    接口爬虫
    """

    def __init__(self, crawlerConfig:dict):
        super().__init__(crawlerConfig)
        self.session = requests.session()
        self.cookie_dict: dict = {}

    def post(self, url, data, **kw):
        return self.session.post(url, data, **kw)

    def get(self, url, **kw):
        return self.session.get(url, **kw)

    def save_cookie(self, cookies: dict = None):
        """
        保存当前session的cookies
        :param cookies: dict 可以覆盖session.cookies
        :return:
        """
        self.cookie_dict.update(requests.utils.dict_from_cookiejar(self.session.cookies))
        super()._save_cookie(cookies)

    def load_cookie(self, cookies: dict = None):
        """
            加载历史cookie
        :param cookies: 可以覆盖历史cookies
        :return:
        """
        super()._load_cookie(cookies)

    def run(self) -> None:
        super().run()

    def __del__(self):
        if self.session:
            self.session.close()
