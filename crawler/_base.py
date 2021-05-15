# -*- coding:utf-8  -*-
# @Time     : 2021-02-27 13:46
# @Author   : BGLB
# @Software : PyCharm
import json
import os
import time
import traceback
from abc import abstractmethod
from threading import Thread

import execjs

from config import BASE_DIR
from logger import BaseLog
from scheduler.status_code import CrawlerStatus, SaverStatus


class _CrawlerBase(Thread):
    """
    爬取数据基类
    """

    def __init__(self, crawlerConfig: dict):
        super().__init__()
        self.name = '{}_{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get('CrawlerType'))
        self.timestamp = str(int(time.time()))
        self.base_dir = os.path.join(BASE_DIR, r'crawler_data\{}'.format(crawlerConfig.get('CrawlerName')))
        self.log = BaseLog('crawler', '{}_{}'.format(crawlerConfig.get('CrawlerName'), crawlerConfig.get(
            'CrawlerType')))
        self.__init_data_dir()
        self.cookie_dict = {}

        self._state = CrawlerStatus.CrawlerStart

    def __init_data_dir(self):
        """
            初始化一些数据目录, 方便之后文件上传
        :return:
        """
        # 数据保存根目录
        self.data_dir = os.path.join(self.base_dir, self.timestamp)
        self.temp_dir = os.path.join(self.data_dir, 'temp')
        self.json_dir = os.path.join(self.data_dir, 'json')
        self.img_dir = os.path.join(self.data_dir, 'img')
        self.db_dir = os.path.join(self.data_dir, 'db')
        self.log.info('数据存储路径: 【{}】'.format(self.data_dir))
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.img_dir, exist_ok=True)
        os.makedirs(self.db_dir, exist_ok=True)

    def make_dir(self, dir_name):
        """
            在self.data_dir创建目录 并返回路径
        :param dir_name:
        :return:
        """
        dir = os.path.join(self.data_dir, dir_name)
        os.makedirs(dir)
        self.log.info('创建目录： {}'.format(dir))
        return dir

    def _load_cookie(self, cookies: dict = None):
        """
            加载保存下来的历史cookie到self.cookie_dict
        :param cookies:
        :return:
        """
        try:
            with open(r'{}\cookies.txt'.format(self.base_dir), 'r') as f:
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
        with open(r'{}\cookies.txt'.format(self.base_dir), 'w', encoding='utf8') as f:
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
    def spider(self):
        self.log.warn('爬虫方法未实现')
        # time.sleep(0.5)

    @abstractmethod
    def saver(self):
        self.log.warn('数据存储方法未实现')

    def save_to_json(self, filename, data):
        """

        :param filename:
        :param data:
        :return:
        """
        pass

    def get_state(self):
        return self._state

    def run(self) -> None:
        """
            爬虫主线程
        """
        self.log.info('开始抓取数据')
        try:
            self._state = CrawlerStatus.Crawlering
            self.spider()
            self._state = CrawlerStatus.CrawlerEnd
        except Exception:
            self.log.error(traceback.format_exc(), 'error')
            self._state = CrawlerStatus.CrawlerException
            return
        try:
            self._state = SaverStatus.SaverStart
            self._state = SaverStatus.Savering
            self.log.info('开始保存数据')
            self.saver()
            self._state = SaverStatus.SaverEnd
        except Exception:
            self.log.error(traceback.format_exc(), 'error')
            self._state = SaverStatus.SaverException
            return
        self.log.info('爬虫主线程工作完毕')
