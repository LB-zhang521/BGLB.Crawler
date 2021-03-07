# -*- coding:utf-8  -*-
# @Time     : 2021-02-27 13:46
# @Author   : BGLB
# @Software : PyCharm
import json
import os
import threading
import execjs
from abc import abstractmethod
from config import BASE_DIR
from logger import BaseLog
from scheduler.status_code import CrawlerStatus


class _CrawlerBase(threading.Thread):
    """
    爬取数据基类
    """

    def __init__(self, crawlerConfig: dict):
        super().__init__()
        self.name = '{}{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get('CrawlerType'))

        # 数据保存根目录
        self.crawlerDataDir = os.path.join(BASE_DIR, r'{}\crawler_data'.format(crawlerConfig.get('CrawlerName')))
        self.log = BaseLog('crawler', '{}_{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get(
            'CrawlerType')))
        self.cookie_dict = {}
        self.state = CrawlerStatus.CrawlerStart

    def _load_cookie(self, cookies: dict = None):
        """
            加载保存下来的历史cookie到self.cookie_dict
        :param cookies:
        :return:
        """
        try:
            with open(self.crawlerDataDir.join('cookies.txt'), 'r') as f:
                self.cookie_dict = json.loads(f, encoding='utf8')
        except IOError:
            self.log.warn('不存在历史cookie')

        if cookies:
            for _k, v in cookies.items():
                self.cookie_dict.update(_k=v)
            self.log.info('历史cookie加载成功')

    def _save_cookie(self, cookies: dict = None):
        """
            保存当前cookie_dict
        :return:
        """
        save_cookie = self.cookie_dict
        save_cookie.update(cookies)
        with open(self.crawlerDataDir.join('cookies.txt'), 'w', encoding='utf8') as f:
            json.dump(save_cookie, f)
        self.log.info('保存cookies成功')

    @staticmethod
    def exec_javascript(scripts: str, func_name: str, runtime_dir: str = None, *args):
        """

        :param scripts: js脚本字符串
        :param func_name: 需要调用的js 函数名
        :param runtime_dir: 运行js的目录
        :param args: 执行js函数需要的参数
        :return:
        """
        ct = execjs.compile(scripts, cwd=runtime_dir)
        return ct.call(func_name, *args)

    @abstractmethod
    def main(self):
        pass

    def saver(self):
        pass

    def get_state(self):

        return self.state

    def run(self) -> None:
        self.state = CrawlerStatus.Crawlering
        self.main()
        self.state = CrawlerStatus.CrawlerEnd

