# -*- coding:utf-8  -*-
# @Time     : 2021-02-25 23:34
# @Author   : BGLB
# @Software : PyCharm

"""
    全局配置
"""
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEBUG = True

CODE_TEMPLATE = {
    'NOTE': {
        '': 'utf-8',
        'Time': '%Y-%m-%d %H:%M:%S',
        'Author': 'BGLB',
        'Software': 'PyCharm'
    }
}

LOG_CONFIG = {
    'LOG_COLOR_CONFIG': {
        'DEBUG': 'white',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
    },
    'LOG_ROOT_DIR': os.path.join(BASE_DIR, 'log')
}

node_config = {
    'request': {
        'MaxTaskCount': 10,

    },
    'android': {
        'MaxTaskCount': 1,
        'devices': {
            "SN": '851QFDSJ22TZ6',
            'password': '0000',

        }
    },
    'brower': {
        'MaxTaskCount': 1,
        'ChromeVersion': "",
    }
}
if __name__ == '__main__':
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
