# -*- coding:utf-8  -*-
# @Time     : 2021-03-07 22:00
# @Author   : BGLB
# @Software : PyCharm
import os
import sys

from services.daemon import crawler_thread_start, screen_thread_start, start_daemon, stop, restart


def code_template(crawler_type: str):
    """
        代码模板
    :return: str
    """
    code_init = ''
    if crawler_type.lower() == 'android':
        code_init = """self.app_info = {
            'PackageName': '',
            'Activity': '',
            'IsReset': True,
            'IsWait': True,
            'AppName': ''
        } 
"""

    code_main = """
from crawler.{crawler_type} import Crawler{crawler_type}


class Crawler(Crawler{crawler_type}):

    def __init__(self, crawler_config):
        super().__init__(crawler_config)
        {code_init}
    def spider(self):
        pass

    def saver(self):
        pass

    def __del__(self):
        super().__del__()
""".format(crawler_type=crawler_type.title(), code_init=code_init)

    return code_main


def create_spider(project_name):
    if os.path.exists(project_name):
        print('已存在项目{}'.format(project_name))
        return False

    print('创建爬虫项目-{}中……'.format(project_name))
    os.makedirs('{}'.format(project_name), exist_ok=True)


def add_spider(project_name, crawler_type=None):
    """
    :param project_name: str
    :param crawler_type: str
    :return:
    """
    support_type = ['request', 'android', 'browser']

    if crawler_type is None:
        for _type in support_type:
            with open('./{}/{}.py'.format(project_name, _type), 'w', encoding='utf8') as f:
                code_te = code_template(_type)
                f.write(code_te)
        print('创建完成！')
    elif crawler_type in support_type:
        filename = '{}.py'.format(crawler_type)
        filepath = '{}/{}'.format(project_name, filename)
        if os.path.exists(filepath):
            print('已存在脚本{}')
            return
        with open('./{}'.format(filepath), 'w', encoding='utf8') as f:
            code_te = code_template(crawler_type)
            f.write(code_te)
        print('创建完成！')
    else:
        print('不支持的type')


if __name__ == '__main__':
    args = sys.argv
    cmd_support = ['create', 'add', 'start', 'start_crawler', 'start_screen', 'stop_screen', 'stop_crawler', 'stop',
                   'restart']

    if len(args) <= 1:
        print(''.join(cmd_support))
    else:
        pass
    if args[1] == cmd_support[0]:
        project_name = input('请输入爬虫项目名称：').replace('\n', '').replace(' ', '').lower()
        if project_name:
            create_spider(project_name)
            add_spider(project_name)
    if args[1] == cmd_support[1]:
        project_name = input('请输入爬虫项目名称：').replace(' ', '').replace('\n', '').lower()
        crawler_type = input('请输入爬虫脚本类型：').replace(' ', '').replace('\n', '').lower()
        if project_name and crawler_type:
            add_spider(project_name, crawler_type)
    if args[1] == cmd_support[2]:
        start_daemon()
    if args[1] == cmd_support[3]:
        crawler_thread_start()
    if args[1] == cmd_support[4]:
        screen_thread_start()
    if str(args[1]).startswith('stop'):
        proc = str(args[1]).split('_')[-1]
        proc.replace('stop', '')
        stop(proc)

    if args[1] == cmd_support[8]:
        restart()
