# -*- coding:utf-8  -*-
# @Time     : 2021-02-28 03:08
# @Author   : BGLB
# @Software : PyCharm
from enum import Enum, IntEnum


class TaskStatus(IntEnum):

    Init = 0  # 待处理
    CrawlerWorking = 1  # 数据爬取中
    CrawlerSuccess = 2  # 数据爬取完成
    SaverWorking = 3    # 数据存储中
    SaverSuccess = 4    # 数据存储完成
    CrawlerFailed = -1  # 数据爬取失败
    SaverFailed = -2    # 数据存储失败


class CrawlerFailedStatus(IntEnum):

    pass


class SaverFailStatus(IntEnum):

    pass

