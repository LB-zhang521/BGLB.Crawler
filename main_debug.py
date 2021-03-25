# -*- coding:utf-8  -*-
# @Time     : 2021-02-25 23:33
# @Author   : BGLB
# @Software : PyCharm

import os
import time
from scheduler.control import task


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


def _main():
    task.add_one_task(TaskConfig)
    pass

# main()
_main()



