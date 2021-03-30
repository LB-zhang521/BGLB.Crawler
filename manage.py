# -*- coding:utf-8  -*-
# @Time     : 2021-03-07 22:00
# @Author   : BGLB
# @Software : PyCharm
import os
import sys
import threading
import time

import flask
import psutil


def code_template(project_name: str, crawler_type:str):
    """
        代码模板
    :return: str
    """
    code_main = """
from crawler.{crawler_type} import Crawler{crawler_type}


class Crawler{project_name}(Crawler{crawler_type}):

    def __init__(self, crawler_config):
        super().__init__(crawler_config)
      
    def spider(self):
        pass
          
    def saver(self):
        pass
    
    def __del__(self):
        super().__del__()
""".format(crawler_type=crawler_type.title(), project_name=project_name.title())


    return code_main


def create_spider(project_name):

    if os.path.exists(project_name):
        print('已存在项目{}'.format(project_name))
        return False

    print('创建爬虫项目-{}中……'.format(project_name))
    os.makedirs('{}'.format(project_name), exist_ok=True)


def add_spider(project_name, crawler_type):
    """

    :param project_name: str
    :param crawler_type: str
    :return:
    """
    support_type = ['request', 'android', 'browser']
    filename = '{}_{}'.format(project_name, crawler_type)
    filepath = '{}/{}'.format(project_name, filename)
    if os.path.exists(filepath):
        print('已存在脚本{}'.format(filepath))
        return
    if crawler_type in support_type:
        with open('./{}/{}_{}.py'.format(project_name, project_name, crawler_type), 'w', encoding='utf8') as f:
            code_te = code_template(project_name, crawler_type)
            f.write(code_te)
    else:
        print('不支持的type')

TaskConfig = {
    "TaskId": "13465786",
    "TaskName": "测试百度",
    "CrawlerConfig": {
        "CrawlerName": "baidu",
        "CrawlerType": "browser",  # [request, brower, android]
    },
    "OrtherConfig": {

    }

}


def check_program(name, cmdline):
    if name == 'main':
        if cmdline and len(cmdline) >= 2 and cmdline[0].endswith('python') and cmdline[1].endswith('main.py'):
            return True
    elif name == 'node_appium':
        if cmdline and len(cmdline) == 8 and 'node' == cmdline[0] and 'appium' in cmdline[1]:
            return True
    return False


def check_if_program_working(name):
    match_pid = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'cmdline'])
            cmdline = pinfo['cmdline']
            # print(cmdline)
            if check_program(name, cmdline):
                match_pid.append(pinfo['pid'])
        except psutil.NoSuchProcess:
            pass
    return match_pid


def daemon():
    task = Task()
    task.daemon().start()


def server_http():
    os.system('start_web.bat')

if __name__ == '__main__':
    args = sys.argv
    cmd_support = ['create', 'add', 'start', 'start_web']
    default_out = "支持的命令有： 1. create 2. add"
    if len(args) <= 1:
        print(default_out)
    else:
        if args[1] == cmd_support[0]:
            project_name = input('请输入爬虫项目名称：').replace('\n', '').replace(' ', '').lower()
            if project_name:
                create_spider(project_name)
        if args[1] == cmd_support[1]:
            project_name = input('请输入爬虫项目名称：').replace(' ', '').replace('\n', '').lower()
            crawler_type = input('请输入爬虫脚本类型：').replace(' ', '').replace('\n', '').lower()
            if project_name and crawler_type:
                add_spider(project_name, crawler_type)
        if args[1] == cmd_support[2]:
            try:
                from scheduler.control import Task
                from services.web import app
                task = Task()
                # app.run()
                t1 = threading.Thread(target=server_http)
                t2 = threading.Thread(target=daemon)
                t1.start()
                t2.start()

            except Exception:
                pass
        if args[1] == cmd_support[3]:
            try:
                from scheduler.control import Task
                from services.web import app
                # task = Task()
                # app.run()
                # t1 = threading.Thread(target=app.run)
                # t2 = task.daemon()

                # t1.start()
                # t2.start()
                app.run()
                # while True:
                #     pass
                # time.sleep(.5)
            except Exception:
                pass


        # print(str(threading.enumerate()))