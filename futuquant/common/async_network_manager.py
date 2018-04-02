# -*- coding: utf-8 -*-
import asyncore
import socket as sock
import time
from threading import Thread
import traceback
from futuquant.common.utils import *

class _AsyncThreadCtrl(object):
    def __init__(self):
        self.__list_aync = []
        self.__net_proc = None
        self.__stop = False

    def add_async(self, async_obj):
        if async_obj in self.__list_aync:
            return
        self.__list_aync.append(async_obj)
        if self.__net_proc is None:
            self.__stop = False
            self.__net_proc = Thread(
                target=self._thread_aysnc_net_proc, args=())
            self.__net_proc.start()

    def remove_async(self, async_obj):
        if async_obj not in self.__list_aync:
            return
        self.__list_aync.remove(async_obj)
        if len(self.__list_aync) == 0:
            self.__stop = True
            self.__net_proc.join(timeout=5)
            self.__net_proc = None

    def _thread_aysnc_net_proc(self):
        while not self.__stop:
            asyncore.loop(timeout=0.001, count=5)


class _AsyncNetworkManager(asyncore.dispatcher_with_send):
    async_thread_ctrl = _AsyncThreadCtrl()

    def __init__(self, host, port, handler_ctx, close_handler=None):
        self.__host = host
        self.__port = port
        self.__close_handler = close_handler

        asyncore.dispatcher_with_send.__init__(self)
        self._socket_create_and_connect()

        time.sleep(0.1)
        self.rsp_buf = b''
        self.handler_ctx = handler_ctx

        self.async_thread_ctrl.add_async(self)

    def __del__(self):
        self.async_thread_ctrl.remove_async(self)

    def reconnect(self):
        """reconnect"""
        self._socket_create_and_connect()

    def close_socket(self):
        """close socket"""
        self.async_thread_ctrl.remove_async(self)
        self.close()

    def handle_read(self):
        """
                    deal with Json package
                    :return: err
                    """
        delimiter = b'\r\n\r\n'
        rsp_str = u''
        try:
            recv_buf = self.recv(5 * 1024 * 1024)
            if recv_buf == b'':
                raise Exception("_AsyncNetworkManager : remote server close")
            self.rsp_buf += recv_buf
            loc = self.rsp_buf.find(delimiter)
            while loc >= 0:
                rsp_binary = self.rsp_buf[0:loc]
                loc += len(delimiter)
                self.rsp_buf = self.rsp_buf[loc:]

                rsp_str = binary2str(rsp_binary)

                self.handler_ctx.recv_func(rsp_str)
                loc = self.rsp_buf.find(delimiter)
        except Exception as e:
            if isinstance(e, IOError) and e.errno == 10035:
                return
            traceback.print_exc()
            err = sys.exc_info()[1]
            self.handler_ctx.error_func(str(err))
            print(rsp_str)
            return

    def network_query(self, req_str):
        """query network status"""
        s_buf = str2binary(req_str)
        self.send(s_buf)

    def __del__(self):
        self.close()

    def handle_close(self):
        """handle close"""
        if self.__close_handler is not None:
            self.__close_handler.notify_async_socket_close(self)

    def _socket_create_and_connect(self):
        if self.socket is not None:
            self.close()
        if self.__host is not None and self.__port is not None:
            self.create_socket(sock.AF_INET, sock.SOCK_STREAM)
            self.connect((self.__host, self.__port))
