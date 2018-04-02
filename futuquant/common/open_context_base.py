# -*- coding: utf-8 -*-

import time
from abc import ABCMeta, abstractmethod
from time import sleep
from threading import RLock, Thread
from futuquant.common.async_network_manager import _AsyncNetworkManager
from futuquant.common.sync_network_manager import _SyncNetworkQueryCtx
from futuquant.common.constant import *
from futuquant.common.utils import *
from futuquant.quote.response_handler import HandlerContext
from futuquant.quote.quote_query import GlobalStateQuery


class OpenContextBase(object):
    """Base class for set context"""
    metaclass__ = ABCMeta

    def __init__(self, host, port, sync_enable, async_enable):
        self.__host = host
        self.__port = port
        self.__sync_socket_enable = sync_enable
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

        if not self.__sync_socket_enable and not self.__async_socket_enable:
            raise Exception('you should specify at least one socket type to create !')

        self._socket_reconnect_and_wait_ready()

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
        # print("on_api_socket_reconnected obj ID={}".format(id(self)))
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

    def get_global_state(self):
        """
        get api server(exe) global state
        :return: RET_OK, state_dict | err_code, msg
        """
        query_processor = self._get_sync_query_processor(GlobalStateQuery.pack_req,
                                                         GlobalStateQuery.unpack_rsp)
        kargs = {"state_type": 0}
        ret_code, msg, state_dict = query_processor(**kargs)
        if ret_code != RET_OK:
            return ret_code, msg
        return RET_OK, state_dict

    def _is_proc_run(self):
        return self._proc_run

    def _send_sync_req(self, req_str):
        """
        send a synchronous request
        """
        ret, msg, content = self._sync_net_ctx.network_query(req_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None
        return RET_OK, msg, content

    def _send_async_req(self, req_str):
        """
        send a asynchronous request
        """
        if self._async_ctx:
            self._async_ctx.send(str2binary(req_str))
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
                    print(err)

        return sync_query_processor

    def _socket_reconnect_and_wait_ready(self):
        """
        sync_socket & async_socket recreate
        :return: None
        """
        if self._is_socket_reconnecting or self._is_obj_closed or self._sync_query_lock is None:
            return

        self._count_reconnect += 1
        # print("_socket_reconnect_and_wait_ready - count = %s" % self._count_reconnect)
        try:
            self._is_socket_reconnecting = True
            self._sync_query_lock.acquire()

            # create async socket (for push data)
            if self.__async_socket_enable:
                if self._async_ctx is None:
                    self._handlers_ctx = HandlerContext(self._is_proc_run)
                    self._async_ctx = _AsyncNetworkManager(self.__host, self.__port, self._handlers_ctx, self)
                else:
                    self._async_ctx.reconnect()

            # create sync socket and loop wait to connect api server
            if self.__sync_socket_enable:
                self._thread_check_sync_sock = None
                if self._sync_net_ctx is None:
                    self._sync_net_ctx = _SyncNetworkQueryCtx(self.__host, self.__port,
                                                              long_conn=True, connected_handler=self)
                self._sync_net_ctx.reconnect()

            # notify reconnected
            self.on_api_socket_reconnected()

            # run thread to check sync socket state
            if self.__sync_socket_enable:
                self._thread_check_sync_sock = Thread(target=self._thread_check_sync_sock_fun)
                self._thread_check_sync_sock.setDaemon(True)
                self._thread_check_sync_sock.start()
        finally:
            try:
                self._is_socket_reconnecting = False
                if self._sync_query_lock:
                    self._sync_query_lock.release()
            except Exception as e:
                traceback.print_exc()
                err = sys.exc_info()[1]
                print(err)

    def notify_sync_socket_connected(self, sync_ctxt):
        """
        :param sync_ctxt:
        :return: (is_socket_ok[bool], is_to_retry_connect[bool])
        """
        if self._is_obj_closed or self._sync_net_ctx is None or self._sync_net_ctx is not sync_ctxt:
            return False, False

        is_ready = False
        ret_code, state_dict = self.get_global_state()
        if ret_code == 0:
            is_ready = int(state_dict['Quote_Logined']) != 0 and int(state_dict['Trade_Logined']) != 0

        # 检查版本是否匹配
        if is_ready:
            cur_ver = state_dict['Version']
            if cur_ver < NN_VERSION_MIN:
                str_ver = cur_ver if cur_ver else str('未知')
                str_error = "API连接的客户端版本过低， 当前版本:\'%s\', 最低要求版本:\'%s\', 请联系管理员重新安装牛牛API客户端！" %(str_ver, NN_VERSION_MIN)
                raise Exception(str_error)

        return is_ready, True

    def notify_async_socket_close(self, async_ctx):
        """
         AsyncNetworkManager onclose callback
        """
        if self._is_obj_closed or self._async_ctx is None or async_ctx is not self._async_ctx:
            return
        # auto reconnect
        self._socket_reconnect_and_wait_ready()

    def _thread_check_sync_sock_fun(self):
        """
        thread fun : timer to check socket state
        """
        thread_handle = self._thread_check_sync_sock
        while True:
            if self._thread_check_sync_sock is not thread_handle:
                if self._thread_check_sync_sock is None:
                    self._thread_is_exit = True
                print ('check_sync_sock thread : exit by obj changed...')
                return
            if self._is_obj_closed:
                self._thread_is_exit = True
                return
            sync_net_ctx = self._sync_net_ctx
            if sync_net_ctx is None:
                self._thread_is_exit = True
                return
            # select sock to get err state
            if not sync_net_ctx.is_sock_ok(0.01):
                self._thread_is_exit = True
                if self._thread_check_sync_sock is thread_handle and not self._is_obj_closed:
                    print("check_sync_sock thread : reconnect !")
                    self._socket_reconnect_and_wait_ready()
                return
            else:
                sleep(0.1)
            # send req loop per 10 seconds
            cur_time = time.time()
            if (self._check_last_req_time is None) or (cur_time - self._check_last_req_time > 10):
                self._check_last_req_time = cur_time
                if self._thread_check_sync_sock is thread_handle:
                    self.get_global_state()