# -*- coding:utf-8  -*-
# @Time     : 2021-02-25 23:33
# @Author   : BGLB
# @Software : PyCharm

from scheduler.control import Task

TaskConfig = {
    "TaskId": "13465786",
    "TaskName": "测试百度",
    "CrawlerConfig": {
        "CrawlerName": "weixin",
        "CrawlerType": "android",  # [request, browser, android]
    },
    "OrtherConfig": {

    }

}


def main():
    Task().start_one_task(TaskConfig)


main()
