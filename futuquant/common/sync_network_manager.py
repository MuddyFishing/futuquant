# -*- coding: utf-8 -*-

import select
import sys
import socket as sock
from struct import pack
from time import sleep
import traceback
from threading import RLock
from futuquant.common.constant import *
from futuquant.common.utils import *

class _SyncNetworkQueryCtx:
    """
    Network query context manages connection between python program and FUTU client program.

    Short (non-persistent) connection can be created by setting long_conn parameter False, which suggests that
    TCP connection is closed once a query session finished

    Long (persistent) connection can be created by setting long_conn parameter True, which suggests that TCP
    connection is persisted after a query session finished, waiting for next query.

    """

    def __init__(self, host, port, long_conn=True, connected_handler=None):
        self.s = None
        self.__host = host
        self.__port = port
        self.long_conn = long_conn
        self._socket_lock = RLock()
        self._connected_handler = connected_handler
        self._is_loop_connecting = False

    def close_socket(self):
        """close socket"""
        self._socket_lock.acquire()
        self._force_close_session()
        self._socket_lock.release()

    def is_sock_ok(self, timeout_select):
        """check if socket is OK"""
        self._socket_lock.acquire()
        try:
            ret = self._is_socket_ok(timeout_select)
        finally:
            self._socket_lock.release()
        return ret

    def _is_socket_ok(self, timeout_select):
        if not self.s:
            return False
        _, _, sel_except = select.select([self.s], [], [], timeout_select)
        if self.s in sel_except:
            return False
        return True

    def reconnect(self):
        """reconnect"""
        self._socket_create_and_loop_connect()

    def network_query(self, req_str):
        """
        the function sends req_str to FUTU client and try to get response from the client.
        :param req_str
        :return: rsp_str
        """
        try:
            ret, msg = self._create_session()
            self._socket_lock.acquire()
            if ret != RET_OK:
                return ret, msg, None

            # rsp_str = ''
            #s_buf = str2binary(req_str)
            #s_cnt = self.s.send(s_buf)
            #print(req_str)
            s_cnt = self.s.send(req_str)

            rsp_buf = b''
            while rsp_buf.find(b'\r\n\r\n') < 0:

                try:
                    recv_buf = self.s.recv(5 * 1024 * 1024)
                    rsp_buf += recv_buf
                    print("receive:*********")
                    print(rsp_buf)
                    if recv_buf == b'':
                        raise Exception("_SyncNetworkQueryCtx : remote server close")
                except Exception as e:
                    traceback.print_exc()
                    err = sys.exc_info()[1]
                    error_str = ERROR_STR_PREFIX + str(
                        err) + ' when receiving after sending %s bytes. For req: ' % s_cnt + ""
                    self._force_close_session()
                    return RET_ERROR, error_str, None

            rsp_str = binary2str(rsp_buf)
            self._close_session()
        except Exception as e:
            traceback.print_exc()
            err = sys.exc_info()[1]
            error_str = ERROR_STR_PREFIX + str(err) + ' when sending. For req: ' + req_str.decode()

            self._force_close_session()
            return RET_ERROR, error_str, None
        finally:
            self._socket_lock.release()

        return RET_OK, "", rsp_str

    def _socket_create_and_loop_connect(self):

        self._socket_lock.acquire()
        is_socket_lock = True

        if self._is_loop_connecting:
            return RET_ERROR, "is loop connecting, can't create_session"
        self._is_loop_connecting = True

        if self.s is not None:
            self._force_close_session()

        while True:
            try:
                if not is_socket_lock:
                    is_socket_lock = True
                    self._socket_lock.acquire()
                s = sock.socket()
                s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 0)
                s.setsockopt(sock.SOL_SOCKET, sock.SO_LINGER, pack("ii", 0, 0))
                s.settimeout(10)
                self.s = s
                self.s.connect((self.__host, self.__port))
            except Exception as e:
                traceback.print_exc()
                err = sys.exc_info()[1]
                err_msg = ERROR_STR_PREFIX + str(err)
                print("socket connect err:{}".format(err_msg))
                self.s = None
                if s:
                    s.close()
                    del s
                sleep(1.5)
                continue

            if self._connected_handler is not None:
                is_socket_lock = False
                self._socket_lock.release()

                sock_ok, is_retry = self._connected_handler.notify_sync_socket_connected(self)
                if not sock_ok:
                    self._force_close_session()
                    if is_retry:
                        print("wait to connect futunn plugin server")
                        sleep(1.5)
                        continue
                    else:
                        return RET_ERROR, "obj is closed"
                else:
                    break
        self._is_loop_connecting = False
        if is_socket_lock:
            # is_socket_lock = False
            self._socket_lock.release()

        return RET_OK, ''

    def _create_session(self):
        if self.long_conn is True and self.s is not None:
            return RET_OK, ""
        ret, msg = self._socket_create_and_loop_connect()
        if ret != RET_OK:
            return ret, msg
        return RET_OK, ""

    def _force_close_session(self):
        if self.s is None:
            return
        self.s.close()
        del self.s
        self.s = None

    def _close_session(self):
        if self.s is None or self.long_conn is True:
            return
        self.s.close()
        self.s = None

    def __del__(self):
        if self.s is not None:
            self.s.close()
            self.s = None


