# -*- coding: utf-8 -*-
import pandas as pd

from futuquant.common.constant import *
from futuquant.common.utils import *
from futuquant.quote.quote_query import StockQuoteQuery


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
            col_list = [
                'code', 'time_key', 'open', 'close', 'high', 'low', 'volume',
                'turnover', 'k_type'
            ]
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

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, rt_data_list = RtDataQuery.unpack_rsp(rsp_str)
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

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, bid_content, ask_content = BrokerQueueQuery.unpack_rsp(
            rsp_str)
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
        ret_code, msg, order_info = TradePushQuery.hk_unpack_order_push_rsp(
            rsp_str)
        order_list = [order_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = [
                'envtype', 'code', 'stock_name', 'dealt_avg_price',
                'dealt_qty', 'qty', 'orderid', 'order_type', 'order_side',
                'price', 'status', 'submited_time', 'updated_time'
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
        ret_code, msg, order_info = TradePushQuery.hk_unpack_order_push_rsp(
            rsp_str)

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
        ret_code, msg, order_info = TradePushQuery.us_unpack_order_push_rsp(
            rsp_str)
        order_list = [order_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = [
                'envtype', 'code', 'stock_name', 'dealt_avg_price',
                'dealt_qty', 'qty', 'orderid', 'order_type', 'order_side',
                'price', 'status', 'submited_time', 'updated_time'
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
        ret_code, msg, order_info = TradePushQuery.us_unpack_order_push_rsp(
            rsp_str)

        if ret_code == RET_OK:
            orderid = order_info['orderid']
            envtype = order_info['envtype']
            status = order_info['status']
            if self._notify_obj is not None and is_USTrade_order_status_finish(
                    status):
                self._notify_obj.on_trade_order_check(orderid, envtype, status)

        return ret_code, None


class HKTradeDealHandlerBase(RspHandlerBase):
    """Base class for handle trade deal push"""

    def on_recv_rsp(self, rsp_str):
        """receive response callback function"""
        ret_code, msg, deal_info = TradePushQuery.hk_unpack_deal_push_rsp(
            rsp_str)
        deal_list = [deal_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = [
                'envtype', 'code', 'stock_name', 'dealid', 'orderid', 'qty',
                'price', 'order_side', 'time', 'contra_broker_id',
                'contra_broker_name'
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
        ret_code, msg, deal_info = TradePushQuery.us_unpack_deal_push_rsp(
            rsp_str)
        deal_list = [deal_info]

        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            col_list = [
                'envtype',
                'code',
                'stock_name',
                'dealid',
                'orderid',
                'qty',
                'price',
                'order_side',
                'time',
            ]

            trade_frame_table = pd.DataFrame(deal_list, columns=col_list)

            return RET_OK, trade_frame_table

    def on_error(self, error_str):
        """error callback function"""
        return error_str


class HandlerContext:
    """Handle Context"""

    def __init__(self, cb_check_recv):
        self.cb_check_recv = cb_check_recv
        self._default_handler = RspHandlerBase()
        self._handler_table = {
            3005: {
                "type": StockQuoteHandlerBase,
                "obj": StockQuoteHandlerBase()
            },
            2208: {
                "type": OrderBookHandlerBase,
                "obj": OrderBookHandlerBase()
            },
            3007: {
                "type": CurKlineHandlerBase,
                "obj": CurKlineHandlerBase()
            },
            3011: {
                "type": TickerHandlerBase,
                "obj": TickerHandlerBase()
            },
            3009: {
                "type": RTDataHandlerBase,
                "obj": RTDataHandlerBase()
            },
            3015: {
                "type": BrokerHandlerBase,
                "obj": BrokerHandlerBase()
            },
            "1036": {
                "type": HeartBeatHandlerBase,
                "obj": HeartBeatHandlerBase()
            },
            "6200": {
                "type": HKTradeOrderHandlerBase,
                "obj": HKTradeOrderHandlerBase()
            },
            "6201": {
                "type": HKTradeDealHandlerBase,
                "obj": HKTradeDealHandlerBase()
            },
            "7200": {
                "type": USTradeOrderHandlerBase,
                "obj": USTradeOrderHandlerBase()
            },
            "7201": {
                "type": USTradeDealHandlerBase,
                "obj": USTradeDealHandlerBase()
            },
        }

        self._pre_handler_table = {
            "6200": {
                "type": HKTradeOrderPreHandler,
                "obj": HKTradeOrderPreHandler()
            },
            "7200": {
                "type": USTradeOrderPreHandler,
                "obj": USTradeOrderPreHandler()
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

    def recv_func(self, rsp_str, proto_id):
        """receive response callback function"""
        if self.cb_check_recv is not None and not self.cb_check_recv():
            return

        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            error_str = msg + rsp_str
            print(error_str)
            return
        print("recv push data and  proto_id")
        print(rsp, proto_id)
        print("################")
        handler = self._default_handler
        pre_handler = None

        if proto_id in self._handler_table:
            handler = self._handler_table[proto_id]['obj']

        if proto_id in self._pre_handler_table:
            pre_handler = self._pre_handler_table[proto_id]['obj']

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
