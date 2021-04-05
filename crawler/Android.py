# -*- coding:utf-8  -*-
# @Time     : 2021-03-05 22:54
# @Author   : BGLB
# @Software : PyCharm
import time
import traceback
from abc import abstractmethod

from uiautomator2 import ConnectError

from crawler._base import _CrawlerBase
from config import node_config
import uiautomator2 as u2

from scheduler.status_code import CrawlerStatus


class CrawlerAndroid(_CrawlerBase):
    """
    安卓爬虫
    """
    def __init__(self, crawler_config: dict):
        self.app_info = {}
        super().__init__(crawler_config)
        # self.app_info = {
        #     'PackageName': '',
        #     'Activity': '',
        #     'IsReset': True,
        #     'IsWait': True,
        # }

        self.__package_name = ''
        self.__device_info = node_config['android'].get('devices')
        self.device: u2.Device
        # self._start_app()

    def _connect_device(self):
        try:
            self.app_device = u2.connect_usb(self.__device_info.get('serial'))
            self.app_device.healthcheck()
            self.log.info('手机连接成功 设备信息如下\n{}'.format(self.app_device.device_info))
            self.app_device.unlock()
            if self.app_device(resourceId='com.android.systemui:id/passwordEntry').exists(5):
                for i in self.__device_info.get('password'):
                    self.app_device.shell(['input', 'keyevent', '{}'.format(int(i)+7)])
                    self.app_device.sleep(.2)
                self.log.info('{}手机解锁成功'.format(self.__device_info))
        except ConnectError and RuntimeError as e:
            self.log.error('手机连接失败 原因如下\n{}'.format(traceback.format_exc()))
            return False
        return True

    def _start_app(self) -> bool:
        self.__package_name = self.app_info.get('PackageName')
        if not self.__package_name:
            self.log.error('app 【{}】启动失败, 请检查PackageName'.format(self.app_info))
            # raise Exception('启动应用 PackageName 不能为空')
            return False
        if self.app_info['IsReset']:
            self.log.info('app 【{}】数据清理中'.format(self.__package_name))
            self.app_device.app_clear(self.__package_name)
        self.app_device.app_start(self.__package_name, self.app_info.get('Activity'), stop=True)
        if self.app_info.get('IsWait'):
            self.log.info('app 【{}】等待应用启动中'.format(self.__package_name))
            pid = self.app_device.app_wait(self.__package_name, front=True, timeout=5)
            if pid == 0:
                self.log.warn('am start app 【{}】启动超时'.format(self.__package_name))
                return self.__click_app_()
        self.log.info('当前app信息-{}'.format(self.app_device.app_current()))

        return True

    def __click_app_(self) -> bool:
        self.log.info('返回主界面 尝试点击启动app')
        if not self.app_info.get('AppName', ''):
            self.log.warn('AppName 必须存在, 则不能通过点击启动')
            return False
        self.app_device.press('HOME')
        time.sleep(1)
        self.app_device.press('HOME')
        time.sleep(1)
        current_app_name = self.app_device(resourceId="com.meizu.flyme.launcher:id/app_name").get_text()
        previous_app_name = ''
        is_start = False
        while current_app_name != previous_app_name:
            if self.app_device(text=self.app_info.get('AppName')).exists(2):
                self.app_device(text=self.app_info.get('AppName')).click(0)
                self.app_device.sleep(1)
                is_start = True
                if self.__package_name in self.app_device.app_current().get('package'):
                    _activity = self.app_info.get('Activity', '')
                    current_activity = self.app_device.app_current().get('activity')
                    if not _activity:
                        self.log.warn("Don't check Activity")
                    if not (_activity == current_activity or _activity in current_activity or current_activity in
                            _activity):
                        self.log.warn('please check activity of app_info \ncurrent_activity:{}'.format(
                            current_activity))
                else:
                    self.log.warn('current_packagename:{}'.format(self.app_device.app_current().get('package')))
                if is_start:
                    self.log.info('app 【{}】 click 启动应用成功'.format(self.__package_name))
                    return is_start
            previous_app_name = current_app_name
            self.app_device.swipe_ext("left")
            # self.app_device.sleep(2)
            current_app_name = self.app_device(resourceId="com.meizu.flyme.launcher:id/app_name").get_text()
        self.log.error('app 【{}】 click 启动应用失败, 请检查是否安装'.format(self.app_info))
        return is_start

    def restart_app(self, clear=False, stop=True, wait=True):
        """
        重新启动app
        :param clear: 启动前是否清理app数据
        :param stop: 启动前是否关闭
        :param wait: 是否等待app启动
        :return: None
        """
        if not self.__package_name:
            raise Exception('启动应用 PackageName 不能为空')
        if clear:
            self.app_device.app_clear(self.__package_name)
            self.log.info('清理app 【{}】'.format(self.__package_name))
        self.app_device.app_start(package_name=self.__package_name, stop=stop)
        if wait:
            self.log.info('等待应用启动中')
            pid = self.app_device.app_wait(self.__package_name)
            if pid and pid != 0:
                self.log.info('{}'.format(str(self.app_device.app_current)))
                self.log.info('app 【{}】重启成功！'.format(self.__package_name))
                return True
            else:
                self.log.error('am start app 【{}】重启超时'.format(self.__package_name))
                return self.__click_app_()

    @abstractmethod
    def spider(self):
        super().spider()

    @abstractmethod
    def saver(self):
        pass

    def run(self):
        if not self._connect_device():
            self._state = CrawlerStatus.CrawlerException
            return
        if not self._start_app():
            self._state = CrawlerStatus.CrawlerException
            return
        super().run()

    def __del__(self):

        pass
