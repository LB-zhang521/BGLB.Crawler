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
from services.screen import start_screen, start_cmd

daemon_log = BaseLog('services', 'daemon')

_proc_info_list = []
_start_cmd_dict = {
    'screen': start_cmd,
    'crawler': '{} main.py'.format(sys.executable, os.path.join(BASE_DIR, 'main.py')),
    'daemon': '{} {}'.format(sys.executable, os.path.join(BASE_DIR, 'daemon.py')),
}


def daemon():
    c_pid = crawler_thread_start()
    s_pid = screen_thread_start()
    _proc_info_list.extend([psutil.Process(c_pid).as_dict(attrs=['exe', 'cmdline', 'pid']),
                            psutil.Process(s_pid).as_dict(attrs=['exe', 'cmdline', 'pid'])])
    while True:
        time.sleep(5)
        try:
            for i in range(len(_proc_info_list)):
                proc_info = _proc_info_list[i]
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
                _proc_info_list[i] = temp
        except Exception:
            daemon_log.error(traceback.format_exc())


def start_daemon():
    for proc in psutil.process_iter():
        _proc = proc.as_dict(attrs=['exe', 'cmdline', 'pid'])
        cmdlind = _proc.get('cmdline', [])
        if cmdlind and _start_cmd_dict.get('daemon') == ' '.join(cmdlind):
            pid = _proc.get('pid')
            try:
                p = psutil.Process(pid)
                print('{} Process running in {}'.format('daemon', pid))
                print('You can call: python manage.py restart')
                return
            except psutil.NoSuchProcess:
                pass

    try:
        cmd = _start_cmd_dict.get('daemon')
        # print(cmd)
        s = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
        print('daemon Process starting ...')
        time.sleep(5)
        p = psutil.Process(s.pid)
        crawler_pid = 0
        for i in p.children():
            if cmd == ' '.join(i.cmdline()):
                crawler_pid = i.pid
                break
        p.kill()
        if crawler_pid != 0:
            print('daemon Process start success  * * * pid-[{}]'.format(crawler_pid))
        else:
            print('daemon Process start error * * *')
    except Exception as e:
        print(traceback.format_exc())


def crawler_thread_start():
    cmd = _start_cmd_dict.get('crawler')
    print('crawler Process starting')
    s = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
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
    print('screen Process starting')
    screen_pid = start_screen()
    if screen_pid != 0:
        daemon_log.info('screen Process start success  * * * pid-[{}]'.format(screen_pid))
    else:
        daemon_log.warn('screen Process start error * * *')
    return screen_pid


def stop(proc_name: str = ''):
    _cmdline = []
    if _start_cmd_dict.get(proc_name, ''):
        stop = True
        _cmdline.append(_start_cmd_dict.get(proc_name, ''))
    else:
        stop = False
        _cmdline.extend(list(_start_cmd_dict.values()))
    for proc in psutil.process_iter():
        _proc = proc.as_dict(attrs=['exe', 'cmdline', 'pid'])
        cmdlind = _proc.get('cmdline')
        for i in _cmdline:
            if cmdlind and i == ' '.join(cmdlind):
                pid = _proc.get('pid')
                try:
                    p = psutil.Process(pid)
                    p.kill()
                    # _proc_info_list.remove(_proc)
                    print('{} Process kill success'.format(cmdlind))
                except psutil.NoSuchProcess:
                    print("{} 进程已停止运行")
                if stop:
                    return


def restart():
    stop()
    print('stop success * * *')
    start_daemon()
    print('restart success * * *')


def statu():
    p1 = psutil.Process(_proc_info_list[0].get('pid'))
    p2 = psutil.Process(_proc_info_list[1].get('pid'))
    print("crawler is running:{} ****".format(p1.is_running()))
    print("screen is running:{} ****".format(p2.is_running()))


if __name__ == '__main__':
    daemon()
