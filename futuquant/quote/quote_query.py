# -*- coding: utf-8 -*-
"""
    Quote query
"""
import json
import sys
import struct
from datetime import timedelta
from google.protobuf.json_format import MessageToJson
from futuquant.common.constant import *
from futuquant.common.utils import *
from futuquant.common.pb.Common_pb2 import RetType


def pack_pb_req(pb_req, proto_id):
    proto_fmt = get_proto_fmt()
    if proto_fmt == ProtoFMT.Json:
        req_json = MessageToJson(pb_req)
        req = _joint_head(proto_id, proto_fmt, len(req_json),
                          req_json.encode())
        return RET_OK, "", req
    elif proto_fmt == ProtoFMT.Protobuf:
        req = _joint_head(proto_id, proto_fmt, pb_req.ByteSize(), pb_req)
        return RET_OK, "", req
    else:
        error_str = ERROR_STR_PREFIX + 'unknown protocol format, %d' % proto_fmt
        return RET_ERROR, error_str, None


def _joint_head(proto_id, proto_fmt_type, body_len, str_body, proto_ver=0):
    if proto_fmt_type == ProtoFMT.Protobuf:
        str_body = str_body.SerializeToString()
    fmt = "%s%ds" % (MESSAGE_HEAD_FMT, body_len)
    #serial_no is useless for now, set to 1
    serial_no = 1
    bin_head = struct.pack(fmt, b'F', b'T', proto_id, proto_fmt_type,
                           proto_ver, serial_no, body_len, 0, 0, 0, 0, 0, 0, 0,
                           0, str_body)
    return bin_head


def parse_head(head_bytes):
    head_dict = {}
    head_dict['head_1'], head_dict['head_2'], head_dict['proto_id'], \
    head_dict['proto_fmt_type'], head_dict['proto_ver'], \
    head_dict['serial_no'], head_dict['body_len'], head_dict['reserved_1'], \
    head_dict['reserved_2'], head_dict['reserved_3'], head_dict['reserved_4'], \
    head_dict['reserved_5'], head_dict['reserved_6'], head_dict['reserved_7'], \
    head_dict['reserved_8'] = struct.unpack(MESSAGE_HEAD_FMT, head_bytes)
    return head_dict


class InitConnect:
    """
    A InitConnect request must be sent first
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, client_ver, client_id, recv_notify=False):
        """
        Send a init connection request to establish the connection btw gateway and client
        :param client_ver:
        :param client_id:
        :param recv_notify:
         :return:  json string for request
        """
        from futuquant.common.pb.InitConnect_pb2 import Request
        req = Request()
        req.c2s.clientVer = client_ver
        req.c2s.clientID = client_id
        req.c2s.recvNotify = recv_notify
        return pack_pb_req(req, ProtoId.InitConnect)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Unpack the init connect response"""
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        return RET_OK, "", rsp_pb.s2c.serverVer


class TradeDayQuery:
    """
    Query Conversion for getting trading days.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, start_date=None, end_date=None):
        """
        Convert from user request for trading days to PLS request
        :param market:
        :param start_date:
        :param end_date:
        :return:  json string for request

        Example:

        ret,msg,content =  TradeDayQuery.pack_req("US", "2017-01-01", "2017-01-18")

        ret: 0
        msg: ""
        content:
        '{"Protocol": "1013", "Version": "1", "ReqParam": {"end_date": "2017-01-18",
        "Market": "2", "start_date": "2017-01-01"}}\r\n'

        """

        # '''Parameter check'''
        if market not in MKT_MAP_NEW:
            error_str = ERROR_STR_PREFIX + " market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None

        if start_date is None:
            today = datetime.today()
            start = today - timedelta(days=365)

            start_date = start.strftime("%Y-%m-%d")
        else:
            ret, msg = check_date_str_format(start_date)
            if ret != RET_OK:
                return ret, msg, None
            start_date = normalize_date_format(start_date)

        if end_date is None:
            today = datetime.today()
            end_date = today.strftime("%Y-%m-%d")
        else:
            ret, msg = check_date_str_format(end_date)
            if ret != RET_OK:
                return ret, msg, None
            end_date = normalize_date_format(end_date)

        # pack to json
        mkt = MKT_MAP_NEW[market]
        from futuquant.common.pb.Qot_ReqTradeDate_pb2 import Request
        req = Request()
        req.c2s.market = mkt
        req.c2s.beginTime = start_date
        req.c2s.endTime = end_date

        return pack_pb_req(req, ProtoId.Qot_ReqTradeDate)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """
        Convert from PLS response to user response
        :return: trading day list

        Example:

        rsp_str : '{"ErrCode":"0","ErrDesc":"","Protocol":"1013","RetData":{"Market":"2",
        "TradeDateArr":["2017-01-17","2017-01-13","2017-01-12","2017-01-11",
        "2017-01-10","2017-01-09","2017-01-06","2017-01-05","2017-01-04",
        "2017-01-03"],"end_date":"2017-01-18","start_date":"2017-01-01"},"Version":"1"}\n\r\n\r\n'

         ret,msg,content = TradeDayQuery.unpack_rsp(rsp_str)

         ret : 0
         msg : ""
         content : ['2017-01-17',
                    '2017-01-13',
                    '2017-01-12',
                    '2017-01-11',
                    '2017-01-10',
                    '2017-01-09',
                    '2017-01-06',
                    '2017-01-05',
                    '2017-01-04',
                    '2017-01-03']

        """
        # response check and unpack response json to objects
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_trading_day_list = rsp_pb.s2c.tradeDate
        # convert to list format that we use
        trading_day_list = [x.time.split()[0] for x in raw_trading_day_list]

        return RET_OK, "", trading_day_list


class StockBasicInfoQuery:
    """
    Query Conversion for getting stock basic information.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, stock_type='STOCK'):
        """
        Convert from user request for trading days to PLS request
        :param market:
        :param stock_type:
        :return: json string for request

        Example:
         ret,msg,content = StockBasicInfoQuery.pack_req("HK_FUTURE","IDX")

         ret : 0
         msg : ""
         content : '{"Protocol": "1014", "Version": "1", "ReqParam": {"Market": "6", "StockType": "6"}}\r\n'
        """
        if market not in MKT_MAP_NEW:
            error_str = ERROR_STR_PREFIX + " market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None

        if stock_type not in SEC_TYPE_MAP:
            error_str = ERROR_STR_PREFIX + " stock_type is %s, which is not valid. (%s)" \
                                           % (stock_type, ",".join([x for x in SEC_TYPE_MAP]))
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_ReqStockList_pb2 import Request
        req = Request()
        req.c2s.market = MKT_MAP_NEW[market]
        req.c2s.secType = SEC_TYPE_MAP[stock_type]

        return pack_pb_req(req, ProtoId.Qot_ReqStockList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """
        Convert from PLS response to user response
        :return: json string for request

        Example:

        rsp_str : '{"ErrCode":"0","ErrDesc":"","Protocol":"1014",
        "RetData":{"BasicInfoArr":
        [{"LotSize":"0","Name":"恒指当月期货","StockCode":"999010","StockID":"999010","StockType":"6"},
        {"LotSize":"0","Name":"恒指下月期货","StockCode":"999011","StockID":"999011","StockType":"6"}],
        "Market":"6"},"Version":"1"}\n\r\n\r\n'


         ret,msg,content = StockBasicInfoQuery.unpack_rsp(rsp_str)

        ret : 0
        msg : ""
        content : [{'code': 'HK_FUTURE.999010',
                    'lot_size': 0,
                    'name': '恒指当月期货',
                    'stock_type': 'IDX'},
                   {'code': 'HK_FUTURE.999011',
                    'lot_size': 0,
                    'name': '恒指下月期货',
                    'stock_type': 'IDX'}]

        """
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_basic_info_list = rsp_pb.s2c.staticInfo

        basic_info_list = [{
            "code":
            merge_stock_str(record.basic.stock.market,
                            record.basic.stock.code),
            "stockid":
            merge_stock_str(record.basic.stock.market,
                            record.basic.stock.code),
            "name":
            record.basic.name,
            "lot_size":
            record.basic.lotSize,
            "stock_type":
            record.basic.secType,
            "stock_child_type":
            record.warrantExData.type,
            "owner_stock_code":
            record.warrantExData.ownerStock,
            "listing_date":
            record.basic.listTime
        } for record in raw_basic_info_list]
        return RET_OK, "", basic_info_list


class MarketSnapshotQuery:
    """
    Query Conversion for getting market snapshot.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """Convert from user request for trading days to PLS request"""
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_ReqStockSnapshot_pb2 import Request
        req = Request()
        for market, code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.market = market
            stock_inst.code = code

        return pack_pb_req(req, ProtoId.Qot_ReqStockSnapshot)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_snapshot_list = rsp_pb.s2c.snapshot
        snapshot_list = []
        for record in raw_snapshot_list:
            snapshot_tmp = {}
            snapshot_tmp['code'] = merge_stock_str(
                int(record.basic.stock.market), record.basic.stock.code)
            snapshot_tmp['update_time'] = record.basic.updateTime
            snapshot_tmp['last_price'] = record.basic.curPrice
            snapshot_tmp['open_price'] = record.basic.openPrice
            snapshot_tmp['high_price'] = record.basic.highPrice
            snapshot_tmp['low_price'] = record.basic.lowPrice
            snapshot_tmp['prev_close_price'] = record.basic.lastClosePrice
            snapshot_tmp['volume'] = record.basic.volume
            snapshot_tmp['turnover'] = record.basic.turnover
            snapshot_tmp['turnover_rate'] = record.basic.turnoverRate
            snapshot_tmp['suspension'] = record.basic.isSuspend
            snapshot_tmp['listing_date'] = record.basic.listTime
            snapshot_tmp['price_spread'] = record.basic.priceSpread
            snapshot_tmp['lot_size'] = record.basic.lotSize
            if record.basic.type == 5:
                snapshot_tmp['wrt_valid'] = True
                snapshot_tmp[
                    'wrt_conversion_ratio'] = record.warrantExData.conversionRate
                snapshot_tmp['wrt_type'] = QUOTE.REV_WRT_TYPE_MAP[
                    record.warrantExData.warrantType]
                snapshot_tmp[
                    'wrt_strike_price'] = record.warrantExData.strikePrice
                snapshot_tmp[
                    'wrt_maturity_date'] = record.warrantExData.maturityTime
                snapshot_tmp[
                    'wrt_end_trade'] = record.warrantExData.endTradeTime
                snapshot_tmp['wrt_code'] = merge_stock_str(
                    record.warrantExData.ownerStock.market,
                    record.warrantExData.ownerStock.code)
                snapshot_tmp[
                    'wrt_recovery_price'] = record.warrantExData.recoveryPrice
                snapshot_tmp[
                    'wrt_street_vol'] = record.warrantExData.streetVolumn
                snapshot_tmp[
                    'wrt_issue_vol'] = record.warrantExData.issueVolumn
                snapshot_tmp[
                    'wrt_street_ratio'] = record.warrantExData.streetRate
                snapshot_tmp['wrt_delta'] = record.warrantExData.delta
                snapshot_tmp[
                    'wrt_implied_volatility'] = record.warrantExData.impliedVolatility
                snapshot_tmp['wrt_premium'] = record.warrantExData.premium
            else:
                snapshot_tmp[
                    'circular_market_val'] = record.equityExData.outstandingMktVal
                snapshot_tmp[
                    'total_market_val'] = record.equityExData.issuedMktVal
                snapshot_tmp[
                    'issued_shares'] = record.equityExData.issuedShares
                snapshot_tmp['net_asset'] = record.equityExData.netAsset
                snapshot_tmp['net_profit'] = record.equityExData.netProfit
                snapshot_tmp[
                    'earning_per_share'] = record.equityExData.earningsPershare
                snapshot_tmp[
                    'outstanding_shares'] = record.equityExData.outstandingShares
                snapshot_tmp[
                    'net_asset_per_share'] = record.equityExData.netAssetPershare
                snapshot_tmp['ey_ratio'] = record.equityExData.eyRate
                snapshot_tmp['pe_ratio'] = record.equityExData.peRate
                snapshot_tmp['pb_ratio'] = record.equityExData.pbRate
            snapshot_list.append(snapshot_tmp)

        return RET_OK, "", snapshot_list


class RtDataQuery:
    """
    Query Conversion for getting stock real-time data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        from futuquant.common.pb.Qot_ReqRT_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code

        return pack_pb_req(req, ProtoId.Qot_ReqRT)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_rt_data_list = rsp_pb.s2c.rt
        stock_code = "test"
        #stock_code = merge_stock_str(
        #int(rsp_data.Market']), rsp_data['StockCode'])
        rt_list = [
            {
                "time": record.time,
                "code": stock_code,
                "data_status": record.isBlank,
                #"opened_mins":
                #record.OpenedMins,
                "cur_price": record.price,
                "last_close": record.lastClosePrice,
                "avg_price": record.avgPrice,
                "turnover": record.turnover,
                "volume": record.volume
            } for record in raw_rt_data_list
        ]

        return RET_OK, "", rt_list


class SubplateQuery:
    """
    Query Conversion for getting sub-plate stock list.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, plate_class):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Qot_ReqPlateSet_pb2 import Request
        req = Request()
        req.c2s.market = MKT_MAP_NEW[market]
        req.c2s.plateSetType = PLATE_CLASS_MAP[plate_class]

        return pack_pb_req(req, ProtoId.Qot_ReqPlateSet)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_plate_list = rsp_pb.s2c.plateInfo

        plate_list = [{
            "code":
            merge_stock_str(record.plate.market, record.plate.code),
            "plate_name":
            record.name,
            "plate_id":
            record.plate.code
        } for record in raw_plate_list]

        return RET_OK, "", plate_list


class PlateStockQuery:
    """
    Query Conversion for getting all the stock list of a given plate.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, plate_code):
        """Convert from user request for trading days to PLS request"""
        ret_code, content = split_stock_str(plate_code)
        if ret_code != RET_OK:
            msg = content
            error_str = ERROR_STR_PREFIX + msg
            return RET_ERROR, error_str, None

        market, stock_code = content
        if market not in QUOTE.REV_MKT_MAP:
            error_str = ERROR_STR_PREFIX + "market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None
        from futuquant.common.pb.Qot_ReqPlateStock_pb2 import Request
        req = Request()
        req.c2s.plate.market = market
        req.c2s.plate.code = stock_code

        return pack_pb_req(req, ProtoId.Qot_ReqPlateStock)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_stock_list = rsp_pb.s2c.staticInfo

        stock_list = []
        for record in raw_stock_list:
            stock_tmp = {}
            stock_tmp['lot_size'] = record.basic.lotSize
            stock_tmp['code'] = merge_stock_str(record.basic.stock.market, record.basic.stock.code)
            stock_tmp['stock_name'] = record.basic.name
            stock_tmp['owner_market'] = merge_stock_str(record.basic.stock.market, record.basic.stock.code)
            stock_tmp['list_time'] = record.basic.listTime
            stock_tmp['stock_child_type'] = QUOTE.REV_WRT_TYPE_MAP[record.basic.secType]
            stock_tmp['stock_tmpe'] = QUOTE.REV_SEC_TYPE_MAP[record.basic.secType]
            stock_list.append(stock_tmp)

        return RET_OK, "", stock_list


class BrokerQueueQuery:
    """
    Query Conversion for getting broker queue information.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str):
        """Convert from user request for trading days to PLS request"""
        ret_code, content = split_stock_str(stock_str)
        if ret_code == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        from futuquant.common.pb.Qot_ReqBroker_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code

        return pack_pb_req(req, ProtoId.Qot_ReqBroker)


    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_broker_bid = rsp_pb.s2c.brokerBid
        logger.debug(raw_broker_bid)
        bid_list = []
        if raw_broker_bid is not None:
            bid_list = [{
                "bid_broker_id":
                record.id,
                "bid_broker_name":
                record.name,
                "bid_broker_pos":
                record.pos,
                "code":
                merge_stock_str(
                    rsp_pb.s2c.stock.market, rsp_pb.s2c.stock.code)
            } for record in raw_broker_bid]

        raw_broker_ask = rsp_pb.s2c.brokerAsk
        ask_list = []
        if raw_broker_ask is not None:
            ask_list = [{
                "ask_broker_id":
                record.id,
                "ask_broker_name":
                record.name,
                "ask_broker_pos":
                record.pos,
                "code":
                merge_stock_str(
                    rsp_pb.s2c.stock.market, rsp_pb.s2c.stock.code)
            } for record in raw_broker_ask]

        return RET_OK, bid_list, ask_list


class HistoryKlineQuery:
    """
    Query Conversion for getting historic Kline data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str, start_date, end_date, ktype, autype, fields,
                 max_num):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        # check date format
        if start_date is None:
            start_date = datetime.now().strftime('%Y-%m-%d')
        else:
            ret, msg = check_date_str_format(start_date)
            if ret != RET_OK:
                return ret, msg, None
            start_date = normalize_date_format(start_date)

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            ret, msg = check_date_str_format(end_date)
            if ret != RET_OK:
                return ret, msg, None
            end_date = normalize_date_format(end_date)

        # check k line type
        if ktype not in KTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in KTYPE_MAP]))
            return RET_ERROR, error_str, None

        if autype not in AUTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in AUTYPE_MAP]))
            return RET_ERROR, error_str, None

        str_field = ','.join(fields)
        list_req_field = KL_FIELD.get_field_list(str_field)
        if not list_req_field:
            return RET_ERROR, ERROR_STR_PREFIX + "field error", None

        req = {
            "Protocol": "1024",
            "Version": "1",
            "ReqParam": {
                'Market': str(market_code),
                'MaxKLNum': str(max_num),
                'NeedKLData': str(','.join(list_req_field)),
                'StockCode': stock_code,
                'start_date': start_date,
                'end_date': end_date,
                'KLType': str(KTYPE_MAP[ktype]),
                'RehabType': str(AUTYPE_MAP[autype])
            }
        }

        req_str = json.dumps(req) + '\r\n'
        head_info = _joint_head(3000, 1, len(req_str), req_str.encode())
        logger.debug(head_info)
        return RET_OK, "", head_info

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "HistoryKLArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find HistoryKLArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        has_next = False
        next_time = ''
        list_ret = []
        if rsp_data["HistoryKLArr"] is None or len(
                rsp_data["HistoryKLArr"]) == 0:
            return RET_OK, "", (list_ret, has_next, next_time)

        raw_kline_list = rsp_data["HistoryKLArr"]
        stock_code = merge_stock_str(
            int(rsp_data['Market']), rsp_data['StockCode'])

        if 'HasNext' in rsp_data:
            has_next = int(rsp_data['HasNext'])
        if 'NextKLTime' in rsp_data:
            next_time = str(rsp_data['NextKLTime']).split(' ')[0]

        dict_data = {}
        for record in raw_kline_list:
            dict_data['code'] = stock_code
            if 'Time' in record:
                dict_data['time_key'] = record['Time']
            if 'Open' in record:
                dict_data['open'] = int10_9_price_to_float(record['Open'])
            if 'High' in record:
                dict_data['high'] = int10_9_price_to_float(record['High'])
            if 'Low' in record:
                dict_data['low'] = int10_9_price_to_float(record['Low'])
            if 'Close' in record:
                dict_data['close'] = int10_9_price_to_float(record['Close'])
            if 'Volume' in record:
                dict_data['volume'] = record['Volume']
            if 'Turnover' in record:
                dict_data['turnover'] = int1000_price_to_float(
                    record['Turnover'])
            if 'PERatio' in record:
                dict_data['pe_ratio'] = int1000_price_to_float(
                    record['PERatio'])
            if 'TurnoverRate' in record:
                dict_data['turnover_rate'] = int1000_price_to_float(
                    record['TurnoverRate'])
            if 'ChangeRate' in record:
                dict_data['change_rate'] = int1000_price_to_float(
                    record['ChangeRate'])

            list_ret.append(dict_data.copy())

        return RET_OK, "", (list_ret, has_next, next_time)


class ExrightQuery:
    """
    Query Conversion for getting exclude-right information of stock.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """Convert from user request for trading days to PLS request"""
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((str(market_code), stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        req = {
            "Protocol": "1025",
            "Version": "1",
            "ReqParam": {
                'StockArr': [{
                    'Market': stock[0],
                    'StockCode': stock[1]
                } for stock in stock_tuple_list]
            }
        }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "ExRightInfoArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find ExRightInfoArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if rsp_data["ExRightInfoArr"] is None or len(
                rsp_data["ExRightInfoArr"]) == 0:
            return RET_OK, "", []

        get_val = (lambda x, y: float(y[x]) / 100000 if x in y else 0)
        raw_exr_list = rsp_data["ExRightInfoArr"]
        exr_list = [{
            'code':
            merge_stock_str(int(record['Market']), record['StockCode']),
            'ex_div_date':
            record['ExDivDate'],
            'split_ratio':
            get_val('SplitRatio', record),
            'per_cash_div':
            get_val('PerCashDiv', record),
            'per_share_div_ratio':
            get_val('PerShareDivRatio', record),
            'per_share_trans_ratio':
            get_val('PerShareTransRatio', record),
            'allotment_ratio':
            get_val(r'AllotmentRatio', record),
            'allotment_price':
            get_val('AllotmentPrice', record),
            'stk_spo_ratio':
            get_val('StkSpoRatio', record),
            'stk_spo_price':
            get_val('StkSpoPrice', record),
            'forward_adj_factorA':
            get_val('ForwardAdjFactorA', record),
            'forward_adj_factorB':
            get_val('ForwardAdjFactorB', record),
            'backward_adj_factorA':
            get_val('BackwardAdjFactorA', record),
            'backward_adj_factorB':
            get_val('BackwarAdjFactorB', record)
        } for record in raw_exr_list]

        return RET_OK, "", exr_list


class SubscriptionQuery:
    """
    Query Conversion for getting user's subscription information.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_subscribe_req(cls, stock_str, data_type):
        """
        Pack subscribe user's request
        :param stock_str:
        :param data_type:
        :return:
        """
        if not isinstance(stock_str, list):
            stock_str = [stock_str]
        if not isinstance(data_type, list):
            data_type = [data_type]

        stock_tuple_list = []
        failure_tuple_list = []
        for stock_inst in stock_str:
            ret_code, content = split_stock_str(stock_inst)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        for sub_type in data_type:
            if sub_type not in SUBTYPE_MAP:
                subtype_str = ','.join([x for x in SUBTYPE_MAP])
                error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (
                    sub_type, subtype_str)
                return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_Sub_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.code = stock_code
            stock_inst.market = market_code
        for sub_ in data_type:
            req.c2s.subType.append(SUBTYPE_MAP[sub_])
        req.c2s.isSubOrUnSub = True

        return pack_pb_req(req, ProtoId.Qot_Sub)

    @classmethod
    def unpack_subscribe_rsp(cls, rsp_pb):
        """Unpack the subscribed response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, "", None

    @classmethod
    def pack_unsubscribe_req(cls, stock_str, data_type):
        """Pack the un-subscribed request"""
        if not isinstance(stock_str, list):
            stock_str = [stock_str]
        if not isinstance(data_type, list):
            data_type = [data_type]

        stock_tuple_list = []
        failure_tuple_list = []
        for stock_inst in stock_str:
            ret_code, content = split_stock_str(stock_inst)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        for sub_type in data_type:
            if sub_type not in SUBTYPE_MAP:
                subtype_str = ','.join([x for x in SUBTYPE_MAP])
                error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (
                    sub_type, subtype_str)
                return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_Sub_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.code = stock_code
            stock_inst.market = market_code
        for sub_ in data_type:
            req.c2s.subType.append(SUBTYPE_MAP[sub_])
        req.c2s.isSubOrUnSub = False

        return pack_pb_req(req, ProtoId.Qot_Sub)

    @classmethod
    def unpack_unsubscribe_rsp(cls, rsp_pb):
        """Unpack the un-subscribed response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, "", None

    @classmethod
    def pack_subscription_query_req(cls, query):
        """Pack the subscribed query request"""
        from futuquant.common.pb.Qot_ReqSubInfo_pb2 import Request
        req = Request()
        param_map = {0: True, 1: False}
        req.c2s.isReqAllConn = param_map[query]

        return pack_pb_req(req, ProtoId.Qot_ReqSubInfo)

    @classmethod
    def unpack_subscription_query_rsp(cls, rsp_pb):
        """Unpack the subscribed query response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None
        raw_sub_info = rsp_pb.s2c
        result = {}
        result['total_used_quota'] = raw_sub_info.totalUsedQuota
        result['remain_quota'] = raw_sub_info.remainQuota
        result['conn_sub_info'] = []
        for conn_sub_info in raw_sub_info.connSubInfo:
            conn_sub_info_tmp = {}
            conn_sub_info_tmp['used_quota'] = conn_sub_info.usedQuota
            conn_sub_info_tmp['is_own_conn_data'] = conn_sub_info.isOwnConnData
            conn_sub_info_tmp['sub_info'] = []
            for sub_info in conn_sub_info.subInfo:
                sub_info_tmp = {}
                sub_info_tmp['sub_type'] = sub_info.subType
                sub_info_tmp['stock'] = []
                for stock in sub_info.stock:
                    stock_tmp = {}
                    stock_tmp['market'] = stock.market
                    stock_tmp['code'] = stock.code
                    sub_info_tmp['stock'].append(stock_tmp)
                conn_sub_info_tmp['sub_info'].append(sub_info_tmp)
            result['conn_sub_info'].append(conn_sub_info_tmp)

        return RET_OK, "", result

    @classmethod
    def pack_push_req(cls, stock_str, data_type):
        """Pack the push request"""
        if not isinstance(stock_str, list):
            stock_str = [stock_str]
        if not isinstance(data_type, list):
            data_type = [data_type]

        stock_tuple_list = []
        failure_tuple_list = []
        for stock_inst in stock_str:
            ret_code, content = split_stock_str(stock_inst)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        for sub_type in data_type:
            if sub_type not in SUBTYPE_MAP:
                subtype_str = ','.join([x for x in SUBTYPE_MAP])
                error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (
                    sub_type, subtype_str)
                return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_RegQotPush_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.code = stock_code
            stock_inst.market = market_code
        for sub_ in data_type:
            req.c2s.subType.append(SUBTYPE_MAP[sub_])
        req.c2s.isRegOrUnReg = True

        return pack_pb_req(req, ProtoId.Qot_RegQotPush)

    @classmethod
    def pack_unpush_req(cls, stock_str, data_type):
        """Pack the un-pushed request"""
        if not isinstance(stock_str, list):
            stock_str = [stock_str]
        if not isinstance(data_type, list):
            data_type = [data_type]

        stock_tuple_list = []
        failure_tuple_list = []
        for stock_inst in stock_str:
            ret_code, content = split_stock_str(stock_inst)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        for sub_type in data_type:
            if sub_type not in SUBTYPE_MAP:
                subtype_str = ','.join([x for x in SUBTYPE_MAP])
                error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (
                    sub_type, subtype_str)
                return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_RegQotPush_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.code = stock_code
            stock_inst.market = market_code
        for sub_ in data_type:
            req.c2s.subType.append(SUBTYPE_MAP[sub_])
        req.c2s.isRegOrUnReg = False

        return pack_pb_req(req, ProtoId.Qot_RegQotPush)


class StockQuoteQuery:
    """
    Query Conversion for getting stock quote data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """Convert from user request for trading days to PLS request"""
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue
            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_ReqStockBasic_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.market = market_code
            stock_inst.code = stock_code

        return pack_pb_req(req, ProtoId.Qot_ReqStockBasic)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, []
        raw_quote_list = rsp_pb.s2c.stockBasic
        quote_list = [{
            'code':
            merge_stock_str(int(record.stock.market), record.stock.code),
            'data_date':
            record.updateTime.split()[0],
            'data_time':
            record.updateTime.split()[1],
            'last_price':
            int1000_price_to_float(record.curPrice),
            'open_price':
            int1000_price_to_float(record.openPrice),
            'high_price':
            int1000_price_to_float(record.highPrice),
            'low_price':
            int1000_price_to_float(record.lowPrice),
            'prev_close_price':
            int1000_price_to_float(record.lastClosePrice),
            'volume':
            int(record.volume),
            'turnover':
            int1000_price_to_float(record.turnover),
            'turnover_rate':
            int1000_price_to_float(record.turnoverRate),
            'amplitude':
            int1000_price_to_float(record.amplitude),
            'suspension':
            record.isSuspended,
            'listing_date':
            record.listTime.split()[0],
            'price_spread':
            int1000_price_to_float(record.priceSpread)
            if record.HasField('priceSpread') else 0,
        } for record in raw_quote_list]

        return RET_OK, "", quote_list


class TickerQuery:
    """Stick ticker data query class"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str, num=500):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        if isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "num is %s of type %s, and the type shoud be %s" \
                                           % (num, str(type(num)), str(int))
            return RET_ERROR, error_str, None

        if num < 0:
            error_str = ERROR_STR_PREFIX + "num is %s, which is less than 0" % num
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        req = {
            "Protocol": "1012",
            "Version": "1",
            "ReqParam": {
                'Market': str(market_code),
                'StockCode': stock_code,
                "Sequence": str(-1),
                'Num': str(num)
            }
        }

        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "TickerArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find TickerArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_ticker_list = rsp_data["TickerArr"]
        if raw_ticker_list is None or len(raw_ticker_list) == 0:
            return RET_OK, "", []

        stock_code = merge_stock_str(
            int(rsp_data['Market']), rsp_data['StockCode'])
        ticker_list = [{
            "code":
            stock_code,
            "time":
            record['Time'],
            "price":
            int1000_price_to_float(record['Price']),
            "volume":
            record['Volume'],
            "turnover":
            int1000_price_to_float(record['Turnover']),
            "ticker_direction":
            QUOTE.REV_TICKER_DIRECTION[int(record['Direction'])],
            "sequence":
            int(record["Sequence"])
        } for record in raw_ticker_list]
        return RET_OK, "", ticker_list


class CurKlineQuery:
    """Stock Kline data query class"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str, num, ktype='K_DAY', autype='qfq'):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if ktype not in KTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in KTYPE_MAP]))
            return RET_ERROR, error_str, None

        if autype not in AUTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in AUTYPE_MAP]))
            return RET_ERROR, error_str, None

        if isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "num is %s of type %s, which type should be %s" \
                                           % (num, str(type(num)), str(int))
            return RET_ERROR, error_str, None

        if num < 0:
            error_str = ERROR_STR_PREFIX + "num is %s, which is less than 0" % num
            return RET_ERROR, error_str, None
        from futuquant.common.pb.Qot_ReqKL_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code
        req.c2s.rehabType = AUTYPE_MAP[autype]
        req.c2s.reqNum = num
        req.c2s.klType = KTYPE_MAP[ktype]

        return pack_pb_req(req, ProtoId.Qot_ReqKL)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, []


        stock_code = merge_stock_str(
            rsp_pb.s2c.stock.market, rsp_pb.s2c.stock.code)
        raw_kline_list = rsp_pb.s2c.rt
        kline_list = [{
            "code":
            stock_code,
            "time_key":
            record.time,
            "open":
            record.openPrice,
            "high":
            record.highPrice,
            "low":
            record.lowPrice,
            "close":
            record.closePrice,
            "volume":
            record.volume,
            "turnover":
            record.turnover,
            "pe_ratio":
            record.pe,
            "turnover_rate":
            record.turnoverRate
        } for record in raw_kline_list]

        return RET_OK, "", kline_list


class OrderBookQuery:
    """
    Query Conversion for getting stock order book data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        from futuquant.common.pb.Qot_ReqOrderBook_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code
        req.c2s.num = 10

        return pack_pb_req(req, ProtoId.Qot_ReqOrderBook)


    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, []

        raw_order_book_ask = rsp_pb.s2c.orderBookAsk
        raw_order_book_bid = rsp_pb.s2c.orderBookBid

        order_book = {}
        order_book['Bid'] = []
        order_book['Ask'] = []

        for record in raw_order_book_bid:
            order_book['Bid'].append((record.price, record.volume, record.orederCount))
        for record in raw_order_book_ask:
            order_book['Ask'].append((record.price, record.volume, record.orederCount))

        return RET_OK, "", order_book


class SuspensionQuery:
    """
    Query SuspensionQuery.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, codes, start, end):
        """Convert from user request for trading days to PLS request"""
        list_req_stock = []
        for stock_str in codes:
            ret, content = split_stock_str(stock_str)
            if ret == RET_ERROR:
                return RET_ERROR, content, None
            else:
                list_req_stock.append(content)

        for x in [start, end]:
            ret, msg = check_date_str_format(x)
            if ret != RET_OK:
                return ret, msg, None
        from futuquant.common.pb.Qot_ReqSuspend_pb2 import Request
        req = Request()

        req = {
            "Protocol": "1039",
            "Version": "1",
            "ReqParam": {
                'Cookie':
                '10000',
                'StockArr': [{
                    'Market': str(market),
                    'StockCode': code
                } for (market, code) in list_req_stock],
                'start_date':
                start,
                'end_date':
                end
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "StockSuspendArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find StockSuspendArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        ret_susp_list = []
        arr_susp = rsp_data["StockSuspendArr"]
        for susp in arr_susp:
            stock_str = merge_stock_str(int(susp['Market']), susp['StockCode'])
            date_arr = susp['SuspendArr']
            list_date = [x['SuspendTime']
                         for x in date_arr] if date_arr else []
            str_date = ','.join(
                list_date) if list_date and len(list_date) > 0 else ''
            ret_susp_list.append({
                'code': stock_str,
                'suspension_dates': str_date
            })

        return RET_OK, "", ret_susp_list


class GlobalStateQuery:
    """
    Query process "FTNN.exe" global state : market state & logined state
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, state_type=0):
        """
        Convert from user request for trading days to PLS request
        :param state_type: for reserved, no use now !
        :return:  json string for request

        req_str: '{"Protocol":"1029","ReqParam":{"StateType":"0"},"Version":"1"}'
        """
        '''Parameter check'''

        # pack to json
        from futuquant.common.pb.GlobalState_pb2 import Request
        req = Request()
        return pack_pb_req(req, ProtoId.GlobalState)

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """
        Convert from PLS response to user response

        Example:

        rsp_str : '{"ErrCode":"0","ErrDesc":"","Protocol":"1029","RetData":{"Market_HK":"5",
        "Market_HKFuture":"15","Market_SH":"6","Market_SZ":"6","Market_US":"11","Quote_Logined":"1","Trade_Logined":"1"
        },"Version":"1"}\r\n\r\n'

         ret,msg,content = TradeDayQuery.unpack_rsp(rsp_str)

         ret : 0
         msg : ""
         content : {"Market_HK":"5",
                    "Market_HKFuture":"15",
                    "Market_SH":"6",
                    "Market_SZ":"6",
                    "Market_US":"11",
                    "Quote_Logined":"1",
                    "Trade_Logined":"1"
                    "TimeStamp":"1508250058"
                   }

        """
        # response check and unpack response json to objects
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None
        logger.debug(rsp)
        rsp_data = rsp['RetData']

        if 'Version' not in rsp_data:
            rsp_data['Version'] = ''

        return RET_OK, "", rsp_data


class HeartBeatPush:
    """
    HeartBeatPush  per 30 second
    """

    def __init__(self):
        pass

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """
        Convert from PLS response to user response

        """
        # response check and unpack response json to objects
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        return RET_OK, '', int(rsp_data['TimeStamp'])


class MultiPointsHisKLine:
    """
    Query MultiPointsHisKLine
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, codes, dates, fields, ktype, autype, max_num,
                 no_data_mode):
        """Convert from user request for trading days to PLS request"""
        list_req_stock = []
        for stock_str in codes:
            ret, content = split_stock_str(stock_str)
            if ret == RET_ERROR:
                return RET_ERROR, content, None
            else:
                list_req_stock.append(content)

        for x in dates:
            ret, msg = check_date_str_format(x)
            if ret != RET_OK:
                return ret, msg, None

        if len(fields) == 0:
            fields = copy(KL_FIELD.ALL_REAL)
        str_field = ','.join(fields)
        list_req_field = KL_FIELD.get_field_list(str_field)
        if not list_req_field:
            return RET_ERROR, ERROR_STR_PREFIX + "field error", None

        if ktype not in KTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in KTYPE_MAP]))
            return RET_ERROR, error_str, None

        if autype not in AUTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in AUTYPE_MAP]))
            return RET_ERROR, error_str, None

        req = {
            "Protocol": "1038",
            "Version": "1",
            "ReqParam": {
                'Cookie':
                '10000',
                'NoDataMode':
                str(no_data_mode),
                'RehabType':
                str(AUTYPE_MAP[autype]),
                'KLType':
                str(KTYPE_MAP[ktype]),
                'MaxKLNum':
                str(max_num),
                'StockArr': [{
                    'Market': str(market),
                    'StockCode': code
                } for (market, code) in list_req_stock],
                'TimePoints':
                str(','.join(dates)),
                'NeedKLData':
                str(','.join(list_req_field))
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']
        if "StockHistoryKLArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find StockHistoryKLArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None
        has_next = int(rsp_data['HasNext'])

        list_ret = []
        dict_data = {}
        arr_kline = rsp_data["StockHistoryKLArr"]
        for kline in arr_kline:
            stock_str = merge_stock_str(
                int(kline['Market']), kline['StockCode'])
            data_arr = kline['HistoryKLArr']
            for point_data in data_arr:
                dict_data['code'] = stock_str
                dict_data['time_point'] = point_data['TimePoint']
                dict_data['data_valid'] = int(point_data['DataValid'])
                if 'Time' in point_data:
                    dict_data['time_key'] = point_data['Time']
                if 'Open' in point_data:
                    dict_data['open'] = int10_9_price_to_float(
                        point_data['Open'])
                if 'High' in point_data:
                    dict_data['high'] = int10_9_price_to_float(
                        point_data['High'])
                if 'Low' in point_data:
                    dict_data['low'] = int10_9_price_to_float(
                        point_data['Low'])
                if 'Close' in point_data:
                    dict_data['close'] = int10_9_price_to_float(
                        point_data['Close'])
                if 'Volume' in point_data:
                    dict_data['volume'] = point_data['Volume']
                if 'Turnover' in point_data:
                    dict_data['turnover'] = int1000_price_to_float(
                        point_data['Turnover'])
                if 'PERatio' in point_data:
                    dict_data['pe_ratio'] = int1000_price_to_float(
                        point_data['PERatio'])
                if 'TurnoverRate' in point_data:
                    dict_data['turnover_rate'] = int1000_price_to_float(
                        point_data['TurnoverRate'])
                if 'ChangeRate' in point_data:
                    dict_data['change_rate'] = int1000_price_to_float(
                        point_data['ChangeRate'])

                list_ret.append(dict_data.copy())

        return RET_OK, "", (list_ret, has_next)
