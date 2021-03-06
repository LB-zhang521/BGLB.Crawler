# -*- coding:utf-8  -*-
# @Time     : 2021-02-28 19:30
# @Author   : BGLB
# @Software : PyCharm
import importlib
import threading

from logger import BaseLog
from main_debug import TaskConfig


def start_one_task(taskConfig: dict):
    """
    :param taskConfig:
    :return:
    """
    crawler_config = taskConfig.get('CrawlerConfig', {})
    crawler_name = crawler_config.get('CrawlerName', '')
    crawler_type = crawler_config.get('CrawlerType', '').lower()
    crawler_module = importlib.import_module('{}.spyider'.format(crawler_name.lower()))
    # crawler_cls = eval('crawler_module.Crawler{}'.format(crawler_name.title()))
    crawler_cls = getattr(crawler_module, 'Crawler{}'.format(crawler_name.title()))
    ControleLog = BaseLog('scheduler_control')
    ControleLog.info('{}, {}开始启动'.format(taskConfig.get('TaskName'), crawler_type))
    t = crawler_cls(TaskConfig.get('CrawlerConfig'))
    t.start()
    # t.join()

    ControleLog.info('Crawler 线程结束!', saylever='last')
    ControleLog.info('启动saver 线程')
    ControleLog.info('启动saver 线程,')

    ControleLog.info('启动saver 守护线程线程')
    ControleLog.info('启动saver 守护线程线程')
    ControleLog.info('启动saver 守护线程线程 关闭！')
    ControleLog.info('启动saver 守护线程线程 结束')


def start_tasks():
    pass


def start_crawler(crawler_cls: str):

    pass


def start_saver():
    pass


def add_one_task():
    pass


def kill_one_task():
    pass


def get_task_status(task_id):
    pass


def get_task_working():
    pass


if __name__ == '__main__':
    start_one_task(TaskConfig)
