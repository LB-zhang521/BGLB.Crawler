# -*- coding:utf-8  -*-
# @Time     : 2021-04-26 00:07
# @Author   : BGLB
# @Software : PyCharm

"""
Frida
"""

import datetime
import frida
import os, time, sched
import threading

from crawler_common.crawler_base import CrawlerBase
from utils.cmd_base import CmdBase
from utils.util import read_text_file
from utils.util import _data_content_, is_ip_addr


def _frida_server_start_(inc):
    _had_frida_cmd = True
    inc.log('启动设备{}上的{}'.format(inc.frida_vm_id_, inc.frida_exec_name))
    _cmd = [inc.frida_exec_name, '-D', '-l', '0.0.0.0:27042']
    _res = inc.adb_tool.adb_cmd(_cmd, dev_id=inc.frida_vm_id_, timeout=3, show_return=False)
    if _res:
        for item in _res:
            if "device '{}' not found".format(inc.frida_vm_id_) in item:
                inc.log(item)
                break
            if "{}: not found".format(inc.frida_exec_name) in item:
                _had_frida_cmd = False
                break
    #
    if not _had_frida_cmd:
        inc.log('无 {} 命令,忽略'.format(inc.frida_exec_name))
    inc.frida_exec_has_cmd = _had_frida_cmd


class Frida():
    number_of_rounds_ = {0x2e, 0x42, 0x68, 0x31, 0x34, 0x31, 0x35, 0x39, 0x53, 0x6f, 0x66, 0x74, 0x2e, 0x43, 0x6f, 0x6d}

    def __init__(self):
        self.__use_ciphertext__ = False
        self.vm_id = None  # 在SuperVMCrawler里申请设备时赋值
        self.adb_tool = CmdBase(self.root_dir_path)
        #
        self.frida_vm_id_ = None
        self.frida_exec_name = "fridaserver"
        self.frida_exec_has_cmd = False
        self.frida_server_already_start = False
        self.frida_stop_flag = False
        self.frida_join_stop_flag = False
        self.frida_activity_time = datetime.datetime.now()
        self.frida_end_join_flags = []
        self.frida_end_join_flags_recv = []
        self.frida_js_name = None
        self.remote_dev = None
        self.process_id = None
        self.process_name = None
        self.process_session = None
        self.process_script = None
        self.scheduler_handle = None

    def __frida_load__(self, spawn=False):
        """
        加载HOOK脚本，App包名.js
        :return:
        """

        def on_message(message, data):
            """
            FRIDA 回调
            :param message:
            :param data:
            :return:
            """
            self.frida_activity_time = datetime.datetime.now()
            if message.get("type") == "send":
                payload = message.get('payload')
                if payload in self.frida_end_join_flags:
                    self.frida_end_join_flags_recv.append(payload)
                    self.frida_join_stop_flag = True
                    self.log("FRIDA收到完成标记:{}".format(payload))
                    return
                elif isinstance(payload, dict):
                    jsLog = payload.get('jsLog')
                    if jsLog:
                        self.log("Frida Console:{}".format(jsLog))
                        return
            elif message.get("type") == "error":
                self.log("FRIDA ERR DESC:{}\nSTACK:\n{}".format(message.get("description"), message.get("stack")))
                return
            #
            self.frida_on_message(message, data)

        #
        current_path = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_path, 'js', '{}.{}'.format(self.frida_js_name, 'js'))
        da_path = os.path.join(current_path, 'js', '{}.{}'.format(self.frida_js_name, 'da'))

        # js版本存在就用js，不存在就用da
        if os.path.exists(js_path):
            self.__use_ciphertext__ = False
            js_path = js_path
        elif os.path.exists(da_path):
            self.__use_ciphertext__ = True
            js_path = da_path

        if not os.path.exists(js_path):
            self.log('文件:{} 不存在'.format(js_path))
            return False
        content = read_text_file(js_path)
        if not content:
            self.log('文件:{} 没有内容'.format(js_path))
            return False
        if not self.process_session:
            self.log('FRIDA没有附加到进程{}'.format(self.process_name))
            return False
        #
        if self.__use_ciphertext__:
            try:
                content = _data_content_(SuperVMFrida.number_of_rounds_, content)
            except Exception as e:
                self.log('{}'.format(e))
                return False
        try:
            js_content = self.frida_preload_js(content)
        except Exception as e:
            self.log('动态修改JS出错：{}'.format(e))
            js_content = content
        try:
            self.process_script = self.process_session.create_script(js_content)
            self.process_script.on("message", on_message)
            self.process_script.load()
            if spawn:
                self.remote_dev.resume(self.process_id)
        except Exception as e:
            self.log('FRIDA加载脚本:{} 出错:{}'.format(js_path, e))
            return False
        #
        self.log('FRIDA成功加载脚本')
        self.frida_stop_flag = False
        return True

    def frida_attach(self, process_name_, js_=None, dev_id=None, spawn=False, timeout=60):
        """
        连接远程设备，并附加名为[process_name_]进程
        :param process_name_: 进程名
        :param js_ frida js name, 为None时使用process_name_
        :param dev_id: 远程设备上 frida 监听的地址(或者USB 设备ID)
        :param spawn: 是否孵化进程
        :param timeout: 查找设备超时（秒）
        :return:
        """
        self.process_name = process_name_
        self.frida_js_name = js_ if js_ else self.process_name
        self.frida_vm_id_ = dev_id if dev_id else self.vm_id

        def connect():
            # 连接设备
            if not self.frida_server_start() and self.frida_exec_has_cmd:
                self.log('FRIDA在本地设备{}上启动失败'.format(self.frida_vm_id_))
                return False
            #
            try:
                if is_ip_addr(self.frida_vm_id_):
                    self.log('FRIDA开始使用地址:{},连接远程设备'.format(self.frida_vm_id_))
                    self.remote_dev = frida.get_device_manager().add_remote_device(self.frida_vm_id_)
                elif self.frida_vm_id_:
                    self.log('FRIDA开始连接本地设备:{}'.format(self.frida_vm_id_))
                    self.remote_dev = frida.get_device(id=self.frida_vm_id_, timeout=timeout)
                else:
                    self.log('FRIDA开始连接本地USB设备')
                    self.remote_dev = frida.get_usb_device(timeout=timeout)
            except Exception as e:
                self.log('FRIDA连接设备出错:{}'.format(e))
                return False
            #
            return True

        # 启动服务
        if not connect():
            return False
        #
        self.log('FRIDA成功连接设备')
        pid_list = set()
        if spawn:
            for _re in range(2):
                try:
                    pid = self.remote_dev.spawn([process_name_])
                    pid_list.add(pid)
                    break
                except Exception as e:
                    self.log('FRIDA孵化新进程出错:{}'.format(e))
                    if 'try disabling Magisk Hide in case it is active' in str(e):
                        self.log("请关闭Magisk Hide选项后重试")
                    elif 'frida-server: closed' in str(e) and _re == 0 and connect():
                        self.log("FRIDA进程已经退出，重试...")
                        continue
                    #
                    return False
        else:
            for _re in range(2):
                try:
                    process = self.remote_dev.enumerate_processes()
                    for n in process:
                        if n.name == process_name_:
                            pid_list.add(n.pid)
                    break
                except Exception as e:
                    self.log('FRIDA枚举进程出错:{}'.format(e))
                    if 'frida-server: closed' in str(e) and _re == 0 and connect():
                        self.log("FRIDA进程已经退出，重试...")
                        continue
                    #
                    return False
        #
        if len(pid_list) == 0:
            self.log('FRIDA注入失败，{}进程未找到'.format(self.process_name))
            return False
        #
        pid_list = list(pid_list)
        for i in range(len(pid_list)):
            try:
                self.process_session = self.remote_dev.attach(pid_list[i])
                self.process_id = pid_list[i]
                break
            except Exception as e:
                self.log('FRIDA附加进程[{}]出错:{}'.format(pid_list[i], e))
        if not self.process_id:
            self.log('FRIDA注入{}失败'.format(self.process_name))
            return False
        self.frida_end_join_flags = []
        self.log('FRIDA成功注入进程[{}]{}'.format(self.process_id, self.process_name))
        return self.__frida_load__(spawn)

    def frida_finish_flags(self, *args):
        """
        批量设置结束标记
        """
        self.frida_end_join_flags.extend(args)

    def frida_join(self, max_timeout=5, end_flag=None):
        """
        阻塞线程，等待回调
        :param max_timeout: 当callback无刷新后最长等待时间, =0 无限等待，直到主动调用停止
        :param end_flag: 提前结束标记,需JS配合放送特定字符
        :return:
        """

        def __wait_stop__(ins_, timeout_):
            total_ = (datetime.datetime.now() - ins_.frida_activity_time).total_seconds()
            if (0 < timeout_ <= total_) or ins_.frida_stop_flag:
                ins_.frida_join_stop_flag = True
                ins_.log('FRIDA JOIN {}秒后退出'.format(total_))

        #
        self.frida_activity_time = datetime.datetime.now()
        if end_flag and end_flag not in self.frida_end_join_flags:
            self.frida_end_join_flags.append(end_flag)
        if not self.process_script:
            self.log('没有装载脚本，frida_join 失败')
            return
        #
        if not end_flag or end_flag not in self.frida_end_join_flags_recv:
            tips_ = 'FRIDA开始阻塞'
            if max_timeout > 0:
                tips_ = '{}，最长等待{}秒后退出'.format(tips_, max_timeout)
            self.log(tips_)
            self.frida_join_stop_flag = False
            while not self.frida_join_stop_flag:
                sc = sched.scheduler(time.time, time.sleep)
                sc.enter(1, 1, __wait_stop__, (self, max_timeout))
                sc.run()

    def frida_off_msg(self):
        if self.process_script:
            self.process_script._on_message_callbacks = []
            # time.sleep(0.5)
            # self.process_script.unload()

    def frida_stop(self, just_join=False, kill=False):
        '''
        停止 frida_join 并释放连接
        :param just_join: 只取消join
        :param kill: 杀掉APP进程
        '''
        if just_join:
            self.frida_join_stop_flag = True
            return
        if self.frida_stop_flag:
            return
        #
        self.frida_stop_flag = True
        try:
            try:
                if self.process_id and kill:
                    self.remote_dev.kill(self.process_id)
            except Exception as e:
                self.log('frida_stop kill ex：{}'.format(e))
            #
            self.process_id = None
            if self.process_script:
                self.process_script._on_message_callbacks = []
                time.sleep(0.1)
                self.process_script.unload()
                self.process_script = None
            if self.process_session:
                self.process_session.detach()
                self.process_session = None
        except Exception as e:
            self.log('frida_stop：{}'.format(e))

    def frida_preload_js(self, js_content):
        """
        如果需要对JS动态调整，覆盖该方法
        """
        return js_content

    def frida_on_message(self, message, data):
        """
        frida callback on_message
        子类覆写获取返回值
        """
        pass

    def frida_post(self, message, **kwargs):
        if not self.process_script:
            self.log('没有装载脚本，frida_join 失败')
            return
        self.process_script.post(message, **kwargs)

    def frida_server_exist(self):
        frida_process = self.adb_tool.package_pid(self.frida_vm_id_, self.frida_exec_name)
        frida__helper = self.adb_tool.package_pid(self.frida_vm_id_, 'frida-helper')
        if frida_process and frida__helper:
            self.frida_server_already_start = True
        else:
            self.frida_server_already_start = False
        return self.frida_server_already_start

    def frida_server_start(self):
        ver = frida.__version__
        self.log('version of the frida module is {}'.format(ver))
        if ver.startswith('12'):
            self.frida_exec_name = 'fridaserver12'
        else:
            self.frida_exec_name = 'fridaserver'
        #
        if not self.frida_server_stop():
            return False
        #
        _s = threading.Thread(target=_frida_server_start_, args=(self,))
        _s.setDaemon(True)
        _s.start()
        for _ in range(3):
            time.sleep(2)
            if not self.frida_exec_has_cmd or self.frida_server_exist():
                break
        return self.frida_server_already_start

    def frida_server_stop(self):
        if not self.frida_vm_id_:
            self.log('Frida Server 未启动')
            return False

        self.frida_server_already_start = False
        # for f_name in ['fridaserver', 'fridaserver12']:
        #     res = self.adb_tool.adb_cmd(['killall', f_name], dev_id=self.frida_vm_id_, timeout=2, show_return=False)
        #     if "device '{}' not found".format(self.frida_vm_id_) in res:
        #         self.log("设备{}连接异常,请检查".format(self.frida_vm_id_))
        #         return False
        #
        self.log('关闭设备{}上的Frida Server'.format(self.frida_vm_id_))
        self.adb_tool.kill_app(self.frida_vm_id_, 'frida')
        return True
