# -*- coding:utf-8  -*-
# @Time     : 2021-03-07 22:00
# @Author   : BGLB
# @Software : PyCharm
import os


from utils.util import code_template


def create_project(projece_name, crawler_type):
    """

    :param projece_name: str
    :param crawler_type: str
    :return:
    """
    support_type = ['request', 'android', 'browser']
    if crawler_type in support_type:
        print('创建爬虫项目-{}中……'.format(projece_name))
        os.makedirs('{}'.format(projece_name), exist_ok=True)
        with open('./{}/{}_{}.py'.format(projece_name, projece_name, crawler_type), 'w', encoding='utf8') as f:
            code_te = code_template(projece_name, crawler_type)
            f.write(code_te)
    else:
        print('不支持的type')


if __name__ == '__main__':
    create_project('souhu', 'request')