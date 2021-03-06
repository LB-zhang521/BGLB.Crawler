# -*- coding:utf-8  -*-
# @Time     : 2021-03-06 00:14
# @Author   : BGLB
# @Software : PyCharm
import re
import threading
import time


import pyttsx3

from config import SAY_CONFIG, DEBUG

_lock = threading.Lock()


class Tosay(threading.Thread):

    def __init__(self):
        super().__init__()
        self.__text_list = []
        self.__priority_list = []
        self.__last_list = []
        self.engine = None
        self.__is_push = False
        self.name = 'sayTheard'
        self.__is_kill = False

    def __ready_say(self):
        self.engine = pyttsx3.init(debug=DEBUG)
        self.engine.setProperty('rate', SAY_CONFIG.get('rate', 400))

    def push_text(self, text: str, saylever=''):
        """
        :param text: 文本
        :param saylever: 优先级 - ['priority', 'last']
        :return:
        """
        while not _lock.locked():
            _lock.acquire()
        self.__is_push = True
        rule = re.compile(u"[^a-zA-Z0-9\u4e00-\u9fa5]")
        text_format = rule.sub('', text)
        # print(text_format)
        if saylever == 'priority':
            self.__priority_list.insert(0, text_format)
        if saylever == 'last':
            self.__last_list.append(text_format)
        if not saylever:
            self.__text_list.append(text_format)

        self.__is_push = False
        _lock.release()

    def run(self) -> None:
        self.__ready_say()
        while SAY_CONFIG.get('issay', False):
            if self.__is_push and _lock.locked():
                continue
            self.__priority_list.extend(self.__text_list)
            self.__text_list = []
            self.__text_list = self.__priority_list
            self.__priority_list = []
            self._say_text_list()
            if self.__is_kill and len(self.__text_list) == 0:
                break
        self._say_last_list()

    def _say_text_list(self):
        _lock.acquire()
        say_text_length = 0
        for i, text in enumerate(self.__text_list):
            self.engine.say(text)
            say_text_length += len(text)
            if say_text_length//20 > 5:
                self.engine.runAndWait()
                say_text_length = 0
        try:
            self.engine.runAndWait()
        except RuntimeError:
            print('**say run time')
        # say_text_length = 0
        self.__text_list = []
        if _lock.locked():
            _lock.release()

    def _say_last_list(self):
        for i, text in enumerate(self.__last_list):
            self.engine.say(text)
        self.engine.runAndWait()

    def kill(self):
        self.__is_kill = True