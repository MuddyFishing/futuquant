# -*- coding: utf-8 -*-
import pandas as pd
from futuquant.quote.quote_query import *
from futuquant.trade.trade_query import *


class RspHandlerBase(object):
    """callback function base class"""

    def __init__(self):
        pass

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        return 0, None

    def on_error(self, error_str):
        """error callback function"""
        pass


class StockQuoteHandlerBase(RspHandlerBase):
    """Base class for handle stock quote"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, quote_list = StockQuoteQuery.unpack_rsp(rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = [
                'code', 'data_date', 'data_time', 'last_price', 'open_price',
                'high_price', 'low_price', 'prev_close_price', 'volume',
                'turnover', 'turnover_rate', 'amplitude', 'suspension',
                'listing_date', 'price_spread'
            ]

            quote_frame_table = pd.DataFrame(quote_list, columns=col_list)

            return RET_OK, quote_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class OrderBookHandlerBase(RspHandlerBase):
    """Base class for handling order book data"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, order_book = OrderBookQuery.unpack_rsp(rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            return ret_code, order_book

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class CurKlineHandlerBase(RspHandlerBase):
    """Base class for handling current Kline data"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, kline_list = CurKlinePush.unpack_rsp(rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = [
                'code', 'time_key', 'open', 'close', 'high', 'low', 'volume',
                'turnover', 'k_type', 'last_close'
            ]
            kline_frame_table = pd.DataFrame(kline_list, columns=col_list)

            return RET_OK, kline_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class TickerHandlerBase(RspHandlerBase):
    """Base class for handling ticker data"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, ticker_list = TickerQuery.unpack_rsp(rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:

            col_list = [
                'code', 'time', 'price', 'volume', 'turnover',
                "ticker_direction", 'sequence'
            ]
            ticker_frame_table = pd.DataFrame(ticker_list, columns=col_list)

            return RET_OK, ticker_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class RTDataHandlerBase(RspHandlerBase):
    """Base class for handling real-time data"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, rt_data_list = RtDataQuery.unpack_rsp(rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:

            col_list = [
                'code', 'time', 'data_status', 'opened_mins', 'cur_price',
                "last_close", 'avg_price', 'turnover', 'volume'
            ]
            rt_data_table = pd.DataFrame(rt_data_list, columns=col_list)

            return RET_OK, rt_data_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class BrokerHandlerBase(RspHandlerBase):
    """Base class for handling broker"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, bid_content, ask_content = BrokerQueueQuery.unpack_rsp(
            rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, [bid_content, ask_content]
        else:
            bid_list = [
                'code', 'bid_broker_id', 'bid_broker_name', 'bid_broker_pos'
            ]
            ask_list = [
                'code', 'ask_broker_id', 'ask_broker_name', 'ask_broker_pos'
            ]
            bid_frame_table = pd.DataFrame(bid_content, columns=bid_list)
            ask_frame_table = pd.DataFrame(ask_content, columns=ask_list)

            return RET_OK, [bid_frame_table, ask_frame_table]

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class HeartBeatHandlerBase(RspHandlerBase):
    """Base class for handling Heart Beat"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, time = HeartBeatPush.unpack_rsp(rsp_pb)

        return ret_code, time

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class SysNotifyHandlerBase(RspHandlerBase):
    """sys notify"""
    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, content = SysNotifyPush.unpack_rsp(rsp_pb)

        return ret_code, content

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class AsyncHandler_TrdSubAccPush(RspHandlerBase):
    """ AsyncHandler_TrdSubAccPush"""
    def __init__(self, notify_obj=None):
        self._notify_obj = notify_obj
        super(AsyncHandler_TrdSubAccPush, self).__init__()

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, _= SubAccPush.unpack_rsp(rsp_pb)

        if self._notify_obj is not None:
            self._notify_obj.on_async_sub_acc_push(ret_code, msg)

        return ret_code, msg


class AsyncHandler_InitConnect(RspHandlerBase):
    """ AsyncHandler_TrdSubAccPush"""
    def __init__(self, notify_obj=None):
        self._notify_obj = notify_obj
        super(AsyncHandler_InitConnect, self).__init__()

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, conn_info_map = InitConnect.unpack_rsp(rsp_pb)

        if self._notify_obj is not None:
            self._notify_obj.on_async_init_connect(ret_code, msg, conn_info_map)

        return ret_code, msg


class HKTradeOrderPreHandler(RspHandlerBase):
    """class for pre handle trader order push"""

    def __init__(self, notify_obj=None):
        self._notify_obj = notify_obj
        super(HKTradeOrderPreHandler, self).__init__()

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, order_info = TradePushQuery.hk_unpack_order_push_rsp(
            rsp_pb)

        if ret_code == RET_OK:
            orderid = order_info['orderid']
            envtype = order_info['envtype']
            status = order_info['status']
            if self._notify_obj is not None:
                self._notify_obj.on_trade_order_check(orderid, envtype, status)

        return ret_code, None

class HandlerContext:
    """Handle Context"""

    def __init__(self, cb_check_recv):
        self.cb_check_recv = cb_check_recv
        self._default_handler = RspHandlerBase()
        self._handler_table = {
            1003: {
                "type": SysNotifyHandlerBase,
                "obj": SysNotifyHandlerBase()
            },
            1004: {
                "type": HeartBeatHandlerBase,
                "obj": HeartBeatHandlerBase()
            },
            3005: {
                "type": StockQuoteHandlerBase,
                "obj": StockQuoteHandlerBase()
            },
            3007: {
                "type": CurKlineHandlerBase,
                "obj": CurKlineHandlerBase()
            },
            3009: {
                "type": RTDataHandlerBase,
                "obj": RTDataHandlerBase()
            },
            3011: {
                "type": TickerHandlerBase,
                "obj": TickerHandlerBase()
            },
            3013: {
                "type": OrderBookHandlerBase,
                "obj": OrderBookHandlerBase()
            },
            3015: {
                "type": BrokerHandlerBase,
                "obj": BrokerHandlerBase()
            },
        }

        self._pre_handler_table = {
            1001: {
                "type": AsyncHandler_InitConnect,
                "obj": AsyncHandler_InitConnect()
            },
            2008: {
                "type": AsyncHandler_TrdSubAccPush,
                "obj": AsyncHandler_TrdSubAccPush()
            },
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

    def recv_func(self, rsp_pb, proto_id):
        """receive response callback function"""
        if self.cb_check_recv is not None and not self.cb_check_recv():
            return

        handler = self._default_handler
        pre_handler = None

        if proto_id in self._handler_table:
            handler = self._handler_table[proto_id]['obj']

        if proto_id in self._pre_handler_table:
            pre_handler = self._pre_handler_table[proto_id]['obj']

        if pre_handler is not None:
            pre_handler.on_recv_rsp(rsp_pb)

        ret, result = handler.on_recv_rsp(rsp_pb)
        if ret != RET_OK:
            error_str = result
            handler.on_error(error_str)

    @staticmethod
    def error_func(err_str):
        """error callback function"""
        print(err_str)
