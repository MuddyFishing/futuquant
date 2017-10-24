# -*- coding: utf-8 -*-
"""
    Trade query
"""
import sys
import json
import traceback
from datetime import datetime
from .constant import *
from .utils import str_price1000


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


def split_stock_str(stock_str):
    """split the stock string"""
    if isinstance(stock_str, str) is False:
        error_str = ERROR_STR_PREFIX + "value of stock_str is %s of type %s, and type %s is expected" \
                                       % (stock_str, type(stock_str), str(str))
        return RET_ERROR, error_str

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


def is_HKTrade_order_status_finish(status):
    val = int(status)
    if val == 3 or val == 5 or val == 6 or val == 7:
        return True
    return False

def is_USTrade_order_status_finish(status):
    val = int(status)
    if val == 3 or val == 5 or val == 6 or val == 7:
        return True
    return False

class UnlockTrade:
    """Unlock trade limitation lock"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, cookie, password):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "6006",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "Password": password,
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

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        unlock_list = [{"svr_result": rsp_data["SvrResult"]}]

        return RET_OK, "", unlock_list


class PlaceOrder:
    """Palce order class"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype, orderside, ordertype, price, qty, strcode):
        """Convert from user request for trading days to PLS request"""
        if int(orderside) < 0 or int(orderside) > 1:
            error_str = ERROR_STR_PREFIX + "parameter orderside is wrong"
            return RET_ERROR, error_str, None

        if int(ordertype) is not 0 and int(ordertype) is not 1 and int(ordertype) is not 3:
            error_str = ERROR_STR_PREFIX + "parameter ordertype is wrong"
            return RET_ERROR, error_str, None

        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "6003",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "OrderSide": orderside,
                            "OrderType": ordertype,
                            "Price": str_price1000(price),
                            "Qty": qty,
                            "StockCode": strcode
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        place_order_list = [{'envtype': rsp_data['EnvType'],
                             'orderid': rsp_data['OrderID']
                             }]

        return RET_OK, "", place_order_list

    @classmethod
    def us_pack_req(cls, cookie, envtype, orderside, ordertype, price, qty, strcode):
        """Convert from user request for trading days to PLS request"""
        if int(orderside) < 0 or int(orderside) > 1:
            error_str = ERROR_STR_PREFIX + "parameter orderside is wrong"
            return RET_ERROR, error_str, None

        if int(ordertype) is not 1 and int(ordertype) is not 2 \
                and int(ordertype) is not 51 and int(ordertype) is not 52:
            error_str = ERROR_STR_PREFIX + "parameter ordertype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "7003",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "OrderSide": orderside,
                            "OrderType": ordertype,
                            "Price": str_price1000(price),
                            "Qty": qty,
                            "StockCode": strcode
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        place_order_list = [{'envtype': rsp_data['EnvType'],
                             'orderid': rsp_data['OrderID']
                             }]

        return RET_OK, "", place_order_list


class SetOrderStatus:
    """calss for setting status of order"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype, localid, orderid, status):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        if int(status) < 0 or int(status) > 3:
            error_str = ERROR_STR_PREFIX + "parameter status is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "6004",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "LocalID": localid,
                            "OrderID": orderid,
                            "SetOrderStatus": status,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        set_order_list = [{'envtype': rsp_data['EnvType'],
                           'orderID': rsp_data['OrderID']
                           }]

        return RET_OK, "", set_order_list

    @classmethod
    def us_pack_req(cls, cookie, envtype, localid, orderid, status):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "7004",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "LocalID": localid,
                            "OrderID": orderid,
                            "SetOrderStatus": status,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        set_order_list = [{'envtype': rsp_data['EnvType'],
                           'orderID': rsp_data['OrderID']
                           }]

        return RET_OK, "", set_order_list


class ChangeOrder:
    """Class for changing order"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype, localid, orderid, price, qty):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "6005",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "LocalID": localid,
                            "OrderID": orderid,
                            "Price": str_price1000(price),
                            "Qty": qty,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        change_order_list = [{'envtype': rsp_data['EnvType'],
                              'orderID': rsp_data['OrderID']
                              }]

        return RET_OK, "", change_order_list

    @classmethod
    def us_pack_req(cls, cookie, envtype, localid, orderid, price, qty):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "7005",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "LocalID": localid,
                            "OrderID": orderid,
                            "Price": str_price1000(price),
                            "Qty": qty,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        change_order_list = [{'envtype': rsp_data['EnvType'],
                              'orderID': rsp_data['OrderID']
                              }]

        return RET_OK, "", change_order_list


class AccInfoQuery:
    """Class for querying information of account"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "6007",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'Cookie' not in rsp_data or 'EnvType' not in rsp_data:
            return RET_ERROR, msg, None

        if 'Power' not in rsp_data or 'ZCJZ' not in rsp_data or 'ZQSZ' not in rsp_data or 'XJJY' not in rsp_data:
            return RET_ERROR, msg, None

        if 'KQXJ' not in rsp_data or 'DJZJ' not in rsp_data or 'ZSJE' not in rsp_data or 'ZGJDE' not in rsp_data:
            return RET_ERROR, msg, None

        if 'YYJDE' not in rsp_data or 'GPBZJ' not in rsp_data:
            return RET_ERROR, msg, None

        accinfo_list = [{'Power': float(rsp_data['Power']) / 1000, 'ZCJZ': float(rsp_data['ZCJZ']) / 1000,
                         'ZQSZ': float(rsp_data['ZQSZ']) / 1000, 'XJJY': float(rsp_data['XJJY']) / 1000,
                         'KQXJ': float(rsp_data['KQXJ']) / 1000, 'DJZJ': float(rsp_data['DJZJ']) / 1000,
                         'ZSJE': float(rsp_data['ZSJE']) / 1000, 'ZGJDE': float(rsp_data['ZGJDE']) / 1000,
                         'YYJDE': float(rsp_data['YYJDE']) / 1000, 'GPBZJ': float(rsp_data['GPBZJ']) / 1000
                         }]

        return RET_OK, "", accinfo_list

    @classmethod
    def us_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "7007",
               "Version": "1",
               "ReqParam": {"Cookie": str(cookie),
                            "EnvType": str(envtype),
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            return RET_ERROR, msg, None

        if 'Power' not in rsp_data or 'ZCJZ' not in rsp_data or 'ZQSZ' not in rsp_data or 'XJJY' not in rsp_data:
            return RET_ERROR, msg, None

        if 'KQXJ' not in rsp_data or 'DJZJ' not in rsp_data or 'ZSJE' not in rsp_data or 'ZGJDE' not in rsp_data:
            return RET_ERROR, msg, None

        if 'YYJDE' not in rsp_data or 'GPBZJ' not in rsp_data:
            return RET_ERROR, msg, None

        accinfo_list = [{'Power': float(rsp_data['Power']) / 1000, 'ZCJZ': float(rsp_data['ZCJZ']) / 1000,
                         'ZQSZ': float(rsp_data['ZQSZ']) / 1000, 'XJJY': float(rsp_data['XJJY']) / 1000,
                         'KQXJ': float(rsp_data['KQXJ']) / 1000, 'DJZJ': float(rsp_data['DJZJ']) / 1000,
                         'ZSJE': float(rsp_data['ZSJE']) / 1000, 'ZGJDE': float(rsp_data['ZGJDE']) / 1000,
                         'YYJDE': float(rsp_data['YYJDE']) / 1000, 'GPBZJ': float(rsp_data['GPBZJ']) / 1000
                         }]

        return RET_OK, "", accinfo_list


class OrderListQuery:
    """Class for querying list queue"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, orderid, statusfilter, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "6008",
               "Version": "1",
               "ReqParam": {"Cookie": str(cookie),
                            "EnvType": str(envtype),
                            "OrderID": str(orderid),
                            "StatusFilterStr": str(statusfilter),
                            "StockCode": strcode,
                            "start_time": start,
                            "end_time": end,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if "HKOrderArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find HKOrderArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_list = rsp_data["HKOrderArr"]
        if raw_order_list is None or len(raw_order_list) == 0:
            return RET_OK, "", []

        order_list = [{"code": merge_stock_str(1, order['StockCode']),
                       "stock_name": order["StockName"],
                       "dealt_avg_price": float(order['DealtAvgPrice']) / 1000,
                       "dealt_qty": order['DealtQty'],
                       "qty": order['Qty'],
                       "orderid": order['OrderID'],
                       "order_type": order['OrderType'],
                       "order_side": order['OrderSide'],
                       "price": float(order['Price']) / 1000,
                       "status": order['Status'],
                       "submited_time": order['SubmitedTime'],
                       "updated_time": order['UpdatedTime']
                       }
                      for order in raw_order_list]
        return RET_OK, "", order_list

    @classmethod
    def us_pack_req(cls, cookie, orderid, statusfilter, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "7008",
               "Version": "1",
               "ReqParam": {"Cookie": str(cookie),
                            "EnvType": str(envtype),
                            "OrderID": orderid,
                            "StatusFilterStr": str(statusfilter),
                            "StockCode": strcode,
                            "start_time": start,
                            "end_time": end,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USOrderArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USOrderArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_list = rsp_data["USOrderArr"]
        if raw_order_list is None or len(raw_order_list) == 0:
            return RET_OK, "", []

        order_list = [{"code": merge_stock_str(2, order['StockCode']),
                       "stock_name": order["StockName"],
                       "dealt_qty": order['DealtQty'],
                       "qty": order['Qty'],
                       "orderid": order['OrderID'],
                       "order_type": order['OrderType'],
                       "order_side": order['OrderSide'],
                       "price": float(order['Price']) / 1000,
                       "status": order['Status'],
                       "submited_time": order['SubmitedTime'],
                       "updated_time": order['UpdatedTime']
                       }
                      for order in raw_order_list]
        return RET_OK, "", order_list


class PositionListQuery:
    """Class for querying position list"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, strcode, stocktype, pl_ratio_min, pl_ratio_max, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1 or (stocktype != '' and stocktype not in SEC_TYPE_MAP):
            error_str = ERROR_STR_PREFIX + "parameter envtype or stocktype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "6009",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "StockCode": strcode,
                            "StockType": str(SEC_TYPE_MAP[stocktype]) if not stocktype == '' else '',
                            "PLRatioMin": str_price1000(pl_ratio_min),
                            "PLRatioMax": str_price1000(pl_ratio_max),
                            "EnvType": envtype,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'Cookie' not in rsp_data or 'EnvType' not in rsp_data:
            return RET_ERROR, msg, None

        if "HKPositionArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find HKPositionArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_position_list = rsp_data["HKPositionArr"]
        if raw_position_list is None or len(raw_position_list) == 0:
            return RET_OK, "", []

        position_list = [{"code": merge_stock_str(1, position['StockCode']),
                          "stock_name": position["StockName"],
                          "qty": position['Qty'],
                          "can_sell_qty": position['CanSellQty'],
                          "cost_price": float(position['CostPrice']) / 1000,
                          "cost_price_valid": position['CostPriceValid'],
                          "market_val": float(position['MarketVal']) / 1000,
                          "nominal_price": float(position['NominalPrice']) / 1000,
                          "pl_ratio": float(position['PLRatio']) / 1000,
                          "pl_ratio_valid": position['PLRatioValid'],
                          "pl_val": float(position['PLVal']) / 1000,
                          "pl_val_valid": position['PLValValid'],
                          "today_buy_qty": position['Today_BuyQty'],
                          "today_buy_val": float(position['Today_BuyVal']) / 1000,
                          "today_pl_val": float(position['Today_PLVal']) / 1000,
                          "today_sell_qty": position['Today_SellQty'],
                          "today_sell_val": float(position['Today_SellVal']) / 1000
                          }
                         for position in raw_position_list]
        return RET_OK, "", position_list

    @classmethod
    def us_pack_req(cls, cookie, strcode, stocktype, pl_ratio_min, pl_ratio_max, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1 or (stocktype != '' and stocktype not in SEC_TYPE_MAP):
            error_str = ERROR_STR_PREFIX + "parameter envtype or stocktype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "7009",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "StockCode": strcode,
                            "StockType": str(SEC_TYPE_MAP[stocktype]) if not stocktype == '' else '',
                            "PLRatioMin": str_price1000(pl_ratio_min),
                            "PLRatioMax": str_price1000(pl_ratio_max),
                            "EnvType": envtype,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USPositionArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USPositionArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_position_list = rsp_data["USPositionArr"]
        if raw_position_list is None or len(raw_position_list) == 0:
            return RET_OK, "", []

        position_list = [{"code": merge_stock_str(2, position['StockCode']),
                          "stock_name": position["StockName"],
                          "qty": position['Qty'],
                          "can_sell_qty": position['CanSellQty'],
                          "cost_price": float(position['CostPrice']) / 1000,
                          "cost_price_valid": position['CostPriceValid'],
                          "market_val": float(position['MarketVal']) / 1000,
                          "nominal_price": float(position['NominalPrice']) / 1000,
                          "pl_ratio": float(position['PLRatio']) / 1000,
                          "pl_ratio_valid": position['PLRatioValid'],
                          "pl_val": float(position['PLVal']) / 1000,
                          "pl_val_valid": position['PLValValid'],
                          "today_buy_qty": position['Today_BuyQty'],
                          "today_buy_val": float(position['Today_BuyVal']) / 1000,
                          "today_pl_val": float(position['Today_PLVal']) / 1000,
                          "today_sell_qty": position['Today_SellQty'],
                          "today_sell_val": float(position['Today_SellVal']) / 1000
                          }
                         for position in raw_position_list]
        return RET_OK, "", position_list


class DealListQuery:
    """Class for """

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        req = {"Protocol": "6010",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'Cookie' not in rsp_data or 'EnvType' not in rsp_data:
            return RET_ERROR, msg, None

        if "HKDealArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find HKDealArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_deal_list = rsp_data["HKDealArr"]
        if raw_deal_list is None or len(raw_deal_list) == 0:
            return RET_OK, "", []

        deal_list = [{"code": merge_stock_str(1, deal['StockCode']),
                      "stock_name": deal["StockName"],
                      "dealid": deal['DealID'],
                      "orderid": deal['OrderID'],
                      "qty": deal['Qty'],
                      "price": float(deal['Price']) / 1000,
                      "orderside": deal['OrderSide'],
                      "time": deal['Time'],
                      "order_side": deal['OrderSide'],
                      }
                     for deal in raw_deal_list]
        return RET_OK, "", deal_list

    @classmethod
    def us_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "7010",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USDealArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USDealArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_deal_list = rsp_data["USDealArr"]
        if raw_deal_list is None or len(raw_deal_list) == 0:
            return RET_OK, "", []

        deal_list = [{"code": merge_stock_str(2, deal['StockCode']),
                      "stock_name": deal["StockName"],
                      "dealid": deal['DealID'],
                      "orderid": deal['OrderID'],
                      "qty": deal['Qty'],
                      "price": float(deal['Price']) / 1000,
                      "orderside": deal['OrderSide'],
                      "time": deal['Time'],
                      "order_side": deal['OrderSide'],
                      }
                     for deal in raw_deal_list]
        return RET_OK, "", deal_list


class TradePushQuery:
    """ Query Trade push info"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_subscribe_req(cls, cookie, envtype, order_id, order_deal_push):
        """Pack the pushed response"""

        req = {"Protocol": "6100",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "OrderID": order_id,
                            "SubOrder": order_deal_push,
                            "SubDeal": order_deal_push
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_pack_subscribe_req(cls, cookie, envtype, order_id, order_deal_push):
        """Pack the pushed response"""

        req = {"Protocol": "7100",
               "Version": "1",
               "ReqParam": {"Cookie": cookie,
                            "EnvType": envtype,
                            "OrderID": order_id,
                            "SubOrder": order_deal_push,
                            "SubDeal": order_deal_push
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_order_push_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        order_info = {
                       "envtype": int(rsp_data['EnvType']),
                       "code": merge_stock_str(1, rsp_data['StockCode']),
                       "stock_name": rsp_data["StockName"],
                       "dealt_avg_price": float(rsp_data['DealtAvgPrice']) / 1000,
                       "dealt_qty": rsp_data['DealtQty'],
                       "qty": rsp_data['Qty'],
                       "orderid": rsp_data['OrderID'],
                       "order_type": rsp_data['OrderType'],
                       "order_side": rsp_data['OrderSide'],
                       "price": float(rsp_data['Price']) / 1000,
                       "status": rsp_data['Status'],
                       "submited_time": rsp_data['SubmitedTime'],
                       "updated_time": rsp_data['UpdatedTime']
                     }
        return RET_OK, "", order_info

    @classmethod
    def hk_unpack_deal_push_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        deal_info = {"envtype": int(rsp_data['EnvType']),
                     "code": merge_stock_str(1, rsp_data['StockCode']),
                     "stock_name": rsp_data["StockName"],
                     "dealid": rsp_data['DealID'],
                     "orderid": rsp_data['OrderID'],
                     "qty": rsp_data['Qty'],
                     "price": float(rsp_data['Price']) / 1000,
                     "order_side": rsp_data['OrderSide'],
                     "time": rsp_data['Time'],
                     "contra_broker_id": int(rsp_data['ContraBrokerID']),
                     "contra_broker_name": rsp_data['ContraBrokerName'],
                    }
        return RET_OK, "", deal_info

    @classmethod
    def us_unpack_order_push_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        order_info = {
                       "envtype": int(rsp_data['EnvType']),
                       "code": merge_stock_str(2, rsp_data['StockCode']),
                       "stock_name": rsp_data["StockName"],
                       "dealt_avg_price": float(rsp_data['DealtAvgPrice']) / 1000,
                       "dealt_qty": rsp_data['DealtQty'],
                       "qty": rsp_data['Qty'],
                       "orderid": rsp_data['OrderID'],
                       "order_type": rsp_data['OrderType'],
                       "order_side": rsp_data['OrderSide'],
                       "price": float(rsp_data['Price']) / 1000,
                       "status": rsp_data['Status'],
                       "submited_time": rsp_data['SubmitedTime'],
                       "updated_time": rsp_data['UpdatedTime']
                     }
        return RET_OK, "", order_info

    @classmethod
    def us_unpack_deal_push_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        deal_info = {"envtype": int(rsp_data['EnvType']),
                     "code": merge_stock_str(1, rsp_data['StockCode']),
                     "stock_name": rsp_data["StockName"],
                     "dealid": rsp_data['DealID'],
                     "orderid": rsp_data['OrderID'],
                     "qty": rsp_data['Qty'],
                     "price": float(rsp_data['Price']) / 1000,
                     "order_side": rsp_data['OrderSide'],
                     "time": rsp_data['Time']
                    }
        return RET_OK, "", deal_info


class HistoryOrderListQuery:
    """Class for querying Histroy Order"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, statusfilter, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "6011",
               "Version": "1",
               "ReqParam": {"Cookie": str(cookie),
                            "EnvType": str(envtype),
                            "StatusFilterStr": str(statusfilter),
                            "StockCode": strcode,
                            "start_date": start,
                            "end_date": end,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if "HKOrderArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find HKOrderArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_list = rsp_data["HKOrderArr"]
        if raw_order_list is None or len(raw_order_list) == 0:
            return RET_OK, "", []

        order_list = [{"code": merge_stock_str(1, order['StockCode']),
                       "stock_name": order["StockName"],
                       "dealt_qty": order['DealtQty'],
                       "qty": order['Qty'],
                       "orderid": order['OrderID'],
                       "order_type": order['OrderType'],
                       "order_side": order['OrderSide'],
                       "price": float(order['Price']) / 1000,
                       "status": order['Status'],
                       "submited_time": order['SubmitedTime'],
                       "updated_time": order['UpdatedTime']
                       }
                      for order in raw_order_list]
        return RET_OK, "", order_list

    @classmethod
    def us_pack_req(cls, cookie, statusfilter, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "7011",
               "Version": "1",
               "ReqParam": {"Cookie": str(cookie),
                            "EnvType": str(envtype),
                            "StatusFilterStr": str(statusfilter),
                            "StockCode": strcode,
                            "start_date": start,
                            "end_date": end,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USOrderArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USOrderArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_list = rsp_data["USOrderArr"]
        if raw_order_list is None or len(raw_order_list) == 0:
            return RET_OK, "", []

        order_list = [{"code": merge_stock_str(2, order['StockCode']),
                       "stock_name": order["StockName"],
                       "dealt_qty": order['DealtQty'],
                       "qty": order['Qty'],
                       "orderid": order['OrderID'],
                       "order_type": order['OrderType'],
                       "order_side": order['OrderSide'],
                       "price": float(order['Price']) / 1000,
                       "status": order['Status'],
                       "submited_time": order['SubmitedTime'],
                       "updated_time": order['UpdatedTime']
                       }
                      for order in raw_order_list]
        return RET_OK, "", order_list


class HistoryDealListQuery:
    """Class for """

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "6012",
               "Version": "1",
               "ReqParam": {"Cookie": str(cookie),
                            "EnvType": str(envtype),
                            "StockCode": strcode,
                            "start_date": start,
                            "end_date": end,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'Cookie' not in rsp_data or 'EnvType' not in rsp_data:
            return RET_ERROR, msg, None

        if "HKDealArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find HKDealArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_deal_list = rsp_data["HKDealArr"]
        if raw_deal_list is None or len(raw_deal_list) == 0:
            return RET_OK, "", []

        deal_list = [{"code": merge_stock_str(1, deal['StockCode']),
                      "stock_name": deal["StockName"],
                      "dealid": deal['DealID'],
                      "orderid": deal['OrderID'],
                      "qty": deal['Qty'],
                      "price": float(deal['Price']) / 1000,
                      "time": deal['Time'],
                      "order_side": deal['OrderSide'],
                      "contra_broker_id": int(deal['ContraBrokerID']),
                      "contra_broker_name": deal['ContraBrokerName'],
                      }
                     for deal in raw_deal_list]
        return RET_OK, "", deal_list

    @classmethod
    def us_pack_req(cls, cookie,  strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {"Protocol": "7012",
               "Version": "1",
               "ReqParam": {"Cookie": str(cookie),
                            "EnvType": str(envtype),
                            "StockCode": strcode,
                            "start_date": start,
                            "end_date": end,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USDealArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USDealArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_deal_list = rsp_data["USDealArr"]
        if raw_deal_list is None or len(raw_deal_list) == 0:
            return RET_OK, "", []

        deal_list = [{"code": merge_stock_str(2, deal['StockCode']),
                      "stock_name": deal["StockName"],
                      "dealid": deal['DealID'],
                      "orderid": deal['OrderID'],
                      "qty": deal['Qty'],
                      "price": float(deal['Price']) / 1000,
                      "order_side": deal['OrderSide'],
                      "time": deal['Time'],
                      }
                     for deal in raw_deal_list]
        return RET_OK, "", deal_list

