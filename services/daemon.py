# -*- coding:utf-8  -*-
# @Time     : 2021-04-07 00:02
# @Author   : BGLB
# @Software : PyCharm
import os
import subprocess
import sys
import time
import traceback

import psutil

from config import BASE_DIR
from logger import BaseLog
from services.screen import start_screen

daemon_log = BaseLog('services', 'daemon')

proc_info_list = []


def daemon():
    time.sleep(1)
    c_pid = crawler_thread_start()
    s_pid = screen_thread_start()
    proc_info_list.extend([psutil.Process(c_pid).as_dict(attrs=['exe', 'cmdline', 'pid']),
                           psutil.Process(s_pid).as_dict(attrs=['exe', 'cmdline', 'pid'])])
    while True:
        time.sleep(5)
        try:
            for i in range(len(proc_info_list)):
                proc_info = proc_info_list[i]
                try:
                    _proc = psutil.Process(proc_info.get('pid'))
                    cmd = _proc.cmdline()
                    if not cmd:
                        break
                    if cmd and proc_info.get('cmdline') == cmd:
                        continue
                except psutil.NoSuchProcess as e:
                    pass
                pid = 0
                if 'main.py' in proc_info.get('cmdline')[-1]:
                    pid = crawler_thread_start()
                elif 'screen' in proc_info.get('exe'):
                    pid = screen_thread_start()
                if pid == 0:
                    break
                temp = psutil.Process(pid).as_dict(attrs=['exe', 'cmdline', 'pid'])
                proc_info_list[i] = temp
        except Exception:
            daemon_log.error(traceback.format_exc())


def start_daemon():
    try:
        cmd = '{} {}'.format(sys.executable, os.path.join(BASE_DIR, 'daemon.py'))
        s = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, universal_newlines=True,
                             encoding='utf-8', shell=True)
        time.sleep(5)
        p = psutil.Process(s.pid)
        crawler_pid = 0
        for i in p.children():
            if cmd == ' '.join(i.cmdline()):
                crawler_pid = i.pid
                break
        p.kill()
        if crawler_pid != 0:
            print('daemon Process success start * * * pid-[{}]'.format(crawler_pid))
        else:
            print('daemon Process start error * * *')
    except Exception as e:
        print(traceback.format_exc())


def crawler_thread_start():
    crawler_path = os.path.join(BASE_DIR, 'main.py')
    cmd = '{} main.py'.format(sys.executable, crawler_path)
    s = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE,
                         universal_newlines=True, encoding='utf-8',
                         shell=True)
    time.sleep(3)
    p = psutil.Process(s.pid)
    crawler_pid = 0
    for i in p.children():
        if cmd == ' '.join(i.cmdline()):
            crawler_pid = i.pid
            break
    p.kill()
    if crawler_pid != 0:
        daemon_log.info('crawler Process start success  * * * pid-[{}]'.format(crawler_pid))
    else:
        daemon_log.warn('crawler Process start error * * *')
    return crawler_pid


def screen_thread_start():
    screen_pid = start_screen()
    if screen_pid != 0:
        daemon_log.info('screen Process start success  * * * pid-[{}]'.format(screen_pid))
    else:
        daemon_log.warn('screen Process start error * * *')
    return screen_pid


def crawler_stop():
    p = psutil.Process(proc_info_list[0].get('pid'))
    p.kill()


def screen_stop():
    p = psutil.Process(proc_info_list[1].get('pid'))
    p.kill()
    pass


def deamon_stop(pid):
    p = psutil.Process(pid)
    p.kill()


def statu():
    p1 = psutil.Process(proc_info_list[0].get('pid'))
    p2 = psutil.Process(proc_info_list[1].get('pid'))
    print("crawler is running:{} ****".format(p1.is_running()))
    print("screen is running:{} ****".format(p2.is_running()))


if __name__ == '__main__':
    daemon()


