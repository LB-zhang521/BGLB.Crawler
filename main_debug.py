# -*- coding:utf-8  -*-
# @Time     : 2021-02-25 23:33
# @Author   : BGLB
# @Software : PyCharm

import os
import time
from scheduler.control import Task


TaskConfig = {
    "TaskId": "13465786",
    "TaskName": "测试百度",
    "CrawlerConfig": {
        "CrawlerName": "baidu",
        "CrawlerType": "browser",  # [request, brower, android]
    },
    "OrtherConfig": {

    }

}


def main():
    Task().start_one_task(TaskConfig)


main()



