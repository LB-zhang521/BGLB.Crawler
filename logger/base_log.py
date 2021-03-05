# -*- coding:utf-8  -*-
# @Time     : 2021-02-21 02:32
# @Author   : BGLB
# @Software : PyCharm

import logging
import os
import re
import sys
import threading
from logging.handlers import TimedRotatingFileHandler
import colorlog
from config import DEBUG, LOG_CONFIG
from utils.common.tosay import Tosay
"""
    日志记录
    ./log/[crawer]/[spyider]/[lever.log]
    ./log/[saver]/[spyider]/[lever]
    
    每个模块一个日志  log - models:[crawler] - spider
    日志分级 -【爬虫脚本，数据存储，】
"""

lock = threading.Lock()
_say_thread = Tosay()
_say_thread.start()


class BaseLog(object):

    LOG_CONFIG['LOG_ROOT_DIR'] = LOG_CONFIG['LOG_ROOT_DIR']
    LOG_CONFIG['LOG_COLOR_CONFIG'] = LOG_CONFIG['LOG_COLOR_CONFIG']
    def __init__(self, _module, spider=''):

        self.log_dir = os.path.join(LOG_CONFIG['LOG_ROOT_DIR'], _module, spider)
        self.log_name = '_'.join([_module, spider])  # 决定了日志最小区分单位
        self.backup_count = 20
        os.makedirs(self.log_dir, exist_ok=True)

        self.formatter_console = colorlog.ColoredFormatter(
            '%(log_color)s'
            '%(asctime)s: [%(process)d %(thread)d] - [{}] [{}] - [%(levelname)s]: %(message)s'.format(_module, spider),
            log_colors=LOG_CONFIG['LOG_COLOR_CONFIG'])

        self.formatter_file = logging.Formatter(
            '%(asctime)s: [%(process)d %(thread)d] - [{}] [{}] - [%(levelname)s]: %(message)s'.format(_module, spider))

        # 记录起来，用于回收
        self.stream_console_handler = None
        self.file_handler_dict = {}
        self.say_thread = _say_thread
        # 一个logger对应多个handler
        self.logger = logging.getLogger(self.log_name)
        if DEBUG:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.__add_handler()

    def __del__(self):
        try:
            self.__delete_logger_handlers()
            if self.say_thread:
                self.say_thread.kill()
        except Exception as e:
            raise e

    def __add_handler(self):
        """
        给logger绑定多个文件handler对应不同日志等级和一个console handler
        :return:
        """

        # 首先清空掉logger的handles，否则可能遇到日志重复的问题
        for h in self.logger.handlers:
            self.logger.removeHandler(h)
        self.logger.handlers = []

        self.__add_handler_stream()

        # 每个等级一个日志文件
        for level in [logging.DEBUG, logging.INFO, logging.ERROR]:
            self.__add_handler_timed_rotate(level)

    def __delete_logger_handlers(self):
        try:
            logging.Logger.manager.loggerDict.pop(self.log_name)
            self.logger.removeHandler(self.stream_console_handler)
            for h in self.file_handler_dict:
                self.logger.removeHandler(h)
            self.logger.handlers = []
        except Exception as e:
            print(e)

    def __add_handler_stream(self):
        """
        :return:
        """
        self.stream_console_handler = logging.StreamHandler(stream=sys.stdout)
        if DEBUG:
            self.stream_console_handler.setLevel(logging.DEBUG)
        else:
            self.stream_console_handler.setLevel(logging.INFO)
        self.stream_console_handler.setFormatter(self.formatter_console)

        self.logger.addHandler(self.stream_console_handler)

    def __add_handler_timed_rotate(self, level):
        """
        记录日志，并实现定期删除日志功能
        :return:
        """
        log_file_path = os.path.join(self.log_dir, logging.getLevelName(level).lower()+'.log')
        handler = TimedRotatingFileHandler(filename=log_file_path, encoding='utf-8', when='M', interval=1,
                                           backupCount=5)
        handler.suffix = '%Y%m%d.bak'
        handler.extMatch = re.compile(r'^\d{8}.log$')
        handler.setFormatter(self.formatter_file)
        handler.setLevel(level)

        self.logger.addHandler(handler)
        self.file_handler_dict[level] = handler

    def __log(self, message, lever, **kwargs):
        """

        :param message:
        :param lever:
        :param kwargs:
        :return:
        """
        LEVER = {
            'CRITICAL': 50,
            'FATAL': 50,
            'ERROR': 40,
            'WARN': 30,
            'WARNING': 30,
            'INFO': 20,
            'DEBUG': 10,
            'NOTSET': 0,
        }

        lock.acquire(timeout=.5)
        if kwargs.get('tosay', True):
            if self.say_thread:
                self.say_thread.push_text(message)
        self.logger.log(LEVER[lever], message)
        if lock.locked():
            lock.release()


    def debug(self, message, module='', lineno=0, **kwargs):
        """
        :param message:
        :param module: sys._getframe().f_code.co_name
        :param lineno: sys._getframe().f_lineno
        :return:
        """
        msg = self.format_msg(message, module, lineno)
        self.__log(msg, 'DEBUG', **kwargs)

    def info(self, message, module='', lineno=0, **kwargs):
        msg = self.format_msg(message, module, lineno)
        self.__log(msg, 'INFO', **kwargs)

    def warn(self, message, module='', lineno=0, **kwargs):
        msg = self.format_msg(message, module, lineno)
        self.__log(msg, 'WARNING', **kwargs)

    def error(self, message, module='', lineno=0, **kwargs):
        msg = self.format_msg(message, module, lineno)
        self.__log(msg, 'ERROR', **kwargs)

    def format_msg(self, message, module, lineno):
        message = str(message)
        if module:
            msg = '{}[line:{}] {}'.format(module, lineno, message)
        else:
            msg = '{}'.format(message)
        return msg


if __name__ == '__main__':
    # log_test = BaseLog('crawler', 'baidu')
    # log_test.debug("出错")
    # log_test.info("test")
    # log_test.warn("test")
    # main()
    # logger.debug('ss')
    # logger.error("error")
    pass