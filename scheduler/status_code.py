# -*- coding:utf-8  -*-
# @Time     : 2021-02-28 03:08
# @Author   : BGLB
# @Software : PyCharm
from enum import Enum, IntEnum


class TaskStatus(Enum):

    Waiting = '排队中'
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
    CrawlerException = 2
    CrawlerEnd = 3


class SaverStatus(IntEnum):
    SaverStart = 4
    Savering = 5
    SaverException = 6
    SavererEnd = 7


if __name__ == '__main__':

    class Base:
        def __init__(self):
            self.state = CrawlerStatus.CrawlerStart

        def get_text(self):
            return self.state

    class Chile(Base):
        def __init__(self):
            super().__init__()
            self.state = CrawlerStatus.Crawlering

    class Sun(Base):
        def __init__(self):
            super().__init__()
            self.state = CrawlerStatus.CrawlerException

    c = Chile()

    print(super(c).get_text())



