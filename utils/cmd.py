# -*- coding:utf-8  -*-
# @Time     : 2021-02-21 02:23
# @Author   : BGLB
# @Software : PyCharm
from logger.LogBase import Loggings
class CmdBase():
    log = Loggings()
    def __init__(self):
        super(CmdBase).__init__()


if __name__ == '__main__':
    ss = CmdBase()
    # print(ss.log)
    ss.log.error('niasdu')