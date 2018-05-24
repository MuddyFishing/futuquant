# -*- coding: utf-8 -*-

import select
from abc import abstractmethod
import socket as sock
from struct import pack
from time import sleep
import traceback
from threading import RLock
from futuquant.common.constant import *
from futuquant.common.utils import *
from futuquant.quote.quote_query import parse_head

class _SyncNetworkQueryCtx:
    """
    Network query context manages connection between python program and FUTU client program.

    Short (non-persistent) connection can be created by setting long_conn parameter False, which suggests that
    TCP connection is closed once a query session finished

    Long (persistent) connection can be created by setting long_conn parameter True, which suggests that TCP
    connection is persisted after a query session finished, waiting for next query.

    """

    def __init__(self, host, port, long_conn=True, connected_handler=None, create_session_handler=None):
        self.s = None
        self.__host = host
        self.__port = port
        self.long_conn = long_conn
        self._socket_lock = RLock()
        self._connected_handler = connected_handler
        self._is_loop_connecting = False
        self._create_session_handler = create_session_handler
        self._conn_id = 0

    def set_conn_id(self, conn_id):
        self._conn_id = conn_id

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
        logger.debug(" ****")
        self._socket_create_and_loop_connect()

    def network_query(self, req_str, is_create_socket=True):
        """
        the function sends req_str to FUTU client and try to get response from the client.
        :param req_str
        :return: rsp_str
        """
        try:
            is_socket_lock = False
            ret, msg = self._create_session(is_create_socket)
            if ret != RET_OK:
                return ret, msg, None

            self._socket_lock.acquire()
            is_socket_lock = True

            head_len = get_message_head_len()
            req_head_dict = parse_head(req_str[:head_len])
            s_cnt = self.s.send(req_str)

            is_rsp_body = False
            left_buf = b''
            rsp_body = b''
            head_dict = []
            while not is_rsp_body:
                if len(left_buf) < head_len:
                    recv_buf = self.s.recv(5 * 1024 * 1024)
                    if recv_buf == b'':
                        raise Exception("_SyncNetworkQueryCtx : head recv error, remote server close")
                    left_buf += recv_buf

                head_dict = parse_head(left_buf[:head_len])
                rsp_body = left_buf[head_len:]

                while head_dict['body_len'] > len(rsp_body):
                    try:
                        recv_buf = self.s.recv(5 * 1024 * 1024)
                        rsp_body += recv_buf
                        if recv_buf == b'':
                            raise Exception("_SyncNetworkQueryCtx : body recv error, remote server close")
                    except Exception as e:
                        traceback.print_exc()
                        err = sys.exc_info()[1]
                        error_str = ERROR_STR_PREFIX + str(
                            err) + ' when receiving after sending %s bytes.' % s_cnt + ""
                        self._force_close_session()
                        return RET_ERROR, error_str, None
                if head_dict["proto_id"] == req_head_dict['proto_id']:
                    is_rsp_body = True
                else:
                    left_buf = rsp_body[head_dict['body_len']:]
                    logger.debug("req protoID={}, recv protoID={}".format(req_head_dict["proto_id"], head_dict["proto_id"]))

            # 数据解密码校验
            """
            from binascii import b2a_hex, a2b_hex
            import base64
            if head_dict['proto_id'] == ProtoId.InitConnect:
                print(base64.b64encode(rsp_body))
            """
            ret_decrypt, msg_decrypt, rsp_body = decrypt_rsp_body(rsp_body, head_dict, self._conn_id)

            if ret_decrypt != RET_OK:
                return ret_decrypt, msg_decrypt, None

            rsp_pb = binary2pb(rsp_body, head_dict['proto_id'], head_dict['proto_fmt_type'])
            if rsp_pb is None:
                return RET_ERROR, "parse error", None

            self._close_session()
        except Exception as e:
            traceback.print_exc()
            err = sys.exc_info()[1]
            error_str = ERROR_STR_PREFIX + str(err) + ' when sending.'

            self._force_close_session()
            return RET_ERROR, error_str, None
        finally:
            if is_socket_lock:
                self._socket_lock.release()

        return RET_OK, "", rsp_pb

    def _socket_create_and_loop_connect(self):

        logger.debug("***")
        if self._is_loop_connecting:
            return RET_ERROR, "is loop connecting, can't create_session"
        self._is_loop_connecting = True

        self._socket_lock.acquire()
        is_socket_lock = True

        if self.s is not None:
            self._force_close_session()

        conn_cnt = 0
        while True:
            try:
                if not is_socket_lock:
                    is_socket_lock = True
                    self._socket_lock.acquire()
                s = sock.socket()
                s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 0)
                s.setsockopt(sock.SOL_SOCKET, sock.SO_LINGER, pack("ii", 1, 0))
                s.settimeout(10)
                self.s = s
                self.s.connect((self.__host, self.__port))
            except Exception as e:
                traceback.print_exc()
                err = sys.exc_info()[1]
                err_msg = ERROR_STR_PREFIX + str(err)
                logger.debug("socket connect count:{} err:{}".format(conn_cnt, err_msg))
                conn_cnt += 1
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
                        logger.debug("wait to connect futunn plugin server")
                        sleep(1.5)
                        continue
                    else:
                        return RET_ERROR, "obj is closed"
                else:
                    break
        self._is_loop_connecting = False
        if is_socket_lock:
            self._socket_lock.release()

        return RET_OK, ''

    def on_create_sync_session(self):
        self.reconnect()
        return RET_OK, ""

    def _create_session(self, is_create_socket):
        if self.long_conn is True and self.s is not None:
            return RET_OK, ""

        if not is_create_socket:
            return RET_ERROR, "no exist connect session"

        if self._create_session_handler:
            ret, msg = self._create_session_handler.on_create_sync_session()
        else:
            ret, msg = self.on_create_sync_session()

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


