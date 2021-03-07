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
    print(t.get_state())
    # t.join()
    print(t.get_state())
    ControleLog.info('Crawler 线程正常结束!', say=True, saylever='last')
    ControleLog.info('启动saver 线程')
    ControleLog.info('启动saver 线程,')
    print(t.get_state())
    ControleLog.info('启动saver 守护线程线程')
    ControleLog.info('启动saver 守护线程线程')
    ControleLog.info('启动saver 守护线程线程 关闭！')
    ControleLog.info('启动saver 守护线程线程 结束')
    print(t.get_state())
    print(threading.active_count())
    while True:
        if t.get_state() == CrawlerStatus.CrawlerException:
            _async_raise(t.ident, SystemExit)
            time.sleep(.5)
            break
    print(t.is_alive())
    print(threading.active_count())
    print(threading.active_count())


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


def _async_raise(tid, exctype):
    """https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread"""
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def get_task_working():
    pass


if __name__ == '__main__':
    start_one_task(TaskConfig)
