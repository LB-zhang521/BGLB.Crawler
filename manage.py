# -*- coding:utf-8  -*-
# @Time     : 2021-03-07 22:00
# @Author   : BGLB
# @Software : PyCharm
import os
import sys
import threading
import time
import psutil

from scheduler.control import Task
# from services.web import create_web
from services.screen import start_screen
from utils.common.constant import StaticPath


def code_template(crawler_type:str):
    """
        代码模板
    :return: str
    """
    code_main = """
from crawler.{crawler_type} import Crawler{crawler_type}


class Crawler(Crawler{crawler_type}):

    def __init__(self, crawler_config):
        super().__init__(crawler_config)
      
    def spider(self):
        pass
          
    def saver(self):
        pass
    
    def __del__(self):
        super().__del__()
""".format(crawler_type=crawler_type.title())


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


def daemon():
    time.sleep(2)
    while True:
        screen_need_restart = True
        for proc in psutil.process_iter():
            prinfo = proc.as_dict(attrs=['exe', 'pid'])
            # print(prinfo)
            # return
            if StaticPath.screenpath == str(prinfo['exe]):
                screen_need_restart = True
        print("==============================="+str(threading.active_count()))
        if not screen_need_restart:
            threading.Thread(target=start_screen).start()
            time.sleep(10)


if __name__ == '__main__':
    args = sys.argv
    cmd_support = ['create', 'add', 'start', 'start_crawler', 'start_screen']
    default_out = "支持的命令有： 1. create 2. add"
    if len(args) <= 1:
        print(default_out)
    else:
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
            try:
                # start_screen()
                # threading.Thread(target=start_screen).start()
                Task().main_thread().start()
                t = threading.Thread(target=daemon)
                t.setDaemon(True)
                t.start()
            except Exception:
                pass
        if args[1] == cmd_support[3]:
            try:
                Task().main_thread().start()
            except Exception:
                pass
        if args[1] == cmd_support[4]:
            threading.Thread(target=start_screen).start()

