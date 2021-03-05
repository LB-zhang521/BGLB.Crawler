# -*- coding:utf-8  -*-
# @Time     : 2021-02-21 01:27
# @Author   : BGLB
# @Software : PyCharm
import time

from config import node_config
from logger import BaseLog
from scheduler.control import start_one_task
import pyttsx3

TaskConfig = {
    "TaskId": "132456789",
    "TaskName": "测试-百度抓取任务",
    "CrawlerConfig": {
        "CrawlerName": "baidu",
        "CrawlerType": "request",  # [request, brower, android]
    },
    "OrtherConfig": {

    }

}


def main():
    start_one_task(TaskConfig)
    # engine.say('你好')
    # engine.say('捕获到页面出现验证码, 请处理! 判断为未注册')
    #
    # # 注意，没有本句话是没有声音的
    # engine.runAndWait()
# engine = pyttsx3.init()


if __name__ == '__main__':
    main()
