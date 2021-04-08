# -*- coding:utf-8  -*-
# @Time     : 2021-04-05 22:21
# @Author   : BGLB
# @Software : PyCharm

"""
    手机投屏
"""
import subprocess
import time

import psutil

from config import node_config
from logger import BaseLog
from utils.common.constant import StaticPath


device_info = node_config.get('android').get('devices')

screen_log = BaseLog('services', 'screen')


def _check_device_(serial):
    adb_exe = StaticPath.adbexecpath
    cmd = [adb_exe, '-s', serial, 'get-state']
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, encoding='utf-8')

    result = output.communicate()[0]
    # result = bytes(output.communicate()[0]).decode('utf-8')
    return str(result.replace('\n', ''))


def start_screen() -> int:
    if not device_info.get('enable'):
        screen_log.warn('{} 设备未启用'.format(device_info))
        return -1
    if device_info.get('screen'):
        serial = device_info.get('serial')
        state = _check_device_(serial)
        screen_log.info('设备:{} state: {}'.format(serial, state))
        'offline | bootloader | device'
        if 'device' == state:
            scrcpy_exe = StaticPath.screenpath  # "scrcpy -s --always-on-tops"  窗口最前
            cmd = ' '.join([scrcpy_exe, '-s', serial, '--always-on-top'])
            p = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, universal_newlines=True,
                                 encoding='utf-8', shell=True,)
            time.sleep(3)
            p = psutil.Process(p.pid)
            screen_pid = 0
            for i in p.children():
                if cmd == ' '.join(i.cmdline()):
                    screen_pid = i.pid
                else:
                    i.kill()
            p.kill()
            return screen_pid
        else:
            screen_log.warn('{} 设备不在线')
            return 0
    else:
        screen_log.info('{} 设备未开启投屏'.format(device_info))
