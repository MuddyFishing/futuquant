# -*- coding: utf-8 -*-

import sys
import json
import traceback
from datetime import datetime
from .constant import *


def check_date_str_format(s):
    """Check the format of date string"""
    try:
        _ = datetime.strptime(s, "%Y-%m-%d")
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

    error_code = int(rsp['ErrCode'])

    if error_code != 0:
        error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
        return RET_ERROR, error_str, None

    if 'RetData' not in rsp:
        error_str = ERROR_STR_PREFIX + 'No ret data found in client rsp. Response: %s' % rsp
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
    if 0 <= split_loc < len(stock_str) - 1 and stock_str[0:split_loc] in MKT_MAP:
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


def binary2str(b):
    """
    Transfer binary to string
    :param b: binary content to be transformed to string
    :return: string
    """
    return b.decode('utf-8')


def is_str(obj):
    if sys.version_info.major == 3:
        return isinstance(obj, str) or isinstance(obj, bytes)
    else:
        return isinstance(obj, basestring)


def price_to_str_int1000(price):
    return str(int(round(float(price) * 1000, 0))) if str(price) is not '' else ''


# 1000*int price to float val
def int1000_price_to_float(price):
    return round(float(price) / 1000.0, 3) if str(price) is not '' else float(0)


# 10^9 int price to float val
def int10_9_price_to_float(price):
    return round(float(price) / float(10**9), 3) if str(price) is not '' else float(0)


# list 参数除重及规整
def unique_and_normalize_list(lst):
    ret = []
    if not lst:
        return ret
    tmp = lst if isinstance(lst, list) else [lst]
    [ret.append(x) for x in tmp if x not in ret]
    return ret


