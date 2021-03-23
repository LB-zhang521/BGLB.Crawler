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
from config import node_config
from scheduler.status_code import CrawlerStatus, TaskStatus, SaverStatus
import queue


class Task(object):

    def __init__(self):
        self.TaskQueue = None
        self.log = BaseLog('scheduler_control')
        self.TaskWorkingList = []
        self.TaskWaittingList = []
        self.__MaxTasksCount = self.get_max_task_count()
        self.TaskQueue = queue.LifoQueue(self.__MaxTasksCount)

    def start_one_task(self, taskConfig: dict):
        """
        :param taskConfig:
        :return:
        """
        # self.tasksSet.add(taskConfig)
        taskConfig.update({'TaskState': TaskStatus.Init.value})
        crawler_config = taskConfig.get('CrawlerConfig', {})
        task_name = taskConfig.get('TaskName')
        task_id = taskConfig.get('TaskId')
        self.log.info('{}, {}开始启动'.format(task_id, task_name))
        crawle_cls = self.get_crawler_class(crawler_config)
        if crawle_cls:
            try:
                crawler_instance = crawle_cls(crawler_config)
                crawler_instance.start()
                taskConfig['CrawlerInstance'] = crawler_instance
            except Exception:
                self.log.error('{}爬虫实例化失败'.format(crawler_config))
                taskConfig['TaskState'] = TaskStatus.CrawlerInstanceError.value
        else:
            taskConfig['TaskState'] = TaskStatus.CrawlerNotFound.value

    @staticmethod
    def get_max_task_count():
        max = 0
        for k, v in node_config.items():
            max += int(v.get('MaxTaskCount'))
        return max

    def get_work_task_count(self, task_type=None) -> dict:
        task_count = {
            'request': 0,
            'brower': 0,
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
            'brower': 0,
            'android': 0
        }
        for item in self.TaskWorkingList:
            crawler_type = item.get('CrawlerConfig').get('CrawlerType')
            if task_type is crawler_type:
                task_count[crawler_type] += 1
            else:
                task_count[crawler_type] += 1

        return task_count

    def main(self):
        while True:
            if not self.TaskQueue.empty():
                task_conf = self.TaskQueue.get()
                self.TaskWorkingList.append(task_conf)
                self.start_one_task(task_conf)
            self.get_all_tasks_detail()

    def get_all_tasks_detail(self):
        task_detail_dict = {
            'request':  0,
            'brower':  0,
            'android': 0
        }

        for k, v in task_detail_dict.items():
            if v > 0:
                print('{}任务有{}个 正在排队'.format(k, v))
            else:
                print('{}任务空闲'.format(k))
        task_detail_dict = {
            'request': 0,
            'brower': 0,
            'android': 0
        }
        for task in self.TaskWorkingList:
            print(task)
            task = dict(task)
            crawler_type = task.get('CrawlerConfig').get('CrawlerType')
            task_detail_dict[crawler_type] += 1
        for k, v in task_detail_dict.items():
            if v > 0:
                print('{}任务有{}个 正在进行'.format(k, v))
            else:
                print('{}任务空闲'.format(k))

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
        # task_conf['CrawlerInstance'] = None
        self.TaskQueue.put(task_conf)
        self.log.info('{}, {}已添加到任务队列'.format(task_conf.get('TaskId'), task_conf.get('TaskName')))

    def cancel_one_task(self, ):
        pass

    def get_task_status(self):

        pass

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

    def get_task_state(self, task_id):
        task_state = {}
        for _task in self.TaskQueue:
            if task_id == _task.get('TaskId', ''):
                task_state.update(_task)
                task_state.pop('CrawlerInstance')
                return task_state
        self.__change_task_state()
        for _task in self.TaskWorkingList:
            if task_id == _task.get('TaskId', ''):
                task_state.update(_task)
                task_state.pop('CrawlerInstance')
                if TaskStatus(_task.get('TaskState')) == TaskStatus.CrawlerFailed or TaskStatus(_task.get(
                        'TaskState')) == TaskStatus.SaverFailed:
                    self.TaskWorkingList.remove(_task)
                return task_state

    def __task_exception_handle(self, task_conf: dict):
        task_conf.update({'CrawlerInstance': None})

    def __change_task_state(self):
        for _task in self.TaskWorkingList:
            _task = dict(_task)
            task_instance = _task.get('CrawlerInstance', None)
            if not task_instance:
                self.log.error('{} 该任务没有获取到实例'.format(_task))
                continue
            state = task_instance.get_state()
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



task = Task()
t = threading.Thread(target=task.main)
t.name = 'MainTheard'
t.setDaemon(True)
t.start()
time.sleep(2)
task.add_one_task(TaskConfig)