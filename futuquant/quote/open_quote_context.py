# -*- coding: utf-8 -*-
"""
    Market quote and trade context setting
"""

import datetime
from time import sleep

import pandas as pd
from futuquant.common.open_context_base import OpenContextBase
from futuquant.common.constant import *
from futuquant.common.utils import *
from futuquant.quote.quote_query import *


class OpenQuoteContext(OpenContextBase):
    """Class for set context of stock quote"""

    def __init__(self, host='127.0.0.1', port=11111, proto_fmt = ProtoFMT.Json):
        self._ctx_subscribe = set()
        super(OpenQuoteContext, self).__init__(host, port, True, True)
        set_proto_fmt(proto_fmt)

    def init_connect(self,
                     client_ver=get_client_ver(),
                     client_id=get_client_id(),
                     recv_notify=False):
        if client_ver is None or not isinstance(client_ver, int):
            error_str = ERROR_STR_PREFIX + "the type of client_ver param is wrong"
            return RET_ERROR, error_str

        if client_id is None or not isinstance(client_id, str):
            error_str = ERROR_STR_PREFIX + "the type of client_id param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            InitConnect.pack_req, InitConnect.unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'client_ver': client_ver,
            'client_id': client_id,
            "recv_notify": recv_notify
        }
        ret_code, msg, content = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        return RET_OK, content

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

        query_processor = self._get_sync_query_processor(
            TradeDayQuery.pack_req, TradeDayQuery.unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'market': market,
            'start_date': start_date,
            "end_date": end_date
        }
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

        query_processor = self._get_sync_query_processor(
            StockBasicInfoQuery.pack_req, StockBasicInfoQuery.unpack_rsp)
        kargs = {"market": market, 'stock_type': stock_type}

        ret_code, msg, basic_info_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code', 'name', 'lot_size', 'stock_type', 'stock_child_type',
            "owner_stock_code", "listing_date", "stockid"
        ]

        basic_info_table = pd.DataFrame(basic_info_list, columns=col_list)

        return RET_OK, basic_info_table

    def get_multiple_history_kline(self,
                                   codelist,
                                   start=None,
                                   end=None,
                                   ktype='K_DAY',
                                   autype='qfq'):
        if is_str(codelist):
            codelist = codelist.split(',')
        elif isinstance(codelist, list):
            pass
        else:
            raise Exception(
                "code list must be like ['HK.00001', 'HK.00700'] or 'HK.00001,HK.00700'"
            )
        result = []
        for code in codelist:
            ret, data = self.get_history_kline(code, start, end, ktype, autype)
            if ret != RET_OK:
                raise Exception('get history kline error {},{},{},{}'.format(
                    code, start, end, ktype))
            result.append(data)
        return 0, result

    def get_history_kline(self,
                          code,
                          start=None,
                          end=None,
                          ktype='K_DAY',
                          autype='qfq',
                          fields=[KL_FIELD.ALL]):
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
            kargs = {
                "stock_str": code,
                "start_date": req_start,
                "end_date": end,
                "ktype": ktype,
                "autype": autype,
                "fields": req_fields,
                "max_num": max_kl_num
            }
            query_processor = self._get_sync_query_processor(
                HistoryKlineQuery.pack_req, HistoryKlineQuery.unpack_rsp)
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

        query_processor = self._get_sync_query_processor(
            ExrightQuery.pack_req, ExrightQuery.unpack_rsp)
        kargs = {"stock_list": code_list}
        ret_code, msg, exr_record = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code', 'ex_div_date', 'split_ratio', 'per_cash_div',
            'per_share_div_ratio', 'per_share_trans_ratio', 'allotment_ratio',
            'allotment_price', 'stk_spo_ratio', 'stk_spo_price',
            'forward_adj_factorA', 'forward_adj_factorB',
            'backward_adj_factorA', 'backward_adj_factorB'
        ]

        exr_frame_table = pd.DataFrame(exr_record, columns=col_list)

        return RET_OK, exr_frame_table

    def get_market_snapshot(self, code_list):
        """get teh market snapshot"""
        code_list = unique_and_normalize_list(code_list)
        if not code_list:
            error_str = ERROR_STR_PREFIX + "the type of code param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            MarketSnapshotQuery.pack_req, MarketSnapshotQuery.unpack_rsp)
        kargs = {"stock_list": code_list}

        ret_code, msg, snapshot_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code',
            'update_time',
            'last_price',
            'open_price',
            'high_price',
            'low_price',
            'prev_close_price',
            'volume',
            'turnover',
            'turnover_rate',
            'suspension',
            'listing_date',
            'circular_market_val',
            'total_market_val',
            'wrt_valid',
            'wrt_conversion_ratio',
            'wrt_type',
            'wrt_strike_price',
            'wrt_maturity_date',
            'wrt_end_trade',
            'wrt_code',
            'wrt_recovery_price',
            'wrt_street_vol',
            'wrt_issue_vol',
            'wrt_street_ratio',
            'wrt_delta',
            'wrt_implied_volatility',
            'wrt_premium',
            'lot_size',
            # 2017.11.6 add
            'issued_shares',
            'net_asset',
            'net_profit',
            'earning_per_share',
            'outstanding_shares',
            'net_asset_per_share',
            'ey_ratio',
            'pe_ratio',
            'pb_ratio',
            # 2017.1.25 add
            'price_spread',
        ]

        snapshot_frame_table = pd.DataFrame(snapshot_list, columns=col_list)

        return RET_OK, snapshot_frame_table

    def get_rt_data(self, code):
        """get real-time data"""
        if code is None or is_str(code) is False:
            error_str = ERROR_STR_PREFIX + "the type of param in code is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            RtDataQuery.pack_req, RtDataQuery.unpack_rsp)
        kargs = {"stock_str": code}

        ret_code, msg, rt_data_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code', 'time', 'data_status', 'opened_mins', 'cur_price',
            'last_close', 'avg_price', 'volume', 'turnover'
        ]

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

        query_processor = self._get_sync_query_processor(
            SubplateQuery.pack_req, SubplateQuery.unpack_rsp)
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

        query_processor = self._get_sync_query_processor(
            PlateStockQuery.pack_req, PlateStockQuery.unpack_rsp)
        kargs = {"plate_code": plate_code}

        ret_code, msg, plate_stock_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code', 'lot_size', 'stock_name', 'owner_market',
            'stock_child_type', 'stock_type'
        ]

        plate_stock_table = pd.DataFrame(plate_stock_list, columns=col_list)

        return RET_OK, plate_stock_table

    def get_broker_queue(self, code):
        """get teh queue of the broker"""
        if code is None or is_str(code) is False:
            error_str = ERROR_STR_PREFIX + "the type of param in code is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            BrokerQueueQuery.pack_req, BrokerQueueQuery.unpack_rsp)
        kargs = {"stock_str": code}

        ret_code, bid_list, ask_list = query_processor(**kargs)

        if ret_code == RET_ERROR:
            return ret_code, ERROR_STR_PREFIX, EMPTY_STRING

        col_bid_list = [
            'code', 'bid_broker_id', 'bid_broker_name', 'bid_broker_pos'
        ]
        col_ask_list = [
            'code', 'ask_broker_id', 'ask_broker_name', 'ask_broker_pos'
        ]

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
        query_processor = self._get_sync_query_processor(
            SubscriptionQuery.pack_subscribe_req,
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
            ret_code, msg, push_req_str = SubscriptionQuery.pack_push_req(
                stock_code, data_type)

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

        query_processor = self._get_sync_query_processor(
            SubscriptionQuery.pack_unsubscribe_req,
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
            ret_code, msg, unpush_req_str = SubscriptionQuery.pack_unpush_req(
                stock_code, data_type)

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
        query_processor = self._get_sync_query_processor(
            SubscriptionQuery.pack_subscription_query_req,
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

        query_processor = self._get_sync_query_processor(
            StockQuoteQuery.pack_req,
            StockQuoteQuery.unpack_rsp,
        )
        kargs = {"stock_list": code_list}

        ret_code, msg, quote_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code', 'data_date', 'data_time', 'last_price', 'open_price',
            'high_price', 'low_price', 'prev_close_price', 'volume',
            'turnover', 'turnover_rate', 'amplitude', 'suspension',
            'listing_date', 'price_spread'
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

        query_processor = self._get_sync_query_processor(
            TickerQuery.pack_req,
            TickerQuery.unpack_rsp,
        )
        kargs = {"stock_str": code, "num": num}
        ret_code, msg, ticker_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code', 'time', 'price', 'volume', 'turnover', "ticker_direction",
            'sequence'
        ]
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

        query_processor = self._get_sync_query_processor(
            CurKlineQuery.pack_req,
            CurKlineQuery.unpack_rsp,
        )

        kargs = {
            "stock_str": code,
            "num": num,
            "ktype": ktype,
            "autype": autype
        }
        ret_code, msg, kline_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg

        col_list = [
            'code', 'time_key', 'open', 'close', 'high', 'low', 'volume',
            'turnover', 'pe_ratio', 'turnover_rate'
        ]
        kline_frame_table = pd.DataFrame(kline_list, columns=col_list)

        return RET_OK, kline_frame_table

    def get_order_book(self, code):
        """get the order book data"""
        if code is None or is_str(code) is False:
            error_str = ERROR_STR_PREFIX + "the type of code param is wrong"
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            OrderBookQuery.pack_req,
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

        query_processor = self._get_sync_query_processor(
            SuspensionQuery.pack_req,
            SuspensionQuery.unpack_rsp,
        )

        kargs = {"codes": req_codes, "start": str(start), "end": str(end)}
        ret_code, msg, susp_list = query_processor(**kargs)
        if ret_code == RET_ERROR:
            return ret_code, msg
        col_list = ['code', 'suspension_dates']
        pd_frame = pd.DataFrame(susp_list, columns=col_list)

        return RET_OK, pd_frame

    def get_multi_points_history_kline(self,
                                       codes,
                                       dates,
                                       fields,
                                       ktype='K_DAY',
                                       autype='qfq',
                                       no_data_mode=KL_NO_DATA_MODE_FORWARD):
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

        query_processor = self._get_sync_query_processor(
            MultiPointsHisKLine.pack_req, MultiPointsHisKLine.unpack_rsp)
        all_num = max(1, len(req_dates) * len(req_codes))
        one_num = max(1, len(req_dates))
        max_data_num = 500
        max_kl_num = all_num if all_num <= max_data_num else int(
            max_data_num / one_num) * one_num
        if 0 == max_kl_num:
            error_str = ERROR_STR_PREFIX + "too much data to req"
            return RET_ERROR, error_str

        data_finish = False
        list_ret = []
        # 循环请求数据，避免一次性取太多超时
        while not data_finish:
            print('get_multi_points_history_kline - wait ... %s' %
                  datetime.now())
            kargs = {
                "codes": req_codes,
                "dates": req_dates,
                "fields": req_fields,
                "ktype": ktype,
                "autype": autype,
                "max_num": max_kl_num,
                "no_data_mode": no_data_mode
            }
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
