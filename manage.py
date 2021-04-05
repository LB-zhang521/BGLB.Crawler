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

from scheduler.control import Task
# from services.web import create_web


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
task = Task()
# app = create_web(task)


def web_daemon():
    time.sleep(2)
    while True:
        web_need_restart = True
        crawler_need_restart = True
        for proc in psutil.process_iter():
            prinfo = proc.as_dict(attrs=['exe', 'cmdline', 'pid'])
            # print(prinfo)
            # return
            if '{}'.format(sys.executable) in str(prinfo['exe']) and prinfo['cmdline'][-1] == 'start_web':
                web_need_restart = False
            if '{}'.format(sys.executable) in str(prinfo['exe']) and prinfo['cmdline'][-1] == 'start':
                crawler_need_restart = False
        # print("==============================="+str(threading.active_count()))
        if web_need_restart:
            os.system('start "start_web"  cmd /c {} ./manage.py start_web'.format(sys.executable))
            time.sleep(5)
        if crawler_need_restart:
            os.system('start "start"  cmd /c {} ./manage.py start'.format(sys.executable))
            time.sleep(5)


def daemon():
    task.daemon().start()


if __name__ == '__main__':
    args = sys.argv
    cmd_support = ['create', 'add', 'start', 'start_web', 'start_crawler']
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
                # app.run()
                daemon()
                t1 = threading.Thread(target=web_daemon)
                t1.setDaemon(True)
                t1.start()

            except Exception:
                pass
        if args[1] == cmd_support[3]:
            try:
                # app.run()
                pass
            except Exception:
                pass


