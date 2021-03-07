# -*- coding:utf-8  -*-
# @Time     : 2021-02-28 03:08
# @Author   : BGLB
# @Software : PyCharm
from enum import Enum, IntEnum


class TaskStatus(Enum):

    Init = '待处理'
    CrawlerWorking = '数据抓取中'
    CrawlerSuccess = '数据抓取完成'
    SaverWorking = '数据存储中'
    SaverSuccess = '数据存储完成'
    CrawlerFailed = '数据抓取失败'
    SaverFailed = '数据存储失败'


class CrawlerStatus(IntEnum):
    CrawlerStart = 0
    Crawlering = 1
    CrawlerException = -1
    CrawlerEnd = 2


class SaverStatus(IntEnum):
    SaverParseFailed = -1
    pass


if __name__ == '__main__':
    print(TaskStatus.CrawlerFailed == TaskStatus.CrawlerFailed)