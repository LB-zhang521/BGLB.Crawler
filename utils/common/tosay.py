# -*- coding:utf-8  -*-
# @Time     : 2021-03-06 00:14
# @Author   : BGLB
# @Software : PyCharm
import re
import threading
import time


import pyttsx3

from config import ISSAY, DEBUG

_lock = threading.Lock()


class Tosay(threading.Thread):

    def __init__(self):
        super().__init__()
        self.__text_list = []
        self.__priority_list = []
        self.__last_list = []
        self.engine = None
        self.__is_push = False
        self.name = 'to_say'
        self.__is_kill = False

    def __ready_say(self):
        self.engine = pyttsx3.init(debug=DEBUG)
        self.engine.setProperty('rate', 400)

    def push_text(self, text: str, lever=''):
        """
        :param text: 文本
        :param lever: 优先级 - ['priority', 'last']
        :return:
        """
        while not _lock.locked():
            _lock.acquire()
        self.__is_push = True
        rule = re.compile(u"[^a-zA-Z0-9\u4e00-\u9fa5]")
        text_format = rule.sub('', text)
        # print(text_format)
        if lever == 'priority':
            self.__priority_list.insert(0, text_format)
        if lever == 'last':
            self.__last_list.append(text_format)
        if not lever:
            self.__text_list.append(text_format)
        self.__priority_list.extend(self.__text_list)
        self.__text_list = []
        self.__priority_list.extend(self.__last_list)
        self.__last_list = []
        self.__text_list = self.__priority_list
        self.__priority_list = []
        # print(self.__text_list)
        self.__is_push = False
        _lock.release()

    def run(self) -> None:
        self.__ready_say()
        while ISSAY:
            if self.__is_push and _lock.locked():
                continue
            # print(self.__text_list)
            self._say_text_list()

            if self.__is_kill and len(self.__text_list) == 0:
                break

    def _say_text_list(self):
        _lock.acquire()
        say_text_length = 0
        text_list = self.__text_list
        for i in range(len(text_list)):

            # self.__text_list.remove(text)
            # print(text)
            self.engine.say(text_list[i])
            # pyttsx3.speak(text)
            say_text_length += len(text_list[i])
            if say_text_length//20 > 5:
                self.engine.runAndWait()
                say_text_length = 0
            if len(self.__text_list) == i+1:
                self.engine.runAndWait()
                say_text_length = 0
                self.__text_list = []
        if _lock.locked():
            _lock.release()

    def kill(self):
        self.__is_kill = True