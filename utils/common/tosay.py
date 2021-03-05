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
        # lock.locked()
        # _lock.acquire(timeout=.5)
        self.__is_push = True
        rule = re.compile(u"[^a-zA-Z0-9\u4e00-\u9fa5]")
        # ignore_bytes = ['\n', '\r', '\t', '\r\n', '[', ']', '{', '}', '.', '!', '.', ':', '']
        text_format = rule.sub('', text)
        time.sleep(0.3)
        # while not self.engine.isBusy():
        #     # self.engine.stop()
        #     # print('busy')
        #     # time.sleep(.5)
        #     pass
        if lever == 'priority':
            self.__priority_list.insert(0, text_format)
        if lever == 'last':
            self.__last_list.append(text_format)
        if not lever:
            self.__text_list.append(text_format)

        for text in self.__priority_list:
            self.__text_list.insert(0, text)
            self.__priority_list.remove(text)
        for text in self.__last_list:
            self.__text_list.append(text)
            self.__last_list.remove(text)
        self.__is_push = False
        # if _lock.acquire(timeout=.5):
        #     _lock.release()

    def run(self) -> None:
        self.__ready_say()
        while ISSAY:

            say_text_length = 0
            for text in self.__text_list:
                self.engine.say(text)
                say_text_length += len(text)
                self.__text_list.remove(text)

                if say_text_length // 20 > 2.5 or len(self.__text_list) == 0:

                    # if not self.engine.isBusy():
                    #     break
                    self.engine.runAndWait()
                    say_text_length = 0
            if self.__is_kill and len(self.__text_list) == 0:
                # print(self.engine.isBusy())
                return

    def kill(self):
        self.__is_kill = True