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

background_task_pool = 'http://127.0.0.1:8001/spider'

node_capacity = ['request', 'android', 'browser']

node_config = {
    'request': {
        'MaxTaskCount': 10,

    },
    'android': {
        'MaxTaskCount': 1,
        'devices': {
            "serial": '851QFDSJ22TZ6',
            'password': '0000',
            'screen': True,
            'enable': True,
        },

    },
    'browser': {
        'MaxTaskCount': 10,
        'ChromeVersion': "",
    }
}

if __name__ == '__main__':
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    for i in os.environ:
        print(i)
