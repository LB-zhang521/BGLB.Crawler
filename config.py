# -*- coding:utf-8  -*-
# @Time     : 2021-02-25 23:34
# @Author   : BGLB
# @Software : PyCharm

"""
    全局配置
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True

LOG_CONFIG = {
    'LOG_COLOR_CONFIG': {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
    },
    'LOG_ROOT_DIR': os.path.join(BASE_DIR, 'log')
}

SAY_CONFIG = {
    "issay": True,
    'rate': 500,  # 每分钟播报字数
}

node_config = {
    "request": {
        "MaxTaskCount": 10,

    },
    "android": {
        "MaxTaskCount": 1,
    },
    "brower": {
        "MaxTaskCount": 5,
        "ChromeVersion": "",
    }
}
