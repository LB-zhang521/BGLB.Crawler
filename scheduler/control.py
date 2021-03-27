# -*- coding:utf-8  -*-
# @Time     : 2021-02-28 19:30
# @Author   : BGLB
# @Software : PyCharm
import ctypes
import importlib
import inspect
import os
import socket
import threading
import time
import traceback

import psutil

from logger import BaseLog
# from main_debug import TaskConfig
from config import node_config
from scheduler.status_code import CrawlerStatus, TaskStatus, SaverStatus
from utils.util import singleton


@singleton
class Task(object):

    def __init__(self):
        self.log = BaseLog('scheduler_control')
        self.TaskWorkingList = []
        self.TaskWaittingList = []
        self.__MaxTasksCount = self.get_max_task_count()
        # self.TaskQueue = queue.LifoQueue(self.__MaxTasksCount)

    def start_one_task(self, task_config: dict):
        """
        :param task_config:
        :return:
        """
        # self.tasksSet.add(taskConfig)
        self.TaskWorkingList.append(task_config)
        task_config.update({'TaskState': TaskStatus.Init.value})
        crawler_config = task_config.get('CrawlerConfig', {})
        task_name = task_config.get('TaskName')
        task_id = task_config.get('TaskId')
        self.log.info('{}, {}开始启动'.format(task_id, task_name))
        crawle_cls = self.get_crawler_class(crawler_config)
        if crawle_cls:
            try:
                crawler_theard = crawle_cls(crawler_config)
                crawler_theard.start()
                task_config['CrawlerInstance'] = crawler_theard
            except Exception as e:
                self.log.error('{}爬虫实例化失败, 错误原因如下:{}'.format(crawler_config, traceback.format_exc()))
                task_config['TaskState'] = TaskStatus.CrawlerInstanceError.value
        else:
            task_config['TaskState'] = TaskStatus.CrawlerNotFound.value

    @staticmethod
    def get_max_task_count():
        max = 0
        for k, v in node_config.items():
            max += int(v.get('MaxTaskCount'))
        return max

    def get_work_task_count(self, task_type=None) -> dict:
        task_count = {
            'request': 0,
            'browser': 0,
            'android': 0
        }
        for item in self.TaskWorkingList:
            crawler_type = item.get('CrawlerConfig').get('CrawlerType')
            if task_type is crawler_type:
                task_count[crawler_type] += 1
            else:
                task_count[crawler_type] += 1

        return task_count

    def get_wait_task_count(self, task_type=None) -> dict:
        task_count = {
            'request': 0,
            'browser': 0,
            'android': 0
        }
        for item in self.TaskWaittingList:
            crawler_type = item.get('CrawlerConfig').get('CrawlerType')
            if task_type is crawler_type:
                task_count[crawler_type] += 1
            else:
                task_count[crawler_type] += 1

        return task_count

    def main(self):
        while True:
            if self.TaskWaittingList:
                for task_conf in self.TaskWaittingList:
                    self.TaskWaittingList.remove(task_conf)
                    self.start_one_task(task_conf)
            else:
                self.get_all_tasks_detail()
            # time.sleep(2)

    def get_all_tasks_detail(self):
        """
            打印所有任务状态
        :return:
        """
        task_detail_dict = {}
        work_task = self.get_work_task_count()
        task_detail_dict.update(work_task)
        for k, v in task_detail_dict.items():
            print('{}任务有{}个 正在进行'.format(k, v))
        task_detail_dict = {}
        wait_task = self.get_wait_task_count()
        task_detail_dict.update(wait_task)

        for k, v in task_detail_dict.items():
            print('{}任务有{}个 排队'.format(k, v))

    def get_crawler_class(self, crawler_config: dict):
        """
            获取爬虫实例
        :param crawler_config:
        :return:
        """
        crawler_name = crawler_config.get('CrawlerName', '')
        crawler_type = crawler_config.get('CrawlerType', '').lower()
        try:
            crawler_module = importlib.import_module('{}.{}_{}'.format(crawler_name.lower(), crawler_name, crawler_type))
        except ModuleNotFoundError:
            self.log.error('未找到模块[{}.{}_{}]'.format(crawler_name.lower(), crawler_name, crawler_type))
            return None
        if not hasattr(crawler_module, 'Crawler{}'.format(crawler_name.title())):
            return None
        CrawlerClass = getattr(crawler_module, 'Crawler{}'.format(crawler_name.title()))
        return CrawlerClass

    def add_one_task(self, task_conf):
        task_conf['TaskState'] = TaskStatus.Waiting.value
        task_conf['CrawlerInstance'] = None
        self.TaskWaittingList.append(task_conf)
        # self.log.info('{}, {}已添加到任务队列'.format(task_conf.get('TaskId'), task_conf.get('TaskName')))

    def cancel_one_task(self, task_id):
        for _task in self.TaskWaittingList:
            if _task.get('TaskId') == task_id:
                _task.update({'CrawlerState': TaskStatus.Cancel.value})

        for _task in self.TaskWorkingList:
            if _task.get('TaskId') == task_id:
                _task.update({'CrawlerState': TaskStatus.Cancel.value})
                ins = _task.get('CrawlerInstance', None)
                if ins:
                    self._async_raise(ins.ident, SystemExit)

    @staticmethod
    def _async_raise(tid, exctype):
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

    def get_task_state(self, task_id=None) ->list:
        task_state_list = []
        self.__update_task_state()
        for _task in self.TaskWaittingList:
            task_state = {}
            task_state.update(_task)
            task_state_list.append(_task)
            del task_state['CrawlerInstance']
            if task_id == _task.get('TaskId', ''):
                return task_state_list
        for _task in self.TaskWaittingList:
            task_state = {}
            task_state.update(_task)
            task_state_list.append(_task)
            del task_state['CrawlerInstance']
            if task_id == _task.get('TaskId', ''):
                return task_state_list

        return task_state_list

    def __task_exception_handle(self, task_conf: dict):
        self.__task_clear(task_conf)

    def __task_clear(self, task_conf):

        ins = task_conf.get('CrawlerInstance')
        parent_cls_str = str(ins.__class__.__bases__[0]).lower()
        if 'request' in parent_cls_str:
            self.__request_task_exception(ins)
        if 'browser' in parent_cls_str:
            self.__browser_task_exception(ins)
        if 'android' in parent_cls_str:
            self.__android_task_exception(ins)
        ins.__del__()
        del task_conf['CrawlerInstance']

    def __request_task_exception(self, ins):
        """
        request-task clear
        :return:
        """
        if ins.session:
            ins.session.close()

    def __browser_task_exception(self, ins):
        """
        brower-task clear
        :return:
        """
        if ins.driver:
            ins.driver.quit()

    def __android_task_exception(self, ins):
        """
        android-task clear
        :return:
        """
        pass

    def __update_task_state(self):
        for _task in self.TaskWorkingList:
            _task = dict(_task)
            task_instance = _task.get('CrawlerInstance', None)
            if not task_instance:
                self.log.error('{} 该任务没有获取到实例'.format(_task))
                continue
            state = task_instance.get_state()
            if state == TaskStatus.Cancel.value:
                self.__task_clear(_task)

            if state.value == CrawlerStatus.CrawlerException.value or state.value == SaverStatus.SaverException.value:
                if state.value == 2:
                    _task.update({'TaskState': TaskStatus.CrawlerFailed.value})
                else:
                    _task.update({'TaskState': TaskStatus.SaverFailed.value})
                self.__task_exception_handle(_task)
                continue
            if state.value < CrawlerStatus.CrawlerEnd.value:
                _task.update({'TaskState': TaskStatus.CrawlerWorking.value})
            elif state.value < SaverStatus.SavererEnd.value:
                _task.update({'TaskState': TaskStatus.SaverWorking.value})
            else:
                _task.update({'TaskState': TaskStatus.SaverSuccess.value})

    def __task_done_handle(self):
        """
        任务正常结束时
        :return:
        """
        """
        上传任务日志
        上传数据
        """

# def main():
#
#     t = threading.Thread(target=task.main)
#     t.name = 'MainTheard'
#     t.setDaemon(True)
#     t.start()
#     # t.join()


if __name__ == '__main__':
    d1 = {}
    d2 = {'1': 2}
    d1.update(d2)
    print(d1)
    del d1['1']
    print(d1,d2)
    pass
