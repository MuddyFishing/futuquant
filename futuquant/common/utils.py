# -*- coding: utf-8 -*-

import hashlib
import json
import os
import sys
import socket
import traceback
from datetime import datetime
from struct import calcsize
from google.protobuf.json_format import MessageToJson

from futuquant.common.constant import *
from futuquant.common.pbjson import json2pb
from futuquant.common.ft_logger import logger


def set_proto_fmt(proto_fmt):
    """Set communication protocol format, json ans protobuf supported"""
    os.environ['FT_PROTO_FMT'] = str(proto_fmt)

def set_trd_accID(accID):
    """set the trade account ID"""
    os.environ['FT_TRD_ACCID'] = str(accID)

def set_trd_market(market_code):
    """set the trade account ID"""
    os.environ['FT_TRD_MARKET'] = str(market_code)

def set_user_id(user_id):
    os.environ['FT_USER_ID'] = str(user_id)

def get_user_id():
    return int(os.environ['FT_USER_ID'])

def get_proto_fmt():
    return int(os.environ['FT_PROTO_FMT'])

def get_trd_accID():
    return int(os.environ['FT_TRD_ACCID'])

def get_trd_market():
    return int(os.environ['FT_TRD_MARKET'])

def get_client_ver():
    return 300

def get_client_id():
    return "PyNormal"

def get_message_head_len():
    return calcsize(MESSAGE_HEAD_FMT)

def check_date_str_format(s):
    """Check the format of date string"""
    try:
        if ":" not in s:
            _ = datetime.strptime(s, "%Y-%m-%d")
        else:
            _ = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return RET_OK, None
    except ValueError:
        traceback.print_exc()
        err = sys.exc_info()[1]
        error_str = ERROR_STR_PREFIX + str(err)
        return RET_ERROR, error_str


def extract_pls_rsp(rsp_str):
    """Extract the response of PLS"""
    try:
        rsp = json.loads(rsp_str)
    except ValueError:
        traceback.print_exc()
        err = sys.exc_info()[1]
        err_str = ERROR_STR_PREFIX + str(err)
        return RET_ERROR, err_str, None

    error_code = int(rsp['retType'])

    if error_code != 1:
        error_str = ERROR_STR_PREFIX + rsp['retMsg']
        return RET_ERROR, error_str, None

    return RET_OK, "", rsp


def normalize_date_format(date_str):
    """normalize the format of data"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    ret = date_obj.strftime("%Y-%m-%d")
    return ret


def split_stock_str(stock_str_param):
    """split the stock string"""
    stock_str = str(stock_str_param)

    split_loc = stock_str.find(".")
    '''do not use the built-in split function in python.
    The built-in function cannot handle some stock strings correctly.
    for instance, US..DJI, where the dot . itself is a part of original code'''
    if 0 <= split_loc < len(
            stock_str) - 1 and stock_str[0:split_loc] in MKT_MAP:
        market_str = stock_str[0:split_loc]
        market_code = MKT_MAP[market_str]
        partial_stock_str = stock_str[split_loc + 1:]
        return RET_OK, (market_code, partial_stock_str)

    else:

        error_str = ERROR_STR_PREFIX + "format of %s is wrong. (US.AAPL, HK.00700, SZ.000001)" % stock_str
        return RET_ERROR, error_str


def merge_stock_str(market, partial_stock_str):
    """
    Merge the string of stocks
    :param market: market code
    :param partial_stock_str: original stock code string. i.e. "AAPL","00700", "000001"
    :return: unified representation of a stock code. i.e. "US.AAPL", "HK.00700", "SZ.000001"

    """

    market_str = TRADE.REV_MKT_MAP[market]
    stock_str = '.'.join([market_str, partial_stock_str])
    return stock_str


def str2binary(s):
    """
    Transfer string to binary
    :param s: string content to be transformed to binary
    :return: binary
    """
    return s.encode('utf-8')


class ProtobufMap(dict):
    created_protobuf_map = {}

    def __init__(self):
        from futuquant.common.pb.InitConnect_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.InitConnect] = Response()

        from futuquant.common.pb.Qot_Sub_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_Sub] = Response()

        from futuquant.common.pb.Qot_ReqSubInfo_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqSubInfo] = Response()

        from futuquant.common.pb.Qot_ReqStockBasic_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqStockBasic] = Response()

        from futuquant.common.pb.Qot_PushStockBasic_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_PushStockBasic] = Response()

        from futuquant.common.pb.Qot_ReqTradeDate_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqTradeDate] = Response()

        from futuquant.common.pb.Qot_RegQotPush_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_RegQotPush] = Response()

        from futuquant.common.pb.Qot_ReqStockList_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqStockList] = Response()

        from futuquant.common.pb.Qot_ReqStockSnapshot_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqStockSnapshot] = Response()

        from futuquant.common.pb.Qot_ReqPlateSet_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqPlateSet] = Response()

        from futuquant.common.pb.Qot_ReqPlateStock_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqPlateStock] = Response()

        from futuquant.common.pb.Qot_ReqBroker_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqBroker] = Response()

        from futuquant.common.pb.Qot_ReqOrderBook_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqOrderBook] = Response()

        from futuquant.common.pb.Qot_ReqKL_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqKL] = Response()

        from futuquant.common.pb.Trd_UnlockTrade_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_UnlockTrade] = Response()

        from futuquant.common.pb.Qot_ReqRT_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqRT] = Response()

        from futuquant.common.pb.PushHeartBeat_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.PushHeartBeat] = Response()

        from futuquant.common.pb.Trd_UnlockTrade_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_UnlockTrade] = Response()

        from futuquant.common.pb.Qot_ReqRehab_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqRehab] = Response()

        from futuquant.common.pb.Qot_ReqSuspend_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqSuspend] = Response()

        from futuquant.common.pb.Qot_ReqTicker_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqTicker] = Response()

        from futuquant.common.pb.Trd_GetAccList_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_GetAccList] = Response()

        from futuquant.common.pb.Trd_GetFunds_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_GetFunds] = Response()

        from futuquant.common.pb.Trd_GetPositionList_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_GetPositionList] = Response()

        from futuquant.common.pb.Trd_GetOrderList_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_GetOrderList] = Response()

        from futuquant.common.pb.Trd_PlaceOrder_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_PlaceOrder] = Response()

        from futuquant.common.pb.Trd_UpdateOrder_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_UpdateOrder] = Response()

        from  futuquant.common.pb.Trd_UpdateOrderFill_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_UpdateOrderFill] = Response()

        from futuquant.common.pb.Trd_GetOrderFillList_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_GetOrderFillList] = Response()

        from futuquant.common.pb.Trd_GetHistoryOrderList_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_GetHistoryOrderList] = Response()

        from futuquant.common.pb.Trd_GetHistoryOrderFillList_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Trd_GetHistoryOrderFillList] = Response()

        from futuquant.common.pb.Qot_HistoryKL_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqHistoryKL] = Response()

        from futuquant.common.pb.Qot_HistoryKLPoints_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.Qot_ReqHistoryKLPoints] = Response()

        from futuquant.common.pb.GlobalState_pb2 import Response
        ProtobufMap.created_protobuf_map[ProtoId.GlobalState] = Response()

    def __getitem__(self, key):
        return ProtobufMap.created_protobuf_map[key] if key in ProtobufMap.created_protobuf_map else None

pb_map = ProtobufMap()

def md5_transform(raw_str):
    h1 = hashlib.md5()
    h1.update(raw_str.encode(encoding='utf-8'))
    return h1.hexdigest()


def binary2str(b, proto_id, proto_fmt_type):
    """
    Transfer binary to string
    :param b: binary content to be transformed to string
    :return: string
    """
    if proto_fmt_type == ProtoFMT.Json:
        return b.decode('utf-8')
    elif proto_fmt_type == ProtoFMT.Protobuf:
        rsp = pb_map[proto_id]
        rsp.ParseFromString(b)
        return MessageToJson(rsp)
    else:
        raise Exception("binary2str: unknown proto format.")

def binary2pb(b, proto_id, proto_fmt_type):
    """
    Transfer binary to pb message
    :param b: binary content to be transformed to pb message
    :return: pb message
    """
    rsp = pb_map[proto_id]
    if rsp is None:
        return None
    if proto_fmt_type == ProtoFMT.Json:
        return json2pb(type(rsp), b.decode('utf-8'))
    elif proto_fmt_type == ProtoFMT.Protobuf:
        rsp.Clear()
        # logger.debug((proto_id))
        rsp.ParseFromString(b)
        return rsp
    else:
        raise Exception("binary2str: unknown proto format.")

def is_str(obj):
    if sys.version_info.major == 3:
        return isinstance(obj, str) or isinstance(obj, bytes)
    else:
        return isinstance(obj, basestring)


def price_to_str_int1000(price):
    return str(int(round(float(price) * 1000,
                         0))) if str(price) is not '' else ''


# 1000*int price to float val
def int1000_price_to_float(price):
    return round(float(price) / 1000.0,
                 3) if str(price) is not '' else float(0)


# 10^9 int price to float val
def int10_9_price_to_float(price):
    return round(float(price) / float(10**9),
                 3) if str(price) is not '' else float(0)


# list 参数除重及规整
def unique_and_normalize_list(lst):
    ret = []
    if not lst:
        return ret
    tmp = lst if isinstance(lst, list) else [lst]
    [ret.append(x) for x in tmp if x not in ret]
    return ret
