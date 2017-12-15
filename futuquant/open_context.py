# -*- coding: utf-8 -*-
"""
    Market quote and trade context setting
"""

from .quote_query import *
from .trade_query import *
from .utils import is_str
from multiprocessing import Queue
from threading import RLock, Thread
import select
import sys
import pandas as pd
import asyncore
import socket as sock
import time
from time import sleep
from abc import ABCMeta, abstractmethod
from struct import pack
import traceback


class RspHandlerBase(object):
    """callback function base class"""

    def __init__(self):
        pass

    def on_recv_rsp(self, rsp_content):
        """receive response callback function"""
        return 0, None

    def on_error(self, error_str):
        """error callback function"""
        pass


class StockQuoteHandlerBase(RspHandlerBase):
    """Base class for handle stock quote"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, quote_list = StockQuoteQuery.unpack_rsp(rsp_str)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = ['code', 'data_date', 'data_time', 'last_price', 'open_price',
                        'high_price', 'low_price', 'prev_close_price',
                        'volume', 'turnover', 'turnover_rate', 'amplitude', 'suspension', 'listing_date'
                        ]

            quote_frame_table = pd.DataFrame(quote_list, columns=col_list)

            return RET_OK, quote_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class OrderBookHandlerBase(RspHandlerBase):
    """Base class for handling order book data"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, order_book = OrderBookQuery.unpack_rsp(rsp_str)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            return ret_code, order_book

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class CurKlineHandlerBase(RspHandlerBase):
    """Base class for handling current Kline data"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, kline_list = CurKlineQuery.unpack_rsp(rsp_str)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = ['code', 'time_key', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'k_type']
            kline_frame_table = pd.DataFrame(kline_list, columns=col_list)

            return RET_OK, kline_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class TickerHandlerBase(RspHandlerBase):
    """Base class for handling ticker data"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, ticker_list = TickerQuery.unpack_rsp(rsp_str)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:

            col_list = ['code', 'time', 'price', 'volume', 'turnover', "ticker_direction", 'sequence']
            ticker_frame_table = pd.DataFrame(ticker_list, columns=col_list)

            return RET_OK, ticker_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class RTDataHandlerBase(RspHandlerBase):
    """Base class for handling real-time data"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, rt_data_list = RtDataQuery.unpack_rsp(rsp_str)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:

            col_list = ['code', 'time', 'data_status', 'opened_mins', 'cur_price', "last_close", 'avg_price',
                        'turnover', 'volume']
            rt_data_table = pd.DataFrame(rt_data_list, columns=col_list)

            return RET_OK, rt_data_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class BrokerHandlerBase(RspHandlerBase):
    """Base class for handling broker"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, bid_content, ask_content = BrokerQueueQuery.unpack_rsp(rsp_str)
        if ret_code == RET_ERROR:
            return ret_code, [bid_content, ask_content]
        else:
            bid_list = ['code', 'bid_broker_id', 'bid_broker_name', 'bid_broker_pos']
            ask_list = ['code', 'ask_broker_id', 'ask_broker_name', 'ask_broker_pos']
            bid_frame_table = pd.DataFrame(bid_content, columns=bid_list)
            ask_frame_table = pd.DataFrame(ask_content, columns=ask_list)

            return RET_OK, [bid_frame_table, ask_frame_table]

    def on_error(self, error_str):
        """error callback function"""
        return error_str

class HeartBeatHandlerBase(RspHandlerBase):
    """Base class for handling Heart Beat"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, timestamp = HeartBeatPush.unpack_rsp(rsp_str)

        return ret_code, timestamp

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class HKTradeOrderHandlerBase(RspHandlerBase):
    """Base class for handle trader order push"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, order_info = TradePushQuery.hk_unpack_order_push_rsp(rsp_str)
        order_list = [order_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = ['envtype', 'code', 'stock_name', 'dealt_avg_price', 'dealt_qty',
                        'qty', 'orderid', 'order_type',
                        'order_side', 'price', 'status', 'submited_time', 'updated_time'
                        ]

            trade_frame_table = pd.DataFrame(order_list, columns=col_list)

            return RET_OK, trade_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class HKTradeOrderPreHandler(RspHandlerBase):
    """class for pre handle trader order push"""
    def __init__(self, notify_obj=None):
        self._notify_obj = notify_obj
        super(HKTradeOrderPreHandler, self).__init__()

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, order_info = TradePushQuery.hk_unpack_order_push_rsp(rsp_str)

        if ret_code == RET_OK:
            orderid = order_info['orderid']
            envtype = order_info['envtype']
            status = order_info['status']
            if self._notify_obj is not None:
                self._notify_obj.on_trade_order_check(orderid, envtype, status)

        return ret_code, None

class USTradeOrderHandlerBase(RspHandlerBase):
    """Base class for handle trader order push"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, order_info = TradePushQuery.us_unpack_order_push_rsp(rsp_str)
        order_list = [order_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = ['envtype', 'code', 'stock_name', 'dealt_avg_price', 'dealt_qty',
                        'qty', 'orderid', 'order_type',
                        'order_side', 'price', 'status', 'submited_time', 'updated_time'
                        ]

            trade_frame_table = pd.DataFrame(order_list, columns=col_list)

            return RET_OK, trade_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class USTradeOrderPreHandler(RspHandlerBase):
    """class for pre handle trader order push"""
    def __init__(self, notify_obj=None):
        self._notify_obj = notify_obj
        super(USTradeOrderPreHandler, self).__init__()

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, order_info = TradePushQuery.us_unpack_order_push_rsp(rsp_str)

        if ret_code == RET_OK:
            orderid = order_info['orderid']
            envtype = order_info['envtype']
            status = order_info['status']
            if self._notify_obj is not None and is_USTrade_order_status_finish(status):
                self._notify_obj.on_trade_order_check(orderid, envtype, status)

        return ret_code, None


class HKTradeDealHandlerBase(RspHandlerBase):
    """Base class for handle trade deal push"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, deal_info = TradePushQuery.hk_unpack_deal_push_rsp(rsp_str)
        deal_list = [deal_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = ['envtype', 'code', 'stock_name', 'dealid',
                        'orderid', 'qty', 'price', 'order_side',
                        'time', 'contra_broker_id', 'contra_broker_name'
                        ]

            trade_frame_table = pd.DataFrame(deal_list, columns=col_list)

            return RET_OK, trade_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class USTradeDealHandlerBase(RspHandlerBase):
    """Base class for handle trade deal push"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, deal_info = TradePushQuery.us_unpack_deal_push_rsp(rsp_str)
        deal_list = [deal_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = ['envtype', 'code', 'stock_name', 'dealid',
                        'orderid', 'qty', 'price', 'order_side', 'time',
                        ]

            trade_frame_table = pd.DataFrame(deal_list, columns=col_list)

            return RET_OK, trade_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class HandlerContext:
    """Handle Context"""

    def __init__(self):
        self._default_handler = RspHandlerBase()
        self._handler_table = {"1030": {"type": StockQuoteHandlerBase, "obj": StockQuoteHandlerBase()},
                               "1031": {"type": OrderBookHandlerBase, "obj": OrderBookHandlerBase()},
                               "1032": {"type": CurKlineHandlerBase, "obj": CurKlineHandlerBase()},
                               "1033": {"type": TickerHandlerBase, "obj": TickerHandlerBase()},
                               "1034": {"type": RTDataHandlerBase, "obj": RTDataHandlerBase()},
                               "1035": {"type": BrokerHandlerBase, "obj": BrokerHandlerBase()},
                               "1036": {"type": HeartBeatHandlerBase, "obj": HeartBeatHandlerBase()},
                               "6200": {"type": HKTradeOrderHandlerBase, "obj": HKTradeOrderHandlerBase()},
                               "6201": {"type": HKTradeDealHandlerBase, "obj": HKTradeDealHandlerBase()},
                               "7200": {"type": USTradeOrderHandlerBase, "obj": USTradeOrderHandlerBase()},
                               "7201": {"type": USTradeDealHandlerBase, "obj": USTradeDealHandlerBase()},
                               }

        self._pre_handler_table = {
                               "6200": {"type": HKTradeOrderPreHandler, "obj": HKTradeOrderPreHandler()},
                               "7200": {"type": USTradeOrderPreHandler, "obj": USTradeOrderPreHandler()},
                               }
        # self._pre_handler_table = self._handler_table.copy()

    def set_pre_handler(self, handler):
        '''pre handler push
        return: ret_error or ret_ok
        '''
        set_flag = False
        for protoc in self._pre_handler_table:
            if isinstance(handler, self._pre_handler_table[protoc]["type"]):
                self._pre_handler_table[protoc]["obj"] = handler
                return RET_OK

        if set_flag is False:
            return RET_ERROR

    def set_handler(self, handler):
        """
        set the callback processing object to be used by the receiving thread after receiving the data.User should set
        their own callback object setting in order to achieve event driven.
        :param handler:the object in callback handler base
        :return: ret_error or ret_ok
        """
        set_flag = False
        for protoc in self._handler_table:
            if isinstance(handler, self._handler_table[protoc]["type"]):
                self._handler_table[protoc]["obj"] = handler
                return RET_OK

        if set_flag is False:
            return RET_ERROR

    def recv_func(self, rsp_str):
        """receive response callback function"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            error_str = msg + rsp_str
            print(error_str)
            return

        protoc_num = rsp["Protocol"]
        handler = self._default_handler
        pre_handler = None

        if protoc_num in self._handler_table:
            handler = self._handler_table[protoc_num]['obj']

        if protoc_num in self._pre_handler_table:
            pre_handler = self._pre_handler_table[protoc_num]['obj']

        if pre_handler is not None:
            pre_handler.on_recv_rsp(rsp_str)

        ret, result = handler.on_recv_rsp(rsp_str)
        if ret != RET_OK:
            error_str = result
            handler.on_error(error_str)

    @staticmethod
    def error_func(err_str):
        """error callback function"""
        print(err_str)


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
            s_buf = str2binary(req_str)
            s_cnt = self.s.send(s_buf)

            rsp_buf = b''
            while rsp_buf.find(b'\r\n\r\n') < 0:

                try:
                    recv_buf = self.s.recv(5 * 1024 * 1024)
                    rsp_buf += recv_buf
                    if recv_buf == b'':
                        raise Exception("_SyncNetworkQueryCtx : remote server close")
                except Exception as e:
                    traceback.print_exc()
                    err = sys.exc_info()[1]
                    error_str = ERROR_STR_PREFIX + str(
                        err) + ' when receiving after sending %s bytes. For req: ' % s_cnt + req_str
                    self._force_close_session()
                    return RET_ERROR, error_str, None

            rsp_str = binary2str(rsp_buf)
            self._close_session()
        except Exception as e:
            traceback.print_exc()
            err = sys.exc_info()[1]
            error_str = ERROR_STR_PREFIX + str(err) + ' when sending. For req: ' + req_str

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


class _AsyncNetworkManager(asyncore.dispatcher_with_send):
    def __init__(self, host, port, handler_ctx, close_handler=None):
        self.__host = host
        self.__port = port
        self.__close_handler = close_handler

        asyncore.dispatcher_with_send.__init__(self)
        self._socket_create_and_connect()

        time.sleep(0.1)
        self.rsp_buf = b''
        self.handler_ctx = handler_ctx

    def reconnect(self):
        """reconnect"""
        self._socket_create_and_connect()

    def close_socket(self):
        """close socket"""
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

        self._req_queue = None
        self._handlers_ctx = None
        self._proc_run = False
        self._net_proc = None
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

        self._req_queue = None
        self._handlers_ctx = None

    def start(self):
        """
        start the receiving thread,asynchronously receive the data pushed by the client
        """
        if self._proc_run is True or self._net_proc is None:
            return

        self._net_proc.start()
        self._proc_run = True

    def stop(self):
        """
        stop the receiving thread, no longer receive the data pushed by the client
        """
        if self._proc_run:
            self._stop_net_proc()
            self._net_proc.join(timeout=5)
            self._net_proc = None
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
        if self._req_queue.full() is False:
            try:
                self._req_queue.put((True, req_str), timeout=1)
                return RET_OK, ''
            except Exception as e:
                traceback.print_exc()
                _ = e
                err = sys.exc_info()[1]
                error_str = ERROR_STR_PREFIX + str(err)
                return RET_ERROR, error_str
        else:
            error_str = ERROR_STR_PREFIX + "Request queue is full. The size: %s" % self._req_queue.qsize()
            return RET_ERROR, error_str

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

    def _stop_net_proc(self):
        """
        stop the request of network
        :return: (ret_error,error_str)
        """
        if self._req_queue.full() is False:
            try:
                self._req_queue.put((False, None), timeout=1)
                return RET_OK, ''
            except Exception as e:
                traceback.print_exc()
                _ = e
                err = sys.exc_info()[1]
                error_str = ERROR_STR_PREFIX + str(err)
                return RET_ERROR, error_str
        else:
            error_str = ERROR_STR_PREFIX + "Cannot send stop request. queue is full. The size: %s" \
                                           % self._req_queue.qsize()
            return RET_ERROR, error_str

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
                    self._handlers_ctx = HandlerContext()
                    self._req_queue = Queue()
                    self._async_ctx = _AsyncNetworkManager(self.__host, self.__port, self._handlers_ctx, self)
                    if self._net_proc is None:
                        self._net_proc = Thread(target=self._fun_net_proc, args=(self._async_ctx, self._req_queue,))
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

    def _fun_net_proc(self, async_ctx, req_queue):
        """
        processing request queue
        :param async_ctx:
        :param req_queue: request queue
        :return:
        """
        while True:
            if req_queue.empty() is False:
                try:
                    ctl_flag, req_str = req_queue.get(timeout=0.001)
                    if ctl_flag is False:
                        break
                    async_ctx.network_query(req_str)
                except Exception as e:
                    traceback.print_exc()

            asyncore.loop(timeout=0.001, count=5)


class OpenQuoteContext(OpenContextBase):
    """Class for set context of stock quote"""

    def __init__(self, host='127.0.0.1', port=11111):
        self._ctx_subscribe = set()
        super(OpenQuoteContext, self).__init__(host, port, True, True)

    def close(self):
        """
        to call close old obj before loop create new, otherwise socket will encounter erro 10053 or more!
        """
        super(OpenQuoteContext, self).close()

    def on_api_socket_reconnected(self):
        """for API socket reconnected"""
        # auto subscribe
        set_sub = self._ctx_subscribe.copy()
        for (stock_code, data_type, push) in set_sub:
            for i in range(3):
                ret, _ = self.subscribe(stock_code, data_type, push)
                if ret == 0:
                    break
                else:
                    sleep(1)

    def get_trading_days(self, market, start_date=None, end_date=None):
        """get the trading days"""
        if market is None or is_str(market) is False:
            error_str = ERROR_STR_PREFIX + "the type of market param is wrong"
            return RET_ERROR, error_str

        if start_date is not None and is_str(start_date) is False:
            error_str = ERROR_STR_PREFIX + "the type of start_date param is wrong"
            return RET_ERROR, error_str

        if end_date is not None and is_str(end_date) is False:
            error_str = ERROR_STR_PREFIX + "the type of end_date param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(TradeDayQuery.pack_req,
                                                         TradeDayQuery.unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'market': market, 'start_date': start_date, "end_date": end_date}
        ret_code, msg, trade_day_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        return RET_OK, trade_day_list

    def get_stock_basicinfo(self, market, stock_type='STOCK'):
        """get the basic information of stock"""
        param_table = {'market': market, 'stock_type': stock_type}
        for x in param_table:
            param = param_table[x]
            if param is None or is_str(param) is False:
                error_str = ERROR_STR_PREFIX + "the type of %s param is wrong" % x
                return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(StockBasicInfoQuery.pack_req,
                                                         StockBasicInfoQuery.unpack_rsp)
        kargs = {"market": market, 'stock_type': stock_type}

        ret_code, msg, basic_info_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'name', 'lot_size', 'stock_type', 'stock_child_type', "owner_stock_code", "listing_date",
                    "stockid"]

        basic_info_table = pd.DataFrame(basic_info_list, columns=col_list)

        return RET_OK, basic_info_table

    def get_multiple_history_kline(self, codelist, start=None, end=None, ktype='K_DAY', autype='qfq'):
        if is_str(codelist):
            codelist = codelist.split(',')
        elif isinstance(codelist, list):
            pass
        else:
            raise Exception("code list must be like ['HK.00001', 'HK.00700'] or 'HK.00001,HK.00700'")
        result = []
        for code in codelist:
            ret, data = self.get_history_kline(code, start, end, ktype, autype)
            if ret != RET_OK:
                raise Exception('get history kline error {},{},{},{}'.format(code, start, end, ktype))
            result.append(data)
        return 0, result

    def get_history_kline(self, code, start=None, end=None, ktype='K_DAY', autype='qfq', fields=[KL_FIELD.ALL]):
        '''
        得到本地历史k线，需先参照帮助文档下载k线
        :param code: 股票code
        :param start: 开始时间 '%Y-%m-%d'
        :param end:  结束时间 '%Y-%m-%d'
        :param ktype: k线类型， 参见 KTYPE_MAP 定义 'K_1M' 'K_DAY'...
        :param autype: 复权类型, 参见 AUTYPE_MAP 定义 'None', 'qfq', 'hfq'
        :param fields: 需返回的字段列表，参见 KL_FIELD 定义 KL_FIELD.ALL  KL_FIELD.OPEN ....
        :return: (ret, data) ret == 0 返回pd dataframe数据，表头包括'code', 'time_key', 'open', 'close', 'high', 'low',
                                        'volume', 'turnover', 'pe_ratio', 'turnover_rate' 'change_rate'
                             ret != 0 返回错误字符串
        '''
        """get the historic Kline data"""
        if start is not None and is_str(start) is False:
            error_str = ERROR_STR_PREFIX + "the type of start param is wrong"
            return RET_ERROR, error_str

        if end is not None and is_str(end) is False:
            error_str = ERROR_STR_PREFIX + "the type of end param is wrong"
            return RET_ERROR, error_str

        req_fields = unique_and_normalize_list(fields)
        if not fields:
            req_fields = copy(KL_FIELD.ALL_REAL)
        req_fields = KL_FIELD.normalize_field_list(req_fields)
        if not req_fields:
            error_str = ERROR_STR_PREFIX + "the type of fields param is wrong"
            return RET_ERROR, error_str

        if autype is None:
            autype = 'None'

        param_table = {'code': code, 'ktype': ktype, 'autype': autype}
        for x in param_table:
            param = param_table[x]
            if param is None or is_str(param) is False:
                error_str = ERROR_STR_PREFIX + "the type of %s param is wrong" % x
                return RET_ERROR, error_str

        req_start = start
        max_kl_num = 1000
        data_finish = False
        list_ret = []
        # 循环请求数据，避免一次性取太多超时
        while not data_finish:
            kargs = {"stock_str": code, "start_date": req_start, "end_date": end, "ktype": ktype, "autype": autype, "fields": req_fields, "max_num": max_kl_num}
            query_processor = self._get_sync_query_processor(HistoryKlineQuery.pack_req,
                                                             HistoryKlineQuery.unpack_rsp)
            ret_code, msg, content = query_processor(**kargs)
            if ret_code != RET_OK:
                return ret_code, msg

            list_kline, has_next, next_time = content
            data_finish = (not has_next) or (not next_time)
            req_start = next_time
            for dict_item in list_kline:
                list_ret.append(dict_item)

        # 表头列
        col_list = ['code']
        for field in req_fields:
            str_field = KL_FIELD.DICT_KL_FIELD_STR[field]
            if str_field not in col_list:
                col_list.append(str_field)

        kline_frame_table = pd.DataFrame(list_ret, columns=col_list)

        return RET_OK, kline_frame_table

    def get_autype_list(self, code_list):
        """get the autype list"""
        if code_list is None or isinstance(code_list, list) is False:
            error_str = ERROR_STR_PREFIX + "the type of code_list param is wrong"
            return RET_ERROR, error_str

        for code in code_list:
            if code is None or is_str(code) is False:
                error_str = ERROR_STR_PREFIX + "the type of param in code_list is wrong"
                return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(ExrightQuery.pack_req,
                                                         ExrightQuery.unpack_rsp)
        kargs = {"stock_list": code_list}
        ret_code, msg, exr_record = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code',
                    'ex_div_date',
                    'split_ratio',
                    'per_cash_div',
                    'per_share_div_ratio',
                    'per_share_trans_ratio',
                    'allotment_ratio',
                    'allotment_price',
                    'stk_spo_ratio',
                    'stk_spo_price',
                    'forward_adj_factorA',
                    'forward_adj_factorB',
                    'backward_adj_factorA',
                    'backward_adj_factorB']

        exr_frame_table = pd.DataFrame(exr_record, columns=col_list)

        return RET_OK, exr_frame_table

    def get_market_snapshot(self, code_list):
        """get teh market snapshot"""
        code_list = unique_and_normalize_list(code_list)
        if not code_list:
            error_str = ERROR_STR_PREFIX + "the type of code param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(MarketSnapshotQuery.pack_req,
                                                         MarketSnapshotQuery.unpack_rsp)
        kargs = {"stock_list": code_list}

        ret_code, msg, snapshot_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'update_time', 'last_price', 'open_price',
                    'high_price', 'low_price', 'prev_close_price',
                    'volume', 'turnover', 'turnover_rate', 'suspension', 'listing_date',
                    'circular_market_val', 'total_market_val', 'wrt_valid',
                    'wrt_conversion_ratio', 'wrt_type', 'wrt_strike_price',
                    'wrt_maturity_date', 'wrt_end_trade', 'wrt_code',
                    'wrt_recovery_price', 'wrt_street_vol', 'wrt_issue_vol',
                    'wrt_street_ratio', 'wrt_delta', 'wrt_implied_volatility', 'wrt_premium', 'lot_size',
                    # 2017.11.6 add
                    'issued_shares', 'net_asset', 'net_profit', 'earning_per_share',
                    'outstanding_shares', 'net_asset_per_share', 'ey_ratio', 'pe_ratio', 'pb_ratio',
                    ]

        snapshot_frame_table = pd.DataFrame(snapshot_list, columns=col_list)

        return RET_OK, snapshot_frame_table

    def get_rt_data(self, code):
        """get real-time data"""
        if code is None or is_str(code) is False:
            error_str = ERROR_STR_PREFIX + "the type of param in code is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(RtDataQuery.pack_req,
                                                         RtDataQuery.unpack_rsp)
        kargs = {"stock_str": code}

        ret_code, msg, rt_data_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'time', 'data_status', 'opened_mins', 'cur_price', 'last_close',
                    'avg_price', 'volume', 'turnover']

        rt_data_table = pd.DataFrame(rt_data_list, columns=col_list)

        return RET_OK, rt_data_table

    def get_plate_list(self, market, plate_class):
        """get stock list of the given plate"""
        param_table = {'market': market, 'plate_class': plate_class}
        for x in param_table:
            param = param_table[x]
            if param is None or is_str(market) is False:
                error_str = ERROR_STR_PREFIX + "the type of market param is wrong"
                return RET_ERROR, error_str

        if market not in MKT_MAP:
            error_str = ERROR_STR_PREFIX + "the value of market param is wrong "
            return RET_ERROR, error_str

        if plate_class not in PLATE_CLASS_MAP:
            error_str = ERROR_STR_PREFIX + "the class of plate is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(SubplateQuery.pack_req,
                                                         SubplateQuery.unpack_rsp)
        kargs = {'market': market, 'plate_class': plate_class}

        ret_code, msg, subplate_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'plate_name', 'plate_id']

        subplate_frame_table = pd.DataFrame(subplate_list, columns=col_list)

        return RET_OK, subplate_frame_table

    def get_plate_stock(self, plate_code):
        """get the stock of the given plate"""
        if plate_code is None or is_str(plate_code) is False:
            error_str = ERROR_STR_PREFIX + "the type of stock_code is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(PlateStockQuery.pack_req,
                                                         PlateStockQuery.unpack_rsp)
        kargs = {"plate_code": plate_code}

        ret_code, msg, plate_stock_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'lot_size', 'stock_name', 'owner_market', 'stock_child_type', 'stock_type']

        plate_stock_table = pd.DataFrame(plate_stock_list, columns=col_list)

        return RET_OK, plate_stock_table

    def get_broker_queue(self, code):
        """get teh queue of the broker"""
        if code is None or is_str(code) is False:
            error_str = ERROR_STR_PREFIX + "the type of param in code is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(BrokerQueueQuery.pack_req,
                                                         BrokerQueueQuery.unpack_rsp)
        kargs = {"stock_str": code}

        ret_code, bid_list, ask_list = query_processor(**kargs)

        if ret_code == RET_ERROR:
            return ret_code, ERROR_STR_PREFIX, EMPTY_STRING

        col_bid_list = ['code', 'bid_broker_id', 'bid_broker_name', 'bid_broker_pos']
        col_ask_list = ['code', 'ask_broker_id', 'ask_broker_name', 'ask_broker_pos']

        bid_frame_table = pd.DataFrame(bid_list, columns=col_bid_list)
        sak_frame_table = pd.DataFrame(ask_list, columns=col_ask_list)
        return RET_OK, bid_frame_table, sak_frame_table

    def subscribe(self, stock_code, data_type, push=False):
        """
        subscribe a sort of data for a stock
        :param stock_code: string stock_code . For instance, "HK.00700", "US.AAPL"
        :param data_type: string  data type. For instance, "K_1M", "K_MON"
        :param push: push option
        :return: (ret_code, ret_data). ret_code: RET_OK or RET_ERROR.
        """
        param_table = {'stock_code': stock_code, 'data_type': data_type}
        for x in param_table:
            param = param_table[x]
            if param is None or is_str(param) is False:
                error_str = ERROR_STR_PREFIX + "the type of %s param is wrong" % x
                return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(SubscriptionQuery.pack_subscribe_req,
                                                         SubscriptionQuery.unpack_subscribe_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'stock_str': stock_code, 'data_type': data_type}
        ret_code, msg, _ = query_processor(**kargs)

        # update subscribe context info
        sub_obj = (str(stock_code), str(data_type), bool(push))
        self._ctx_subscribe.add(sub_obj)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        if push:
            ret_code, msg, push_req_str = SubscriptionQuery.pack_push_req(stock_code, data_type)

            if ret_code != RET_OK:
                return RET_ERROR, msg

            ret_code, msg = self._send_async_req(push_req_str)
            if ret_code != RET_OK:
                return RET_ERROR, msg

        return RET_OK, None

    def unsubscribe(self, stock_code, data_type, unpush=True):
        """
        unsubcribe a sort of data for a stock
        :param stock_code: string stock_code . For instance, "HK.00700", "US.AAPL"
        :param data_type: string  data type. For instance, "K_1M", "K_MON"
        :param unpush: bool
        :return: (ret_code, ret_data). ret_code: RET_OK or RET_ERROR.
        """

        param_table = {'stock_code': stock_code, 'data_type': data_type}
        for x in param_table:
            param = param_table[x]
            if param is None or is_str(param) is False:
                error_str = ERROR_STR_PREFIX + "the type of %s param is wrong" % x
                return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(SubscriptionQuery.pack_unsubscribe_req,
                                                         SubscriptionQuery.unpack_unsubscribe_rsp)
        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'stock_str': stock_code, 'data_type': data_type}

        # update subscribe context info
        unsub_obj1 = (str(stock_code), str(data_type), True)
        unsub_obj2 = (str(stock_code), str(data_type), False)
        if unsub_obj1 in self._ctx_subscribe:
            self._ctx_subscribe.remove(unsub_obj1)
        if unsub_obj2 in self._ctx_subscribe:
            self._ctx_subscribe.remove(unsub_obj2)

        ret_code, msg, _ = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        if unpush:
            ret_code, msg, unpush_req_str = SubscriptionQuery.pack_unpush_req(stock_code, data_type)

            if ret_code != RET_OK:
                return RET_ERROR, msg

            ret_code, msg = self._send_async_req(unpush_req_str)
            if ret_code != RET_OK:
                return RET_ERROR, msg

        return RET_OK, None

    def query_subscription(self, query=0):
        """
        get the current subscription table
        :return:
        """
        query_processor = self._get_sync_query_processor(SubscriptionQuery.pack_subscription_query_req,
                                                         SubscriptionQuery.unpack_subscription_query_rsp)
        kargs = {"query": query}

        ret_code, msg, subscription_table = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        return RET_OK, subscription_table

    def get_stock_quote(self, code_list):
        """
        :param code_list:
        :return: DataFrame of quote data

        Usage:

        After subcribe "QUOTE" type for given stock codes, invoke

        get_stock_quote to obtain the data

        """
        code_list = unique_and_normalize_list(code_list)
        if not code_list:
            error_str = ERROR_STR_PREFIX + "the type of code_list param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(StockQuoteQuery.pack_req,
                                                         StockQuoteQuery.unpack_rsp,
                                                         )
        kargs = {"stock_list": code_list}

        ret_code, msg, quote_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'data_date', 'data_time', 'last_price', 'open_price',
                    'high_price', 'low_price', 'prev_close_price',
                    'volume', 'turnover', 'turnover_rate', 'amplitude', 'suspension', 'listing_date'
                    ]

        quote_frame_table = pd.DataFrame(quote_list, columns=col_list)

        return RET_OK, quote_frame_table

    def get_rt_ticker(self, code, num=500):
        """
        get transaction information
        :param code: stock code
        :param num: the default is 500
        :return: (ret_ok, ticker_frame_table)
        """

        if code is None or is_str(code) is False:
            error_str = ERROR_STR_PREFIX + "the type of code param is wrong"
            return RET_ERROR, error_str

        if num is None or isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "the type of num param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(TickerQuery.pack_req,
                                                         TickerQuery.unpack_rsp,
                                                         )
        kargs = {"stock_str": code, "num": num}
        ret_code, msg, ticker_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'time', 'price', 'volume', 'turnover', "ticker_direction", 'sequence']
        ticker_frame_table = pd.DataFrame(ticker_list, columns=col_list)

        return RET_OK, ticker_frame_table

    def get_cur_kline(self, code, num, ktype='K_DAY', autype='qfq'):
        """
        get current kline
        :param code: stock code
        :param num:
        :param ktype: the type of kline
        :param autype:
        :return:
        """
        param_table = {'code': code, 'ktype': ktype}
        for x in param_table:
            param = param_table[x]
            if param is None or is_str(param) is False:
                error_str = ERROR_STR_PREFIX + "the type of %s param is wrong" % x
                return RET_ERROR, error_str

        if num is None or isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "the type of num param is wrong"
            return RET_ERROR, error_str

        if autype is not None and is_str(autype) is False:
            error_str = ERROR_STR_PREFIX + "the type of autype param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(CurKlineQuery.pack_req,
                                                         CurKlineQuery.unpack_rsp,
                                                         )

        kargs = {"stock_str": code, "num": num, "ktype": ktype, "autype": autype}
        ret_code, msg, kline_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = ['code', 'time_key', 'open', 'close', 'high', 'low', 'volume', 'turnover', 'pe_ratio', 'turnover_rate']
        kline_frame_table = pd.DataFrame(kline_list, columns=col_list)

        return RET_OK, kline_frame_table

    def get_order_book(self, code):
        """get the order book data"""
        if code is None or is_str(code) is False:
            error_str = ERROR_STR_PREFIX + "the type of code param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(OrderBookQuery.pack_req,
                                                         OrderBookQuery.unpack_rsp,
                                                         )

        kargs = {"stock_str": code}
        ret_code, msg, orderbook = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        return RET_OK, orderbook

    def get_suspension_info(self, codes, start='', end=''):
        '''
        指定时间段，获某一支股票的停牌日期
        :param codes: 股票code
        :param start: 开始时间 '%Y-%m-%d'
        :param end: 结束时间 '%Y-%m-%d'
        :return: (ret, data) ret == 0 data为pd dataframe数据， 表头'code' 'suspension_dates'(逗号分隔的多个日期字符串)
                         ret != 0 data为错误字符串
        '''
        req_codes = unique_and_normalize_list(codes)
        if not codes:
            error_str = ERROR_STR_PREFIX + "the type of code param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(SuspensionQuery.pack_req,
                                                         SuspensionQuery.unpack_rsp,
                                                         )

        kargs = {"codes": req_codes, "start": str(start), "end": str(end)}
        ret_code, msg, susp_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg
        col_list = ['code', 'suspension_dates']
        pd_frame = pd.DataFrame(susp_list, columns=col_list)

        return RET_OK, pd_frame

    def get_multi_points_history_kline(self, codes, dates, fields, ktype='K_DAY', autype='qfq', no_data_mode=KL_NO_DATA_MODE_FORWARD):
        '''
        获取多支股票多个时间点的指定数据列
        :param codes: 单个或多个股票 'HK.00700'  or  ['HK.00700', 'HK.00001']
        :param dates: 单个或多个日期 '2017-01-01' or ['2017-01-01', '2017-01-02']
        :param fields:单个或多个数据列 KL_FIELD.ALL or [KL_FIELD.DATE_TIME, KL_FIELD.OPEN]
        :param ktype: K线类型
        :param autype:复权类型
        :param no_data_mode: 指定时间为非交易日时，对应的k线数据取值模式，
        :return: pd frame 表头与指定的数据列相关， 固定表头包括'code'(代码) 'time_point'(指定的日期) 'data_valid' (0=无数据 1=请求点有数据 2=请求点无数据，取前一个)
        '''
        req_codes = unique_and_normalize_list(codes)
        if not codes:
            error_str = ERROR_STR_PREFIX + "the type of code param is wrong"
            return RET_ERROR, error_str

        req_dates = unique_and_normalize_list(dates)
        if not dates:
            error_str = ERROR_STR_PREFIX + "the type of dates param is wrong"
            return RET_ERROR, error_str

        req_fields = unique_and_normalize_list(fields)
        if not fields:
            req_fields = copy(KL_FIELD.ALL_REAL)
        req_fields = KL_FIELD.normalize_field_list(req_fields)
        if not req_fields:
            error_str = ERROR_STR_PREFIX + "the type of fields param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(MultiPointsHisKLine.pack_req,
                                                         MultiPointsHisKLine.unpack_rsp)
        all_num = max(1, len(req_dates) * len(req_codes))
        one_num = max(1, len(req_dates))
        max_data_num = 500
        max_kl_num = all_num if all_num <= max_data_num else int(max_data_num / one_num) * one_num
        if 0 == max_kl_num:
            error_str = ERROR_STR_PREFIX + "too much data to req"
            return RET_ERROR, error_str

        data_finish = False
        list_ret = []
        # 循环请求数据，避免一次性取太多超时
        while not data_finish:
            print('get_multi_points_history_kline - wait ... %s' % datetime.now())
            kargs = {"codes": req_codes, "dates": req_dates, "fields": req_fields, "ktype": ktype, "autype": autype, "max_num": max_kl_num, "no_data_mode":no_data_mode}
            ret_code, msg, content = query_processor(**kargs)
            if ret_code == RET_ERROR:
                return ret_code, msg

            list_kline, has_next = content
            data_finish = (not has_next)
            for dict_item in list_kline:
                item_code = dict_item['code']
                if has_next and item_code in req_codes:
                    req_codes.remove(item_code)
                list_ret.append(dict_item)
            if 0 == len(req_codes):
                data_finish = True


        # 表头列
        col_list = ['code', 'time_point', 'data_valid']
        for field in req_fields:
            str_field = KL_FIELD.DICT_KL_FIELD_STR[field]
            if str_field not in col_list:
                col_list.append(str_field)

        pd_frame = pd.DataFrame(list_ret, columns=col_list)

        return RET_OK, pd_frame

class SafeTradeSubscribeList:
    def __init__(self):
        self._list_sub = []
        self._lock = RLock()

    def add_val(self, orderid, envtype):
        self._lock.acquire()
        self._list_sub.append((str(orderid), int(envtype)))
        self._lock.release()

    def has_val(self, orderid, envtype):
        ret_val = False
        self._lock.acquire()
        if (str(orderid), int(envtype)) in self._list_sub:
            ret_val = True
        self._lock.release()
        return ret_val

    def del_val(self, orderid, envtype):
        self._lock.acquire()
        key = (str(orderid), int(envtype))
        if key in self._list_sub:
            self._list_sub.remove(key)
        self._lock.release()

    def copy(self):
        list_ret = None
        self._lock.acquire()
        list_ret = [i for i in self._list_sub]
        self._lock.release()
        return list_ret


class OpenHKTradeContext(OpenContextBase):
    """Class for set context of HK stock trade"""
    cookie = 100000

    def __init__(self, host="127.0.0.1", port=11111):
        self._ctx_unlock = None
        self._obj_order_sub = SafeTradeSubscribeList()

        super(OpenHKTradeContext, self).__init__(host, port, True, True)
        self.set_pre_handler(HKTradeOrderPreHandler(self))

    def close(self):
        """
        to call close old obj before loop create new, otherwise socket will encounter erro 10053 or more!
        """
        super(OpenHKTradeContext, self).close()

    def on_api_socket_reconnected(self):
        """for API socket reconnected"""
        # auto unlock
        if self._ctx_unlock is not None:
            for i in range(3):
                password, password_md5 = self._ctx_unlock
                ret, data = self.unlock_trade(password, password_md5)
                if ret == RET_OK:
                    break
                sleep(1)

        # auto subscribe order deal push
        list_sub = self._obj_order_sub.copy()
        dic_order = {}
        list_zero_order_env = []
        for (orderid, envtype) in list_sub:
            if str(orderid) == u'':
                list_zero_order_env.append(envtype)
                continue
            if envtype not in dic_order:
                dic_order[envtype] = []
            dic_order[envtype].append(orderid)

        for envtype in dic_order:
            self._subscribe_order_deal_push(dic_order[envtype], True, True, envtype)

        # use orderid blank to subscrible all order
        for envtype in list_zero_order_env:
            self._subscribe_order_deal_push([], True, False, envtype)

    def on_trade_order_check(self, orderid, envtype, status):
        '''multi thread notify order finish after subscribe order push'''
        if is_HKTrade_order_status_finish(status):
            self._obj_order_sub.del_val(orderid=orderid, envtype=envtype)
        elif (not self._obj_order_sub.has_val(orderid, envtype)) and self._obj_order_sub.has_val(u'', envtype):
            self._obj_order_sub.add_val(orderid, envtype)  #record info for subscribe order u''

    def _subscribe_order_deal_push(self, orderid_list, order_deal_push=True, push_atonce=True, envtype=0):
        """subscribe order for recv push data"""
        for orderid in orderid_list:
            if order_deal_push is False:
                self._obj_order_sub.del_val(orderid, envtype)
            else:
                self._obj_order_sub.add_val(orderid, envtype)

        ret_code, _, push_req_str = TradePushQuery.hk_pack_subscribe_req(
            str(self.cookie), str(envtype), orderid_list, str(int(order_deal_push)), str(int(push_atonce)))
        if ret_code == RET_OK:
            ret_code, _ = self._send_async_req(push_req_str)

        return ret_code

    def unlock_trade(self, password, password_md5=None):
        '''
        交易解锁，安全考虑，所有的交易api,需成功解锁后才可操作
        :param password: 明文密码字符串 (二选一）
        :param password_md5: 密码的md5字符串（二选一）
        :return:(ret, data) ret == 0 时, data为None
                            ret != 0 时， data为错误字符串
        '''
        query_processor = self._get_sync_query_processor(UnlockTrade.pack_req,
                                                         UnlockTrade.unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'password': str(password) if password else '',
                 'password_md5': str(password_md5) if password_md5 else ''}

        ret_code, msg, unlock_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        # reconnected to auto unlock
        if RET_OK == ret_code:
            self._ctx_unlock = (password, password_md5)

            # unlock push socket
            ret_code, msg, push_req_str = UnlockTrade.pack_req(**kargs)
            if ret_code == RET_OK:
                self._send_async_req(push_req_str)

        return RET_OK, None

    def subscribe_order_deal_push(self, orderid_list, order_deal_push=True, envtype=0):
        """
        subscribe_order_deal_push
        """
        if not TRADE.check_envtype_hk(envtype):
            return RET_ERROR

        list_sub = [u'']
        if orderid_list is None:
            list_sub = [u'']
        elif isinstance(orderid_list, list):
            list_sub = [str(x) for x in orderid_list]
        else:
            list_sub = [str(orderid_list)]

        return self._subscribe_order_deal_push(list_sub, order_deal_push, True, envtype)

    def place_order(self, price, qty, strcode, orderside, ordertype=0, envtype=0, order_deal_push=False):
        """
        place order
        use  set_handle(HKTradeOrderHandlerBase) to recv order push !
        """
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        ret_code, content = split_stock_str(str(strcode))
        if ret_code == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        if int(market_code) != 1:
            error_str = ERROR_STR_PREFIX + "the type of stocks is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(PlaceOrder.hk_pack_req,
                                                         PlaceOrder.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype), 'orderside': str(orderside),
                 'ordertype': str(ordertype), 'price': str(price), 'qty': str(qty), 'strcode': str(stock_code)}

        ret_code, msg, place_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        # handle order push
        self._subscribe_order_deal_push(orderid_list=[place_order_list[0]['orderid']],
                                        order_deal_push=order_deal_push, envtype=envtype)

        col_list = ["envtype", "orderid", "code", "stock_name", "dealt_avg_price", "dealt_qty", "qty",
                    "order_type", "order_side", "price", "status", "submited_time", "updated_time"]

        place_order_table = pd.DataFrame(place_order_list, columns=col_list)

        return RET_OK, place_order_table

    def set_order_status(self, status, orderid=0, envtype=0):
        """for setting the status of order"""
        if int(status) not in TRADE.REV_ORDER_STATUS:
            error_str = ERROR_STR_PREFIX + "the type of status is wrong "
            return RET_ERROR, error_str

        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(SetOrderStatus.hk_pack_req,
                                                         SetOrderStatus.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype), 'localid': str(0),
                 'orderid': str(orderid), 'status': str(status)}

        ret_code, msg, set_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['envtype', 'orderID']
        set_order_table = pd.DataFrame(set_order_list, columns=col_list)

        return RET_OK, set_order_table

    def change_order(self, price, qty, orderid=0, envtype=0):
        """for changing the order"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(ChangeOrder.hk_pack_req,
                                                         ChangeOrder.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype), 'localid': str(0),
                 'orderid': str(orderid), 'price': str(price), 'qty': str(qty)}

        ret_code, msg, change_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['envtype', 'orderID']
        change_order_table = pd.DataFrame(change_order_list, columns=col_list)

        return RET_OK, change_order_table

    def accinfo_query(self, envtype=0):
        """
        query account information
        :param envtype: trading environment parameters,0 means real transaction and 1 means simulation trading
        :return:error return RET_ERROR,msg and ok return RET_OK,ret
        """
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(AccInfoQuery.hk_pack_req,
                                                         AccInfoQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype)}

        ret_code, msg, accinfo_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['Power', 'ZCJZ', 'ZQSZ', 'XJJY', 'KQXJ', 'DJZJ', 'ZSJE', 'ZGJDE', 'YYJDE', 'GPBZJ']
        accinfo_frame_table = pd.DataFrame(accinfo_list, columns=col_list)

        return RET_OK, accinfo_frame_table

    def order_list_query(self, orderid="", statusfilter="",  strcode='', start='', end='', envtype=0):
        """for querying the order list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(OrderListQuery.hk_pack_req,
                                                         OrderListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'orderid': str(orderid),
                 'statusfilter': str(statusfilter),
                 'strcode': str(stock_code),
                 'start': str(start),
                 'end': str(end),
                 'envtype': str(envtype)}
        ret_code, msg, order_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "dealt_avg_price", "dealt_qty", "qty",
                    "orderid", "order_type", "order_side", "price",
                    "status", "submited_time", "updated_time"]

        order_list_table = pd.DataFrame(order_list, columns=col_list)

        return RET_OK, order_list_table

    def position_list_query(self, strcode='', stocktype='', pl_ratio_min='',
                            pl_ratio_max='', envtype=0):
        """for querying the position list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(PositionListQuery.hk_pack_req,
                                                         PositionListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'strcode': str(stock_code),
                 'stocktype': str(stocktype),
                 'pl_ratio_min': str(pl_ratio_min),
                 'pl_ratio_max': str(pl_ratio_max),
                 'envtype': str(envtype)}
        ret_code, msg, position_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "qty", "can_sell_qty", "cost_price",
                    "cost_price_valid", "market_val", "nominal_price", "pl_ratio",
                    "pl_ratio_valid", "pl_val", "pl_val_valid", "today_buy_qty",
                    "today_buy_val", "today_pl_val", "today_sell_qty", "today_sell_val"]

        position_list_table = pd.DataFrame(position_list, columns=col_list)

        return RET_OK, position_list_table

    def deal_list_query(self, envtype=0):
        """for querying deal list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(DealListQuery.hk_pack_req,
                                                         DealListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype)}
        ret_code, msg, deal_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        # "orderside" 保留是为了兼容旧版本, 对外文档统一为"order_side"
        col_list = ["code", "stock_name", "dealid", "orderid",
                    "qty", "price", "orderside", "time", "order_side"]

        deal_list_table = pd.DataFrame(deal_list, columns=col_list)

        return RET_OK, deal_list_table

    def history_order_list_query(self, statusfilter='', strcode='', start='', end='', envtype=0):
        """for querying the order list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(HistoryOrderListQuery.hk_pack_req,
                                                         HistoryOrderListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'statusfilter': str(statusfilter),
                 'strcode': str(stock_code),
                 'start': str(start),
                 'end': str(end),
                 'envtype': str(envtype)}
        ret_code, msg, order_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "dealt_qty", "qty",
                    "orderid", "order_type", "order_side", "price",
                    "status", "submited_time", "updated_time"]

        order_list_table = pd.DataFrame(order_list, columns=col_list)

        return RET_OK, order_list_table

    def history_deal_list_query(self, strcode, start, end, envtype=0):
        """for querying deal list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(HistoryDealListQuery.hk_pack_req,
                                                         HistoryDealListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'strcode': str(stock_code),
                 'start': str(start),
                 'end': str(end),
                 'envtype': str(envtype)}

        ret_code, msg, deal_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "dealid", "orderid", "qty", "price",
                    "order_side", "time", "contra_broker_id", "contra_broker_name"]

        deal_list_table = pd.DataFrame(deal_list, columns=col_list)

        return RET_OK, deal_list_table

    def login_new_account(self, user_id, login_password_md5, trade_password, trade_password_md5=None):
        '''
        自动登陆一个新的牛牛帐号
        :param user_id: 牛牛号
        :param login_password_md5: 新帐号的登陆密码的md5值
        :param trade_password: 新帐号的交易密码
        :param trade_password_md5: 新帐号的交易密码的md5值 (跟交易密码二选一)
        :return:
        '''
        query_processor = self._get_sync_query_processor(LoginNewAccountQuery.pack_req,
                                                         LoginNewAccountQuery.unpack_rsp)

        kargs = {'cookie': str(self.cookie),
                 'user_id': str(user_id),
                 'password_md5': str(login_password_md5)
                 }

        # 切换帐号，必然会断线，故判断ret_code 无意义
        try:
            query_processor(**kargs)
        except Exception as e:
            pass

        # 触发重连等待
        self.get_global_state()

        # 接下来就是解锁交易密码
        ret = RET_OK
        data = ''
        if trade_password or trade_password_md5:
            ret, data = self.unlock_trade(trade_password, trade_password_md5)
        else:
            self._ctx_unlock = None

        return ret, data


class OpenUSTradeContext(OpenContextBase):
    """Class for set context of US stock trade"""
    cookie = 100000

    def __init__(self, host="127.0.0.1", port=11111):
        self._ctx_unlock = None
        self._obj_order_sub = SafeTradeSubscribeList()

        super(OpenUSTradeContext, self).__init__(host, port, True, True)
        self.set_pre_handler(USTradeOrderPreHandler(self))

    def close(self):
        """
        to call close old obj before loop create new, otherwise socket will encounter erro 10053 or more!
        """
        super(OpenUSTradeContext, self).close()

    def on_api_socket_reconnected(self):
        """for api socket reconnected"""
        # auto unlock
        if self._ctx_unlock is not None:
            for i in range(3):
                password, password_md5 = self._ctx_unlock
                ret, data = self.unlock_trade(password, password_md5)
                if ret == RET_OK:
                    break

        # auto subscribe order deal push
        list_sub = self._obj_order_sub.copy()
        dic_order = {}
        list_zero_order_env = []
        for (orderid, envtype) in list_sub:
            if str(orderid) == u'':
                list_zero_order_env.append(envtype)
                continue
            if envtype not in dic_order:
                dic_order[envtype] = []
            dic_order[envtype].append(orderid)

        for envtype in dic_order:
            self._subscribe_order_deal_push(dic_order[envtype], True, True, envtype)

        # use orderid blank to subscrible all order
        for envtype in list_zero_order_env:
            self._subscribe_order_deal_push([], True, False, envtype)

    def on_trade_order_check(self, orderid, envtype, status):
        '''multi thread notify order finish after subscribe order push'''
        if is_USTrade_order_status_finish(status):
            self._obj_order_sub.del_val(orderid=orderid, envtype=envtype)
        elif (not self._obj_order_sub.has_val(orderid, envtype)) and self._obj_order_sub.has_val(u'', envtype):
            self._obj_order_sub.add_val(orderid, envtype)  # record info for subscribe order u''

    def _subscribe_order_deal_push(self, orderid_list, order_deal_push=True, push_atonce=True, envtype=0):
        """subscribe order for recv push data"""
        for orderid in orderid_list:
            if order_deal_push is False:
                self._obj_order_sub.del_val(orderid, envtype)
            else:
                self._obj_order_sub.add_val(orderid, envtype)

        ret_code, _, push_req_str = TradePushQuery.us_pack_subscribe_req(
            str(self.cookie), str(envtype), orderid_list, str(int(order_deal_push)), str(int(push_atonce)))
        if ret_code == RET_OK:
            ret_code, _ = self._send_async_req(push_req_str)

        return ret_code

    def unlock_trade(self, password, password_md5=None):
        '''
        交易解锁，安全考虑，所有的交易api,需成功解锁后才可操作
        :param password: 明文密码字符串 (二选一）
        :param password_md5: 密码的md5字符串（二选一）
        :return:(ret, data) ret == 0 时, data为None
                            ret != 0 时， data为错误字符串
        '''
        query_processor = self._get_sync_query_processor(UnlockTrade.pack_req,
                                                         UnlockTrade.unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'password': str(password), 'password_md5': str(password_md5)}
        ret_code, msg, unlock_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        # reconnected to auto unlock
        if RET_OK == ret_code:
            self._ctx_unlock = (password, password_md5)

            # unlock push socket
            ret_code, msg, push_req_str = UnlockTrade.pack_req(**kargs)
            if ret_code == RET_OK:
                self._send_async_req(push_req_str)

        return RET_OK, None

    def subscribe_order_deal_push(self, orderid_list, order_deal_push=True, envtype=0):
        """
        subscribe_order_deal_push
        """
        if not TRADE.check_envtype_us(envtype):
            return RET_ERROR

        list_sub = [u'']
        if orderid_list is None:
            list_sub = [u'']
        elif isinstance(orderid_list, list):
            list_sub = [str(x) for x in orderid_list]
        else:
            list_sub = [str(orderid_list)]

        return self._subscribe_order_deal_push(list_sub, order_deal_push, True, envtype)

    def place_order(self, price, qty, strcode, orderside, ordertype=2, envtype=0, order_deal_push=False):
        """
        place order
        use  set_handle(USTradeOrderHandlerBase) to recv order push !
        """
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        ret_code, content = split_stock_str(str(strcode))
        if ret_code == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        if int(market_code) != 2:
            error_str = ERROR_STR_PREFIX + "the type of stocks is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(PlaceOrder.us_pack_req,
                                                         PlaceOrder.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype), 'orderside': str(orderside),
                 'ordertype': str(ordertype), 'price': str(price), 'qty': str(qty), 'strcode': str(stock_code)}

        ret_code, msg, place_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        # handle order push
        self._subscribe_order_deal_push(orderid_list=[place_order_list[0]['orderid']],
                                        order_deal_push=order_deal_push, envtype=envtype)

        col_list = ["envtype", "orderid", "code", "stock_name", "dealt_avg_price", "dealt_qty", "qty",
                    "order_type", "order_side", "price", "status", "submited_time", "updated_time"]

        place_order_table = pd.DataFrame(place_order_list, columns=col_list)

        return RET_OK, place_order_table

    def set_order_status(self, status=0, orderid=0, envtype=0):
        """for setting the statusof order"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        if int(status) != 0:
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support cancel order "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(SetOrderStatus.us_pack_req,
                                                         SetOrderStatus.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype), 'localid': str(0),
                 'orderid': str(orderid), 'status': '0'}

        ret_code, msg, set_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['envtype', 'orderID']
        set_order_table = pd.DataFrame(set_order_list, columns=col_list)

        return RET_OK, set_order_table

    def change_order(self, price, qty, orderid=0, envtype=0):
        """for changing the order"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(ChangeOrder.us_pack_req,
                                                         ChangeOrder.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype), 'localid': str(0),
                 'orderid': str(orderid), 'price': str(price), 'qty': str(qty)}

        ret_code, msg, change_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['envtype', 'orderID']
        change_order_table = pd.DataFrame(change_order_list, columns=col_list)

        return RET_OK, change_order_table

    def accinfo_query(self, envtype=0):
        """for querying the information of account"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(AccInfoQuery.us_pack_req,
                                                         AccInfoQuery.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype)}

        ret_code, msg, accinfo_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['Power', 'ZCJZ', 'ZQSZ', 'XJJY', 'KQXJ', 'DJZJ', 'ZSJE', 'ZGJDE', 'YYJDE', 'GPBZJ']
        accinfo_frame_table = pd.DataFrame(accinfo_list, columns=col_list)

        return RET_OK, accinfo_frame_table

    def order_list_query(self, orderid="", statusfilter="", strcode='', start='', end='', envtype=0):
        """for querying order list"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(OrderListQuery.us_pack_req,
                                                         OrderListQuery.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'orderid': str(orderid),
                 'statusfilter': str(statusfilter),
                 'strcode': str(stock_code),
                 'start': str(start),
                 'end': str(end),
                 'envtype': str(envtype)}
        ret_code, msg, order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "dealt_avg_price", "dealt_qty", "qty",
                    "orderid", "order_type", "order_side", "price",
                    "status", "submited_time", "updated_time"]

        order_list_table = pd.DataFrame(order_list, columns=col_list)

        return RET_OK, order_list_table

    def position_list_query(self, strcode='', stocktype='', pl_ratio_min='',
                            pl_ratio_max='', envtype=0):
        """for querying the position"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(PositionListQuery.us_pack_req,
                                                         PositionListQuery.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'strcode': str(stock_code),
                 'stocktype': str(stocktype),
                 'pl_ratio_min': str(pl_ratio_min),
                 'pl_ratio_max': str(pl_ratio_max),
                 'envtype': str(envtype)}
        ret_code, msg, position_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "qty", "can_sell_qty", "cost_price",
                    "cost_price_valid", "market_val", "nominal_price", "pl_ratio",
                    "pl_ratio_valid", "pl_val", "pl_val_valid", "today_buy_qty",
                    "today_buy_val", "today_pl_val", "today_sell_qty", "today_sell_val"]

        position_list_table = pd.DataFrame(position_list, columns=col_list)

        return RET_OK, position_list_table

    def deal_list_query(self, envtype=0):
        """for querying the deal list"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(DealListQuery.us_pack_req,
                                                         DealListQuery.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype)}
        ret_code, msg, deal_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        #"orderside" 保留是为了兼容旧版本, 对外文档统一为"order_side"
        col_list = ["code", "stock_name", "dealid", "orderid",
                    "qty", "price", "orderside", "time", "order_side"]

        deal_list_table = pd.DataFrame(deal_list, columns=col_list)

        return RET_OK, deal_list_table

    def history_order_list_query(self, statusfilter='', strcode='', start='', end='', envtype=0):
        """for querying order list"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "us stocks temporarily only support real trading "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(HistoryOrderListQuery.us_pack_req,
                                                         HistoryOrderListQuery.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'statusfilter': str(statusfilter),
                 'strcode': str(stock_code),
                 'start': str(start),
                 'end': str(end),
                 'envtype': str(envtype)}

        ret_code, msg, order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "dealt_qty", "qty",
                    "orderid", "order_type", "order_side", "price",
                    "status", "submited_time", "updated_time"]

        order_list_table = pd.DataFrame(order_list, columns=col_list)

        return RET_OK, order_list_table

    def history_deal_list_query(self, strcode, start, end, envtype=0):
        """for querying deal list"""
        if not TRADE.check_envtype_us(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(HistoryDealListQuery.us_pack_req,
                                                         HistoryDealListQuery.us_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie),
                 'strcode': str(stock_code),
                 'start': str(start),
                 'end': str(end),
                 'envtype': str(envtype)}

        ret_code, msg, deal_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["code", "stock_name", "dealid", "orderid",
                    "qty", "price", "order_side", "time"]

        deal_list_table = pd.DataFrame(deal_list, columns=col_list)

        return RET_OK, deal_list_table