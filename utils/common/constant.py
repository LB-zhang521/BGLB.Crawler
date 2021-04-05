# -*- coding:utf-8  -*-
# @Time     : 2021-03-04 21:47
# @Author   : BGLB
# @Software : PyCharm
"""
    静态常量数据
"""
import os
import platform

from config import BASE_DIR


def _chromedriver():
    """
    chromedriver 路径
    :return:
    """
    if 'Windows' in platform.system():
        return os.path.join(BASE_DIR, r'crawler\chromedriver\chromedriver.exe')
    return os.path.join(BASE_DIR, r'crawler\chromedriver\chromedriver')


def _adbexecpath():
    """
    abd 执行路径
    :return:
    """
    return os.path.join(BASE_DIR, r'crawler\adb\adb.exe')


def _screenpath():
    return os.path.join(BASE_DIR, r'utils\screen\scrcpy.exe')


class StaticPath(object):
    chromedriver = _chromedriver()
    adbexecpath = _adbexecpath()
    screenpath = _screenpath()


if __name__ == '__main__':
    print(StaticPath.chromedriver)
