# -*- coding: utf-8 -*-

import time
from abc import ABCMeta, abstractmethod
from time import sleep
from threading import RLock, Thread
from futuquant.common.async_network_manager import _AsyncNetworkManager
from futuquant.common.sync_network_manager import _SyncNetworkQueryCtx
from futuquant.common.utils import *
from futuquant.quote.response_handler import HandlerContext
from futuquant.quote.quote_query import InitConnect
from futuquant.quote.response_handler import AsyncHandler_InitConnect
from futuquant.quote.quote_query import GlobalStateQuery
from futuquant.common.conn_mng import FutuConnMng
import threading


class OpenContextBase(object):
    """Base class for set context"""
    metaclass__ = ABCMeta

    def __init__(self, host, port, async_enable):
        self.__host = host
        self.__port = port
        self.__async_socket_enable = async_enable
        self._async_ctx = None
        self._sync_net_ctx = None
        self._thread_check_sync_sock = None
        self._thread_is_exit = False
        self._check_last_req_time = None
        self._is_socket_reconnecting = False
        self._is_obj_closed = False

        self._handlers_ctx = None
        self._proc_run = False

        self._sync_query_lock = RLock()
        self._count_reconnect = 0

        # init connect info
        self._sync_connect_info = {}
        self._sync_conn_id = 0
        self._async_conn_id = 0
        self._event_async_close = threading.Event()

        self._socket_reconnect_and_wait_ready()

    def _sync_init_connect(self):
        """
        :param client_ver:
        :param client_id:
        :return:(ret, msg)
        """
        query_processor = self._get_sync_query_processor(
            InitConnect.pack_req, InitConnect.unpack_rsp)
        kargs = {
            'client_ver': int(SysConfig.get_client_ver()),
            'client_id': str(SysConfig.get_client_id()),
            'recv_notify': False,
        }
        ret_code, msg, content = query_processor(**kargs)

        if ret_code != RET_OK:
            logger.info("init connect fail: {}".format(msg))
            return RET_ERROR, msg
        else:
            conn_info = copy(content)
            self._sync_conn_id = conn_info['conn_id']
            self._sync_net_ctx.set_conn_id(self._sync_conn_id)
            FutuConnMng.add_conn(conn_info)
            logger.info("sync socket init_connect ok: {}".format(conn_info))

        return RET_OK, ""

    def on_async_init_connect(self, ret, msg, conn_info_map):
        """
        异步socket收到initconnect的回包
        :param ret:
        :param msg:
        :param conn_info_map:
        :return:
        """
        if ret == RET_OK:
            self._async_conn_id = conn_info_map['conn_id']
            self._async_ctx.set_conn_id(self._async_conn_id)
            FutuConnMng.add_conn(conn_info_map)
        logger.debug("async init connect ret={}, msg={}, conn_info={}".format(ret, msg, conn_info_map))

    def get_sync_conn_id(self):
        """
        get sync soocket connect id
        :return: id(int)
        """
        return self._sync_conn_id

    def get_async_conn_id(self):
        """
        get async soocket connect id
        :return: id(int)
        """
        return self._async_conn_id

    def get_login_user_id(self):
        """
        get login user id
        :return: user id(int64)
        """
        return FutuConnMng.get_conn_user_id(self._sync_conn_id)

    def __del__(self):
        self._close()

    @abstractmethod
    def close(self):
        """
        to call close old obj before loop create new, otherwise socket will encounter error 10053 or more!
        """
        self._close()

    @abstractmethod
    def on_api_socket_reconnected(self):
        """
        callback after reconnect ok
        """
        # logger.debug("on_api_socket_reconnected obj ID={}".format(id(self)))
        pass

    def _close(self):

        self._is_obj_closed = True
        self.stop()

        if self._thread_check_sync_sock is not None:
            self._thread_check_sync_sock.join(timeout=10)
            self._thread_check_sync_sock = None
            assert self._thread_is_exit

        if self._sync_net_ctx is not None:
            self._sync_net_ctx.close_socket()
            self._sync_net_ctx = None

        if self._async_ctx is not None:
            self._async_ctx.close_socket()
            self._async_ctx = None

        if self._sync_query_lock is not None:
            self._sync_query_lock = None

        self._handlers_ctx = None

    def start(self):
        """
        start the receiving thread,asynchronously receive the data pushed by the client
        """
        self._proc_run = True

    def stop(self):
        """
        stop the receiving thread, no longer receive the data pushed by the client
        """
        self._proc_run = False

    def set_handler(self, handler):
        """
        set async push hander obj
        :param handler: RspHandlerBase deviced obj
        :return: ret_error or ret_ok
        """
        if self._handlers_ctx is not None:
            return self._handlers_ctx.set_handler(handler)
        return RET_ERROR

    def set_pre_handler(self, handler):
        '''set pre handler'''
        if self._handlers_ctx is not None:
            return self._handlers_ctx.set_pre_handler(handler)
        return RET_ERROR

    def _is_proc_run(self):
        return self._proc_run

    def _send_sync_req(self, req_str):
        """
        send a synchronous request
        """
        if self._sync_net_ctx:
            ret, msg, content = self._sync_net_ctx.network_query(req_str)
            if ret != RET_OK:
                return RET_ERROR, msg, None
            return RET_OK, msg, content
        return RET_ERROR, "sync_ctx is None!", None

    def _send_async_req(self, req_str):
        """
        send a asynchronous request
        """
        if self._async_ctx:
            self._async_ctx.async_req(req_str)
            return RET_OK, ''
        return RET_ERROR, 'async_ctx is None!'

    def _get_sync_query_processor(self, pack_func, unpack_func):
        """
        synchronize the query processor
        :param pack_func: back
        :param unpack_func: unpack
        :return: sync_query_processor
        """
        send_req = self._send_sync_req

        def sync_query_processor(**kargs):
            """sync query processor"""
            msg_obj_del = "the object may have been deleted!"
            if self._is_obj_closed or self._sync_query_lock is None:
                return RET_ERROR, msg_obj_del, None
            try:
                self._sync_query_lock.acquire()
                if self._is_obj_closed:
                    return RET_ERROR, msg_obj_del, None

                ret_code, msg, req_str = pack_func(**kargs)

                if ret_code == RET_ERROR:
                    return ret_code, msg, None

                ret_code, msg, rsp_str = send_req(req_str)
                if ret_code == RET_ERROR:
                    return ret_code, msg, None

                ret_code, msg, content = unpack_func(rsp_str)
                if ret_code == RET_ERROR:
                    return ret_code, msg, None
                return RET_OK, msg, content
            finally:
                try:
                    if self._sync_query_lock:
                        self._sync_query_lock.release()
                except Exception as e:
                    traceback.print_exc()
                    err = sys.exc_info()[1]
                    logger.debug(err)

        return sync_query_processor

    def on_create_sync_session(self):

        logger.debug("...")
        ret = RET_OK
        msg = ""

        if not self._sync_net_ctx.is_sock_ok(0.01):
            ret, msg = self._socket_reconnect_and_wait_ready()

        return ret, msg

    def _clear_conn_id(self):
        if self._sync_conn_id:
            FutuConnMng.remove_conn(self._sync_conn_id)
            self._sync_conn_id = 0

        if self._async_conn_id:
            FutuConnMng.remove_conn(self._async_conn_id)
            self._async_conn_id = 0

    def _socket_reconnect_and_wait_ready(self):
        """
        sync_socket & async_socket recreate
        :return: (ret, msg)
        """
        if self._is_socket_reconnecting or self._is_obj_closed or self._sync_query_lock is None:
            return RET_ERROR, 'socket is reconnecting or closed'
        self._is_socket_reconnecting = True

        logger.debug(" enter ...")
        self._clear_conn_id()
        self._count_reconnect += 1

        try:
            self._sync_query_lock.acquire()

            # create sync socket and loop wait to connect api server
            self._thread_check_sync_sock = None
            if self._sync_net_ctx is None:
                self._sync_net_ctx = _SyncNetworkQueryCtx(self.__host, self.__port,
                                    long_conn=True, connected_handler=self, create_session_handler=self)

            # sync socket reconnect
            self._sync_net_ctx.reconnect()
            self._event_async_close.clear()

            # run thread to check sync socket state
            self._thread_check_sync_sock = Thread(
                    target=self._thread_check_sync_sock_fun)
            self._thread_check_sync_sock.setDaemon(True)
            self._thread_check_sync_sock.start()

            # notify reconnected
            self.on_api_socket_reconnected()

        finally:
            try:
                self._is_socket_reconnecting = False
                if self._sync_query_lock:
                    self._sync_query_lock.release()
            except Exception as e:
                traceback.print_exc()
                err = sys.exc_info()[1]
                logger.debug(err)
            logger.debug(" leave ...")

        return RET_OK, ""

    def _wait_async_init_connect(self, timeout=5):

        if not self.__async_socket_enable:
            return RET_OK

        # send req
        ret_code, msg, req = InitConnect.pack_req(SysConfig.get_client_ver(), SysConfig.get_client_id(), True)
        if ret_code == RET_OK:
            ret_code, msg = self._send_async_req(req)
        if ret_code != RET_OK:
            logger.info("async int connect fail:{}".format(msg))
            return RET_ERROR, msg

        # wait
        last_time = time.time()
        last_log = last_time
        while True:
            sleep(0.01)
            if self._async_conn_id != 0:
                break
            cur_time = time.time()
            if cur_time - last_log >= 1:
                last_log = cur_time
                logger.debug("wait async init conn ...")
            if cur_time - last_time > timeout:
                break

        return RET_OK if self._async_conn_id != 0 else RET_ERROR

    @abstractmethod
    def notify_sync_socket_connected(self, sync_ctxt):
        """
        :param sync_ctxt:
        :return: (is_socket_ok[bool], is_to_retry_connect[bool])
        """
        if self._is_obj_closed or self._sync_net_ctx is None or self._sync_net_ctx is not sync_ctxt:
            return False, False

        logger.debug("sync socket init_connect")
        ret_code, _ = self._sync_init_connect()
        is_ready = ret_code == RET_OK
        is_retry = True

        # create async socket (for push data)
        if is_ready and self.__async_socket_enable:
            if self._async_ctx is None:
                self._handlers_ctx = HandlerContext(self._is_proc_run)
                self._async_ctx = _AsyncNetworkManager(
                    self.__host, self.__port, self._handlers_ctx, self)
                self.set_pre_handler(AsyncHandler_InitConnect(self))

            self._async_ctx.reconnect()

        # wait async init connect
        if is_ready:
            is_ready = (self._wait_async_init_connect() == RET_OK)

        if not is_ready:
            self._clear_conn_id()

        return is_ready, is_retry

    def notify_async_socket_close(self, async_ctx):
        """
         AsyncNetworkManager onclose callback
        """
        if self._is_socket_reconnecting or self._is_obj_closed or self._async_ctx is None or async_ctx is not self._async_ctx:
            return

        # auto reconnect
        self._event_async_close.set()

    def _thread_check_sync_sock_fun(self):
        """
        thread fun : timer to check socket state
        """
        thread_handle = self._thread_check_sync_sock
        while True:
            if self._thread_check_sync_sock is not thread_handle:
                if self._thread_check_sync_sock is None:
                    self._thread_is_exit = True
                logger.debug('check_sync_sock thread : exit by obj changed...')
                return
            if self._is_obj_closed:
                self._thread_is_exit = True
                return
            sync_net_ctx = self._sync_net_ctx
            if sync_net_ctx is None:
                self._thread_is_exit = True
                return
            # select sock to get err state
            is_async_close = self._event_async_close.wait(0.01)
            if is_async_close or not sync_net_ctx.is_sock_ok(0.01):
                self._thread_is_exit = True
                if self._thread_check_sync_sock is thread_handle and not self._is_obj_closed:
                    logger.debug("check_sync_sock thread : reconnect !")
                    self._socket_reconnect_and_wait_ready()
                return
            else:
                sleep(0.1)
            # send req loop per 10 seconds
            cur_time = time.time()
            if (self._check_last_req_time is
                    None) or (cur_time - self._check_last_req_time > 15):
                self._check_last_req_time = cur_time
                id_cur = id(self._thread_check_sync_sock)
                id_old = id(thread_handle)
                # if id_cur == id_old:
                #    self.get_global_state()

    def get_global_state(self):
        """
        get api server(exe) global state
        :return: RET_OK, state_dict | err_code, msg
        """
        query_processor = self._get_sync_query_processor(
            GlobalStateQuery.pack_req, GlobalStateQuery.unpack_rsp)

        kargs = {
            'user_id': self.get_login_user_id(),
            'conn_id': self.get_sync_conn_id(),
        }
        ret_code, msg, state_dict = query_processor(**kargs)
        if ret_code != RET_OK:
            return ret_code, msg

        return RET_OK, state_dict