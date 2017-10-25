# -*- coding: utf-8 -*-

"""
 定时监控futnn api进程，如果进程crash, 自动重启，
  1. 该脚本仅支持windows (目前api也只有windows版本）
  2. 构造 FTApiDaemon 需指定ftnn.exe所在的目录 ,一般是'C:\Program Files (x86)\FTNN\\'
  3. 对象实现的本地监控， 只能运行在ftnn api 进程所在的机器上
"""

import psutil
import time
import socket
import sys
import configparser
from threading import Thread
import os

class FTApiDaemon:
    '''
    only run for windows,  to restart ftunn.exe when crashed
    '''

    def __init__(self, ftnn_root_path='C:\Program Files (x86)\FTNN\\'):
        self._root_path = ftnn_root_path
        self._exe_path = self._root_path + 'FTNN.exe'
        self._crash_report_path = self._root_path + 'FTBugReport.exe'
        self._plugin_path = self._root_path + 'plugin\config.ini'
        self._api_port = None
        self._started = False
        self._thread_daemon = None
        self._close = False
        self._time_restart = 300 #5分钟一次
        self._daemon_type = {
            "TIMER_WATCH": self._fun_thread_daemon_watch,
            "TIMER_RESTART": self._fun_thread_daemon_restart,
        }

        if not os.path.isfile(self._exe_path) or not os.path.isfile(self._crash_report_path):
            print("FTApiDaemon erro file not exist !")
        else:
            '读取ini中api的配置信息'
            try:
                config = configparser.ConfigParser()
                config.read_file(open(self._plugin_path))
                self._api_port = int(config.get("pluginserver", "port"))
                print('FTApiDaemon find api_port={}'.format(self._api_port))
                del config
            except Exception as e:
                print('FTApiDaemon config read error!')

    @property
    def restart_time(self):
        return self._time_restart

    @restart_time.setter
    def restart_time(self, val):
        val = int(val)
        if val < 1:
            val = 1
        self._time_restart = val

    ''' 启动线程监控ftnn api 进程'''
    def start(self, daemon_type='TIMER_WATCH'):
        if self._started:
            return

        if self._api_port is None:
            print("FTApiDaemon start fail!")
            return

        if daemon_type not in self._daemon_type:
            print("Daemon type param err!")
            return

        self._started = True
        self._close = False
        self._thread_daemon = Thread(target=self._daemon_type[daemon_type])
        self._thread_daemon.setDaemon(False)
        self._thread_daemon.start()

    '''中止监控'''
    def close(self):
        if not self._started:
            return

        self._started = False

        if self._thread_daemon is not None:
            self._close = True
            self._thread_daemon.join(tiimeout=10)
            self._thread_daemon = None

    def _loop_kill_futunn(self, loop_timer=1):
        '''loop to close exist ftnn.exe && ftbugreport.exe process'''
        while True:
            process_bugreport = self._get_process_by_path(self._crash_report_path)
            process_ftnn = self._get_process_by_path(self._exe_path)
            if process_bugreport is None and process_ftnn is None:
                break

            if process_bugreport is not None:
                process_bugreport.kill()

            if process_ftnn is not None:
                process_ftnn.kill()

            time.sleep(loop_timer)

    def _fun_thread_daemon_restart(self):
        if self._close:
            return

        while True:
            if self._is_api_socket_ok() is False:
                process_new = psutil.Popen([self._exe_path, "type=python_auto"])
                if process_new is not None:
                    print("FTApiDaemon new futnn process open ! pid={}".format(process_new.pid))
                else:
                    print("FTApiDaemon open process fail ! ")

            time.sleep(self._time_restart)
            self._loop_kill_futunn()

    def _fun_thread_daemon_watch(self):
        time_sleep = 5

        if self._close:
            return

        while True:

            '''check api work'''
            is_api_ok = self._is_api_socket_ok()
            if is_api_ok is True:
                time.sleep(time_sleep)
                continue

            self._loop_kill_futunn()

            '''start new ftnn.exe process'''
            process_new = psutil.Popen([self._exe_path, "type=python_auto"])
            if process_new is not None:
                print("FTApiDaemon new futnn process open ! pid={}".format(process_new.pid))
            else:
                print("FTApiDaemon open process fail ! ")

            time.sleep(time_sleep)

    def _is_api_socket_ok(self):
        api_ip = '127.0.0.1'
        s = socket.socket()
        s.settimeout(10)
        try:
            s.connect((api_ip, self._api_port))
            s.close()
            del s
        except Exception as e:
            err = sys.exc_info()[1]
            err_msg = str(err)
            # print("socket connect err:{}".format(err_msg))
            return False
        return True

    def _get_process_by_pid(self, pid):
        """通过processid 获取进程"""
        try:
            p = psutil.Process(pid)
        except Exception as e:
            return None
        return p

    def _get_process_by_path(self, path):
        """通过路径获取进程"""
        lower_path = str(path).lower()
        for pid in psutil.pids():
            try:
                process = psutil.Process(pid)
                tmp = process.exe()
                if str(tmp).lower() == lower_path:
                    return process
            except:
                continue
        return None


if __name__ == '__main__':
    root_path = 'C:\Program Files (x86)\FTNN\\'
    # root_path = 'C:\Program Files (x86)\FTNN_api\\'

    daemon = FTApiDaemon(root_path)

    # 每5分钟重启一次futunn
    daemon.restart_time = 5 * 60
    daemon.start(daemon_type='TIMER_RESTART')

    # 监控程序，发现有异常退出就重启
    # daemon.start(daemon_type='TIMER_WATCH')

