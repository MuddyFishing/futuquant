# -*- coding: utf-8 -*-
import asyncore
import socket as sock
import time
from time import sleep
from threading import Thread, RLock
from multiprocessing import Queue
import errno
import traceback
from futuquant.common.utils import *
from futuquant.quote.quote_query import parse_head
from threading import current_thread


class _AsyncThreadCtrl(object):
    def __init__(self):
        self.__list_aync = []
        self.__net_proc = None
        self.__net_proc_hold = None
        self.__stop = False
        self.__list_lock = RLock()

    def add_async(self, async_obj):
        with self.__list_lock:
            if async_obj in self.__list_aync:
                return
            self.__list_aync.append(async_obj)
            if self.__net_proc is None:
                self.__stop = False

                # work thread
                self.__net_proc = Thread(
                    target=self._thread_aysnc_net_proc, args=())
                self.__net_proc.setDaemon(True)
                self.__net_proc.start()

                # main hold thread
                self.__net_proc_hold = Thread(
                    target=self._thread_aysnc_net_proc_hold, args=())
                self.__net_proc_hold.start()

    def remove_async(self, async_obj):
        with self.__list_lock:
            if async_obj not in self.__list_aync:
                return
            self.__list_aync.remove(async_obj)
            if len(self.__list_aync) == 0:
                self.__stop = True

                self.__net_proc.join(timeout=5)
                self.__net_proc = None

                self.__net_proc_hold.join(timeout=5)
                self.__net_proc_hold = None

    def _thread_aysnc_net_proc(self):
        while not self.__stop:

            with self.__list_lock:
                for obj in self.__list_aync:
                    obj.thread_proc_async_req()
                asyncore.loop(timeout=0.01, count=1)

            if not asyncore.socket_map:
                sleep(0.01)

    def _thread_aysnc_net_proc_hold(self):
        while not self.__stop:
            sleep(0.1)


class _AsyncNetworkManager(asyncore.dispatcher_with_send):
    async_thread_ctrl = _AsyncThreadCtrl()

    def __init__(self, host, port, handler_ctx, close_handler=None):
        self.__host = host
        self.__port = port
        self.__close_handler = close_handler
        self.__req_queue = Queue()
        self.__is_log_handle_close = False
        self.__recv_buf = b''
        self._conn_id = 0
        super(_AsyncNetworkManager, self).__init__()

        self.handler_ctx = handler_ctx
        self.async_thread_ctrl.add_async(self)

    def set_conn_id(self, conn_id):
        self._conn_id = conn_id

    def __del__(self):
        self.async_thread_ctrl.remove_async(self)

    def reconnect(self):
        """reconnect"""
        self._socket_create_and_connect()

    def close_socket(self):
        """close socket"""
        self._clear_req_recv_cache()
        self.async_thread_ctrl.remove_async(self)
        self.close()

    def async_req(self, req_str):
        self.__req_queue.put(req_str)

    def thread_proc_async_req(self):
        try:
            if self.connected and self.__req_queue.empty() is False:
                req_str = self.__req_queue.get(timeout=0.001)
                self.send(req_str)
                # logger.debug("async conn_id:{}".format(self._conn_id))

        except Exception as e:
            # traceback.print_exc()
            pass

    def handle_read(self):

        try:
            # handle_read要控制一下处理时长，避免一直阻塞处理
            last_tm = time.time()
            max_tm = 0.2

            head_len = get_message_head_len()
            recv_tmp = self.recv(5 * 1024 * 1024)
            # logger.debug("async handle_read len={} head_len={}".format(len(recv_tmp), head_len))
            if recv_tmp == b'':
                return
            self.__recv_buf += recv_tmp

            while len(self.__recv_buf) > head_len:
                head_dict = parse_head(self.__recv_buf[:get_message_head_len()])
                body_len = head_dict['body_len']

                # 处理完已读数据或者处理时间片超过指定时间
                if (body_len + head_len) > len(self.__recv_buf) or (time.time() - last_tm > max_tm):
                    return

                rsp_body = self.__recv_buf[head_len: head_len + body_len]
                self.__recv_buf = self.__recv_buf[head_len + body_len:]
                # logger.debug("async proto_id = {} rsp_body_len={} body_len={}".format(head_dict['proto_id'],len(rsp_body), body_len))

                # 数据解密码校验
                ret_decrypt, msg_decrypt, rsp_body = decrypt_rsp_body(rsp_body, head_dict, self._conn_id)

                # debug 时可打开，避免异步推送影响同步请求的调试
                """
                if head_dict['proto_id'] == ProtoId.InitConnect:
                    ret_decrypt, msg_decrypt, rsp_body = decrypt_rsp_body(rsp_body, head_dict, self._conn_id)
                else:
                    ret_decrypt, msg_decrypt, rsp_body = -1, "only for debug", None
                """

                if ret_decrypt == RET_OK:
                    rsp_pb = binary2pb(rsp_body, head_dict['proto_id'], head_dict['proto_fmt_type'])
                    if rsp_pb is None:
                        logger.error("async handle_read not support proto:{} conn_id:{}".format(head_dict['proto_id'],
                                                                                                self._conn_id))
                    else:
                        self.handler_ctx.recv_func(rsp_pb, head_dict['proto_id'])
                else:
                    logger.error(msg_decrypt)

        except Exception as e:
            if isinstance(e, IOError) and e.errno in [errno.EINTR, errno.EWOULDBLOCK, errno.EAGAIN]:
                return
            self.__recv_buf = b''
            traceback.print_exc()
            err = sys.exc_info()[1] + " conn_id:{}".format(self._conn_id)
            self.handler_ctx.error_func(str(err))
            logger.debug(err)
            return

    def network_query(self, req_str):
        """query network status"""
        s_buf = str2binary(req_str)
        self.send(s_buf)

    def handle_connect(self):
        self.__is_log_handle_close = False

    def handle_close(self):
        """handle close"""
        # reduce close log info
        if not self.__is_log_handle_close:
            logger.debug("async socket err! conn_id:{}".format(self._conn_id))
            self.__is_log_handle_close = True

        if self.connected:
            self.close()
            self._clear_req_recv_cache()

        if self.__close_handler is not None:
            self.__close_handler.notify_async_socket_close(self)

    def _clear_req_recv_cache(self):
        while self.__req_queue.empty() is False:
            self.__req_queue.get(timeout=0.001)
        self.__recv_buf = b''

    def _socket_create_and_connect(self):

        if self.__host is None or self.__port is None:
            err_msg = "_AsyncNetworkManager  host or port is None"
            logger.error(err_msg)
            raise Exception(err_msg)

        if self.socket is not None:
            self.close()

        self._clear_req_recv_cache()
        self.create_socket(sock.AF_INET, sock.SOCK_STREAM)
        self.connect((self.__host, self.__port))
