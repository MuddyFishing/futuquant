# -*- coding: utf-8 -*-

import json
import os
import sys
import traceback
from datetime import datetime
from struct import calcsize
from google.protobuf.json_format import MessageToJson

from futuquant.common.constant import *


def set_proto_fmt(proto_fmt="Json"):
    """Set communication protocol format, json ans protobuf supported"""
    if proto_fmt.upper() == "JSON":
        os.environ['FT_PROTO_FMT'] = "Json"
    elif proto_fmt.upper() == "PROTOBUF":
        os.environ['FT_PROTO_FMT'] = "Protobuf"
    else:
        error_str = ERROR_STR_PREFIX + "Unknown protocol format, %s" % proto_fmt
        print(error_str)
        #set json as default
        os.environ['FT_PROTO_FMT'] = "Json"


def get_proto_fmt():
    return PROTO_FMT_MAP[os.environ['FT_PROTO_FMT']]


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

    error_code = int(rsp['errCode'])

    if error_code != 0:
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
            stock_str) - 1 and stock_str[0:split_loc] in MKT_MAP_NEW:
        market_str = stock_str[0:split_loc]
        market_code = MKT_MAP_NEW[market_str]
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
        from futuquant.common.pb.Qot_Sub_pb2 import Response
        ProtobufMap.created_protobuf_map[3001] = Response()

        from futuquant.common.pb.Qot_ReqSubInfo_pb2 import Response
        ProtobufMap.created_protobuf_map[3003] = Response()

        from futuquant.common.pb.Qot_ReqStockBasic_pb2 import Response
        ProtobufMap.created_protobuf_map[3004] = Response()


    def __getitem__(self, key):
        return ProtobufMap.created_protobuf_map[key]
pb_map = ProtobufMap()


def binary2str(b, proto_id=0):
    """
    Transfer binary to string
    :param b: binary content to be transformed to string
    :return: string
    """
    if get_proto_fmt() == PROTO_FMT_MAP['Json']:
        return b.decode('utf-8')
    else:
        rsp = pb_map[proto_id]
        rsp.ParseFromString(b)
        return MessageToJson(rsp)


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
