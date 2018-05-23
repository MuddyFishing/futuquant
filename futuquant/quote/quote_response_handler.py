# -*- coding: utf-8 -*-
import pandas as pd
from futuquant.common import RspHandlerBase
from futuquant.quote.quote_query import *
from futuquant.trade.trade_query import *


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


class OrderBookHandlerBase(RspHandlerBase):
    """Base class for handling order book data"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, order_book = OrderBookQuery.unpack_rsp(rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:
            return ret_code, order_book


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


class RTDataHandlerBase(RspHandlerBase):
    """Base class for handling real-time data"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, rt_data_list = RtDataQuery.unpack_rsp(rsp_pb)
        if ret_code == RET_ERROR:
            return ret_code, msg
        else:

            col_list = [
                'code', 'time', 'is_blank', 'opened_mins', 'cur_price',
                "last_close", 'avg_price', 'turnover', 'volume'
            ]
            rt_data_table = pd.DataFrame(rt_data_list, columns=col_list)

            return RET_OK, rt_data_table


class BrokerHandlerBase(RspHandlerBase):
    """Base class for handling broker"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, (stock_code, bid_content, ask_content) = BrokerQueueQuery.unpack_rsp(
            rsp_pb)
        if ret_code != RET_OK:
            return ret_code, msg, None
        else:
            bid_list = [
                'code', 'bid_broker_id', 'bid_broker_name', 'bid_broker_pos'
            ]
            ask_list = [
                'code', 'ask_broker_id', 'ask_broker_name', 'ask_broker_pos'
            ]
            bid_frame_table = pd.DataFrame(bid_content, columns=bid_list)
            ask_frame_table = pd.DataFrame(ask_content, columns=ask_list)

            return RET_OK, stock_code, [bid_frame_table, ask_frame_table]


class HeartBeatHandlerBase(RspHandlerBase):
    """Base class for handling Heart Beat"""

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, msg, time = HeartBeatPush.unpack_rsp(rsp_pb)

        return ret_code, time


class SysNotifyHandlerBase(RspHandlerBase):
    """sys notify"""
    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, content = SysNotifyPush.unpack_rsp(rsp_pb)

        return ret_code, content


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

