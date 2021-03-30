# -*- coding:utf-8  -*-
# @Time     : 2021-02-21 01:27
# @Author   : BGLB
# @Software : PyCharm

from scheduler.control import Task


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
    Task().start_one_task(TaskConfig)


if __name__ == '__main__':
    main()
