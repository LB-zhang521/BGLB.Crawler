# -*- coding:utf-8  -*-
# @Time     : 2021-03-28 22:24
# @Author   : BGLB
# @Software : PyCharm

from flask import Flask, redirect, url_for
app = Flask(__name__)
from scheduler.control import Task
task = Task()


@app.route('/')
def index():

    return "admin"


@app.route('/start')
def start():
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
    task.add_one_task(TaskConfig)
    return 'start'


@app.route('/statu')
def get_state():
    return str(task.get_task_state('13465786'))


@app.route('/cancel')
def cancel():
    task.cancel_one_task('13465786')

    return 'cancel'


if __name__ == '__main__':
    app.run(debug=True)
