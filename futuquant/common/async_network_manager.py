# -*- coding: utf-8 -*-
import asyncore
import socket as sock
import time
from threading import Thread, RLock
from multiprocessing import Queue
import traceback
from futuquant.common.utils import *
from futuquant.quote.quote_query import parse_head
from threading import current_thread


class _AsyncThreadCtrl(object):
    def __init__(self):
        self.__list_aync = []
        self.__net_proc = None
        self.__stop = False
        self.__list_lock = RLock()

    def add_async(self, async_obj):
        with self.__list_lock:
            if async_obj in self.__list_aync:
                return
            self.__list_aync.append(async_obj)
            if self.__net_proc is None:
                self.__stop = False
                self.__net_proc = Thread(
                    target=self._thread_aysnc_net_proc, args=())
                self.__net_proc.start()

    def remove_async(self, async_obj):
        with self.__list_lock:
            if async_obj not in self.__list_aync:
                return
            self.__list_aync.remove(async_obj)
            if len(self.__list_aync) == 0:
                self.__stop = True
                self.__net_proc.join(timeout=5)
                self.__net_proc = None

    def _thread_aysnc_net_proc(self):
        while not self.__stop:
            with self.__list_lock:
                for obj in self.__list_aync:
                    obj.thread_proc_async_req()
                asyncore.loop(timeout=0.001, count=5)


class _AsyncNetworkManager(asyncore.dispatcher_with_send):
    async_thread_ctrl = _AsyncThreadCtrl()

    def __init__(self, host, port, handler_ctx, close_handler=None):
        self.__host = host
        self.__port = port
        self.__close_handler = close_handler
        self.__req_queue = Queue()

        asyncore.dispatcher_with_send.__init__(self)
        self._socket_create_and_connect()

        time.sleep(0.1)
        self.__recv_buf = b''
        self.handler_ctx = handler_ctx
        self.async_thread_ctrl.add_async(self)

    def __del__(self):
        self.async_thread_ctrl.remove_async(self)

    def reconnect(self):
        """reconnect"""
        self._socket_create_and_connect()

    def close_socket(self):
        """close socket"""
        self.__recv_buf = b''
        self.async_thread_ctrl.remove_async(self)
        self.close()

    def async_req(self, req_str):
        self.__req_queue.put(req_str)

    def thread_proc_async_req(self):
        if self.__req_queue.empty() is False:
            req_str = self.__req_queue.get(timeout=0.001)
            if self.connected:
                self.send(req_str)

    def handle_read(self):
        """
                    deal with package
                    :return:
                    """
        try:
            head_len = get_message_head_len()
            recv_tmp = self.recv(5 * 1024 * 1024)
            # logger.debug("async handle_read len={} head_len={}".format(len(recv_tmp), head_len))
            if recv_tmp == b'':
                return
            self.__recv_buf += recv_tmp

            while len(self.__recv_buf) > head_len:
                head_dict = parse_head(self.__recv_buf[:get_message_head_len()])
                body_len = head_dict['body_len']

                while (body_len + head_len) > len(self.__recv_buf):
                    recv_tmp = self.recv(5 * 1024 * 1024)
                    if recv_tmp == b'':
                        return
                    self.__recv_buf += recv_tmp

                rsp_body = self.__recv_buf[head_len: head_len + body_len]
                self.__recv_buf = self.__recv_buf[head_len + body_len:]
                logger.debug("async proto_id = {} rsp_body_len={} body_len={}".format(head_dict['proto_id'],
                                                                                      len(rsp_body), body_len))
                rsp_pb = binary2pb(rsp_body, head_dict['proto_id'], head_dict['proto_fmt_type'])
                if rsp_pb is None:
                    logger.error("async handle_read not support proto:{}".format(head_dict['proto_id']))
                else:
                    self.handler_ctx.recv_func(rsp_pb, head_dict['proto_id'])

            if len(self.__recv_buf):
                logger.debug("left len = {} data={}".format(len(self.__recv_buf), self.__recv_buf))

        except Exception as e:
            if isinstance(e, IOError) and e.errno == 10035:
                return
            self.__recv_buf = b''
            traceback.print_exc()
            err = sys.exc_info()[1]
            self.handler_ctx.error_func(str(err))
            logger.debug(rsp_pb)
            return

    def network_query(self, req_str):
        """query network status"""
        s_buf = str2binary(req_str)
        self.send(s_buf)

    def __del__(self):
        self.close()

    def handle_close(self):
        """handle close"""
        logger.debug("async socket err!")
        while self.__req_queue.empty() is False:
            self.__req_queue.get(timeout=0.001)

        if self.__close_handler is not None:
            self.__close_handler.notify_async_socket_close(self)

    def _socket_create_and_connect(self):
        if self.socket is not None:
            self.close()
        if self.__host is not None and self.__port is not None:
            self.create_socket(sock.AF_INET, sock.SOCK_STREAM)
            self.connect((self.__host, self.__port))
