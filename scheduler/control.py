# -*- coding:utf-8  -*-
# @Time     : 2021-02-28 19:30
# @Author   : BGLB
# @Software : PyCharm
import ctypes
import importlib
import inspect
import threading
import time

from logger import BaseLog
from main_debug import TaskConfig
from scheduler.status_code import CrawlerStatus
import queue
_TaskQueue = queue.Queue()


class Task(object):

    def __init__(self):
        self.TaskQueue = None
        self.log = BaseLog('scheduler_control')

    def start_one_task(self, taskConfig: dict):
        """
        :param taskConfig:
        :return:
        """
        crawler_config = taskConfig.get('CrawlerConfig', {})
        task_name = taskConfig.get('TaskName')
        task_id = taskConfig.get('TaskId')
        self.log.info('{}, {}开始启动'.format(task_id, task_name))
        self.start_crawle(crawler_config)

    def start_tasks(self):

        pass

    def start_crawle(self, crawler_config: dict):
        """
            启动爬虫主线程
        :param crawler_config:
        :return:
        """
        crawler_name = crawler_config.get('CrawlerName', '')
        crawler_type = crawler_config.get('CrawlerType', '').lower()
        crawler_module = importlib.import_module('{}.{}_{}'.format(crawler_name.lower(), crawler_name, crawler_type))
        # crawler_cls = eval('crawler_module.Crawler{}'.format(crawler_name.title()))
        CrawlerClass = getattr(crawler_module, 'Crawler{}'.format(crawler_name.title()))
        CrawlerInstance = CrawlerClass(crawler_config)
        CrawlerInstance.start()

    def add_one_task(self, ):
        pass

    def kill_one_task(self, ):
        pass

    def get_task_status(self, task_id):
        pass

    def _async_raise(self, tid, exctype):
        """https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread"""
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        if res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def get_task_working(self, ):
        pass


if __name__ == '__main__':
    Task().start_one_task(TaskConfig)
