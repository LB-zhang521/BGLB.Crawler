# -*- coding:utf-8  -*-
# @Time     : 2021-02-21 01:27
# @Author   : BGLB
# @Software : PyCharm

from config import node_config
from logger import BaseLog
from scheduler.control import start_one_task

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


if __name__ == '__main__':
    main()