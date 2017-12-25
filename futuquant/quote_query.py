# -*- coding: utf-8 -*-
"""
    Quote query
"""
import sys
import json
from datetime import datetime
from datetime import timedelta
from .utils import *
from .constant import *
import traceback


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
    """extract the response of PLS"""
    try:
        rsp = json.loads(rsp_str)
    except ValueError:
        traceback.print_exc()
        err = sys.exc_info()[1]
        err_str = ERROR_STR_PREFIX + str(err)
        return RET_ERROR, err_str, None

    error_code = int(rsp['ErrCode'])

    if error_code != 0:
        error_str = ERROR_STR_PREFIX + str(error_code) + ' ' + rsp['ErrDesc']
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
    if is_str(stock_str) is False:
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
    if (market not in MKT_MAP) and (market not in QUOTE.REV_MKT_MAP):
        return ""
    market_str = QUOTE.REV_MKT_MAP[market]
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
        if market not in MKT_MAP:
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
        mkt_str = str(MKT_MAP[market])
        req = {"Protocol": "1013",
               "Version": "1",
               "ReqParam": {"Market": mkt_str,
                            "start_date": start_date,
                            "end_date": end_date
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
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
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'TradeDateArr' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find TradeDateArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_trading_day_list = rsp_data['TradeDateArr']

        if raw_trading_day_list is None or len(raw_trading_day_list) == 0:
            return RET_OK, "", []

        # convert to list format that we use
        trading_day_list = [normalize_date_format(x) for x in raw_trading_day_list]

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
        if market not in MKT_MAP:
            error_str = ERROR_STR_PREFIX + " market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None

        if stock_type not in SEC_TYPE_MAP:
            error_str = ERROR_STR_PREFIX + " stock_type is %s, which is not valid. (%s)" \
                                           % (stock_type, ",".join([x for x in SEC_TYPE_MAP]))
            return RET_ERROR, error_str, None

        req = {"Protocol": "1014",
               "Version": "1",
               "ReqParam": {"Market": str(MKT_MAP[market]),
                            "StockType": str(SEC_TYPE_MAP[stock_type]),
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
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
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'BasicInfoArr' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find BasicInfoArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_basic_info_list = rsp_data["BasicInfoArr"]
        market = rsp_data["Market"]

        if raw_basic_info_list is None or len(raw_basic_info_list) == 0:
            return RET_OK, "", []

        basic_info_list = [{"code": merge_stock_str(int(market), record['StockCode']),
                            "stockid": record['StockID'],
                            "name": record["StockName"],
                            "lot_size": int(record["LotSize"]),
                            "stock_type": QUOTE.REV_SEC_TYPE_MAP[int(record["StockType"])],
                            "stock_child_type": (QUOTE.REV_WRT_TYPE_MAP[int(record["StockChildType"])] if
                                                 int(record["StockType"]) == 5 else 0),
                            "owner_stock_code": (merge_stock_str(int(record["OwnerMarketType"]),
                                                                 record["OwnerStockCode"])
                                                 if int(record["StockType"]) == 5 else 0),
                            "listing_date": record["ListTime"]
                            }
                           for record in raw_basic_info_list]
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
            stock_tuple_list.append((str(market_code), stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        req = {"Protocol": "1015",
               "Version": "1",
               "ReqParam": {"StockArr": [{'Market': stock[0], 'StockCode': stock[1]} for stock in stock_tuple_list]}
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
        if "SnapshotArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SnapshotArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_snapshot_list = rsp_data["SnapshotArr"]

        if raw_snapshot_list is None or len(raw_snapshot_list) == 0:
            return RET_OK, "", []

        def futu_timestamp_to_str(int_value):
            if int_value == 0:
                return '1970-01-01'
            else: # for py3.6, fromtimestamp(value), value >= 86400
                return datetime.fromtimestamp(int_value).strftime("%Y-%m-%d")

        snapshot_list = [{'code': merge_stock_str(int(record['MarketType']), record['StockCode']),
                          'update_time': str(record['UpdateTimeStr']),
                          'last_price': int1000_price_to_float(record['NominalPrice']),
                          'open_price': int1000_price_to_float(record['OpenPrice']),
                          'high_price': int1000_price_to_float(record['HighestPrice']),
                          'low_price': int1000_price_to_float(record['LowestPrice']),
                          'prev_close_price': int1000_price_to_float(record['LastClose']),
                          'volume': record['Volume'],
                          'turnover': int1000_price_to_float(record['Turnover']),
                          'turnover_rate': int1000_price_to_float(record['TurnoverRate']),
                          'suspension': True if int(record['SuspendFlag']) == 1 else False,
                          'listing_date': futu_timestamp_to_str(int(record['ListingDate'])),
                          'circular_market_val': int1000_price_to_float(record['CircularMarketVal']),
                          'total_market_val': int1000_price_to_float(record['TotalMarketVal']),
                          'wrt_valid': True if int(record['Wrt_Valid']) == 1 else False,
                          'wrt_conversion_ratio': int1000_price_to_float(record['Wrt_ConversionRatio']),
                          'wrt_type': QUOTE.REV_WRT_TYPE_MAP[int(record['Wrt_Type'])]
                          if int(record['Wrt_Valid']) == 1 else 0,
                          'wrt_strike_price': int1000_price_to_float(record['Wrt_StrikePrice']),
                          'wrt_maturity_date': str(record['Wrt_MaturityDateStr']),
                          'wrt_end_trade': str(record['Wrt_EndTradeDateStr']),
                          'wrt_code': merge_stock_str(int(record['Wrt_OwnerMarketType']), record['Wrt_OwnerStockCode']),
                          'wrt_recovery_price': int1000_price_to_float(record['Wrt_RecoveryPrice']),
                          'wrt_street_vol': int(record['Wrt_StreetVol']),
                          'wrt_issue_vol': int(record['Wrt_IssueVol']),
                          'wrt_street_ratio': int1000_price_to_float(record['Wrt_StreetRatio']),
                          'wrt_delta': int1000_price_to_float(record['Wrt_Delta']),
                          'wrt_implied_volatility': int1000_price_to_float(record['Wrt_ImpliedVolatility']),
                          'wrt_premium': int1000_price_to_float(record['Wrt_Premium']),
                          'lot_size': int(record['LotSize']),
                          # 2017.11.6 add
                          'issued_shares': int(record['Eqt_IssuedShares']) if 'Eqt_IssuedShares' in record else 0,
                          'net_asset': int1000_price_to_float(record['Eqt_NetAssetValue']) if 'Eqt_NetAssetValue' in record else 0,
                          'net_profit': int1000_price_to_float(record['Eqt_NetProfit']) if 'Eqt_NetProfit' in record else 0,
                          'earning_per_share': int1000_price_to_float(record['Eqt_EarningPerShare']) if 'Eqt_EarningPerShare' in record else 0,
                          'outstanding_shares': int(record['Eqt_OutStandingShares']) if 'Eqt_OutStandingShares' in record else 0,
                          'net_asset_per_share': int1000_price_to_float(record['Eqt_NetAssetPerShare']) if 'Eqt_NetAssetPerShare' in record else 0,
                          'ey_ratio': int1000_price_to_float(record['Eqt_EYRatio']) if 'Eqt_EYRatio' in record else 0,
                          'pe_ratio': int1000_price_to_float(record['Eqt_PERatio']) if 'Eqt_PERatio' in record else 0,
                          'pb_ratio': int1000_price_to_float(record['Eqt_PBRatio']) if 'Eqt_PBRatio' in record else 0,
                          } for record in raw_snapshot_list]

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
        req = {"Protocol": "1010",
               "Version": "1",
               "ReqParam": {'Market': str(market_code), 'StockCode': stock_code}
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
        if "RTDataArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find RTDataArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        rt_data_list = rsp_data["RTDataArr"]
        if rt_data_list is None or len(rt_data_list) == 0:
            return RET_OK, "", []

        stock_code = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
        rt_list = [{"time": record['Time'],
                    "code": stock_code,
                    "data_status": True if int(record['DataStatus']) == 1 else False,
                    "opened_mins": record['OpenedMins'],
                    "cur_price": int1000_price_to_float(record['CurPrice']),
                    "last_close": int1000_price_to_float(record['LastClose']),
                    "avg_price": int1000_price_to_float(record['AvgPrice']),
                    "turnover": int1000_price_to_float(record['Turnover']),
                    "volume": record['Volume']
                    } for record in rt_data_list]

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
        if market not in MKT_MAP:
            error_str = ERROR_STR_PREFIX + "market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None

        if plate_class not in PLATE_CLASS_MAP:
            error_str = ERROR_STR_PREFIX + "the class of plate is %s, which is not valid. (%s)" \
                                           % (plate_class, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None

        req = {"Protocol": "1026",
               "Version": "1",
               "ReqParam": {"Market": str(MKT_MAP[market]),
                            "PlateClass": str(PLATE_CLASS_MAP[plate_class])}
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
        if "PlatesetIDsArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find PlatesetIDsArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_plate_list = rsp_data["PlatesetIDsArr"]

        if raw_plate_list is None or len(raw_plate_list) == 0:
            return RET_OK, "", []

        plate_list = [{"code": merge_stock_str(int(record['Market']), record['StockCode']),
                       "plate_name": record['StockName'],
                       "plate_id": record['StockID']
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

        req = {"Protocol": "1027",
               "Version": "1",
               "ReqParam": {"Market": str(market),
                            "StockCode": str(stock_code)}
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

        if "PlateSubIDsArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find PlateSubIDsArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if rsp_data["PlateSubIDsArr"] is None or len(rsp_data["PlateSubIDsArr"]) == 0:
            return RET_OK, "", []

        raw_stock_list = rsp_data["PlateSubIDsArr"]
        stock_list = [{"lot_size": int(record['LotSize']),
                       "code": merge_stock_str(int(record['Market']), record['StockCode']),
                       "stock_name": record['StockName'],
                       "owner_market": merge_stock_str(int(record['OwnerMarketType']), record['OwnerStockCode']),
                       "stock_child_type": (str(QUOTE.REV_WRT_TYPE_MAP['StockChildType'])
                                            if int(record['StockType']) == 5 else 0),
                       "stock_type": QUOTE.REV_SEC_TYPE_MAP[int(record['StockType'])]
                       } for record in raw_stock_list]

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

        req = {"Protocol": "1028",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code}
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
        if "BrokerBidArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find BrokerBidArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if "BrokerAskArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find BrokerAskArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_broker_bid = rsp_data["BrokerBidArr"]
        bid_list = []
        if raw_broker_bid is not None:
            bid_list = [{"bid_broker_id": record['BrokerID'],
                         "bid_broker_name": record['BrokerName'],
                         "bid_broker_pos": record['BrokerPos'],
                         "code": merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
                         } for record in raw_broker_bid]

        raw_broker_ask = rsp_data["BrokerAskArr"]
        ask_list = []
        if raw_broker_ask is not None:
            ask_list = [{"ask_broker_id": record['BrokerID'],
                         "ask_broker_name": record['BrokerName'],
                         "ask_broker_pos": record['BrokerPos'],
                         "code": merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
                         } for record in raw_broker_ask]

        return RET_OK, bid_list, ask_list


class HistoryKlineQuery:
    """
    Query Conversion for getting historic Kline data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_str, start_date, end_date, ktype, autype, fields, max_num):
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

        req = {"Protocol": "1024",
               "Version": "1",
               "ReqParam": {'Market': str(market_code),
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
        return RET_OK, "", req_str

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
        if rsp_data["HistoryKLArr"] is None or len(rsp_data["HistoryKLArr"]) == 0:
            return RET_OK, "", (list_ret, has_next, next_time)

        raw_kline_list = rsp_data["HistoryKLArr"]
        stock_code = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])

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
                dict_data['turnover'] = int1000_price_to_float(record['Turnover'])
            if 'PERatio' in record:
                dict_data['pe_ratio'] = int1000_price_to_float(record['PERatio'])
            if 'TurnoverRate' in record:
                dict_data['turnover_rate'] = int1000_price_to_float(record['TurnoverRate'])
            if 'ChangeRate' in record:
                dict_data['change_rate'] = int1000_price_to_float(record['ChangeRate'])

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

        req = {"Protocol": "1025",
               "Version": "1",
               "ReqParam": {'StockArr': [{'Market': stock[0], 'StockCode': stock[1]} for stock in stock_tuple_list]}
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

        if rsp_data["ExRightInfoArr"] is None or len(rsp_data["ExRightInfoArr"]) == 0:
            return RET_OK, "", []

        get_val = (lambda x, y: float(y[x]) / 100000 if x in y else 0)
        raw_exr_list = rsp_data["ExRightInfoArr"]
        exr_list = [{'code': merge_stock_str(int(record['Market']), record['StockCode']),
                     'ex_div_date': record['ExDivDate'],
                     'split_ratio': get_val('SplitRatio', record),
                     'per_cash_div': get_val('PerCashDiv', record),
                     'per_share_div_ratio': get_val('PerShareDivRatio', record),
                     'per_share_trans_ratio': get_val('PerShareTransRatio', record),
                     'allotment_ratio': get_val(r'AllotmentRatio', record),
                     'allotment_price': get_val('AllotmentPrice', record),
                     'stk_spo_ratio': get_val('StkSpoRatio', record),
                     'stk_spo_price': get_val('StkSpoPrice', record),
                     'forward_adj_factorA': get_val('ForwardAdjFactorA', record),
                     'forward_adj_factorB': get_val('ForwardAdjFactorB', record),
                     'backward_adj_factorA': get_val('BackwardAdjFactorA', record),
                     'backward_adj_factorB': get_val('BackwarAdjFactorB', record)
                     }
                    for record in raw_exr_list]

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
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in SUBTYPE_MAP:
            subtype_str = ','.join([x for x in SUBTYPE_MAP])
            error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = SUBTYPE_MAP[data_type]
        req = {"Protocol": "1005",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockSubType": str(subtype)
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_subscribe_rsp(cls, rsp_str):
        """Unpack the subscribed response"""
        ret, msg, content = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        return RET_OK, "", None

    @classmethod
    def pack_unsubscribe_req(cls, stock_str, data_type):
        """Pack the un-subscribed request"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in SUBTYPE_MAP:
            subtype_str = ','.join([x for x in SUBTYPE_MAP])
            error_str = ERROR_STR_PREFIX + 'data_type is %s, which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = SUBTYPE_MAP[data_type]

        req = {"Protocol": "1006",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockSubType": str(subtype)
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_unsubscribe_rsp(cls, rsp_str):
        """Unpack the un-subscribed response"""
        ret, msg, content = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        return RET_OK, "", None

    @classmethod
    def pack_subscription_query_req(cls, query):
        """Pack the subscribed query request"""
        req = {"Protocol": "1007",
               "Version": "1",
               "ReqParam": {"QueryAllSocket": str(query)}
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_subscription_query_rsp(cls, rsp_str):
        """Unpack the subscribed query response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SubInfoArr' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find TradeDateArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        subscription_table = {}

        raw_subscription_list = rsp_data['SubInfoArr']
        if raw_subscription_list is None or len(raw_subscription_list) == 0:
            return RET_OK, "", subscription_table

        subscription_list = [(merge_stock_str(int(x['Market']), x['StockCode']),
                              QUOTE.REV_SUBTYPE_MAP[int(x['StockSubType'])])
                             for x in raw_subscription_list]

        for stock_code_str, sub_type in subscription_list:
            if sub_type not in subscription_table:
                subscription_table[sub_type] = []
            subscription_table[sub_type].append(stock_code_str)

        return RET_OK, "", subscription_table

    @classmethod
    def pack_push_req(cls, stock_str, data_type):
        """Pack the pushed response"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in SUBTYPE_MAP:
            subtype_str = ','.join([x for x in SUBTYPE_MAP])
            error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = SUBTYPE_MAP[data_type]
        req = {"Protocol": "1008",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockPushType": str(subtype)
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def pack_unpush_req(cls, stock_str, data_type):
        """Pack the un-pushed request"""
        ret, content = split_stock_str(stock_str)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if data_type not in SUBTYPE_MAP:
            subtype_str = ','.join([x for x in SUBTYPE_MAP])
            error_str = ERROR_STR_PREFIX + 'data_type is %s , which is wrong. (%s)' % (data_type, subtype_str)
            return RET_ERROR, error_str, None

        subtype = SUBTYPE_MAP[data_type]
        req = {"Protocol": "1008",
               "Version": "1",
               "ReqParam": {"Market": str(market_code),
                            "StockCode": stock_code,
                            "StockPushType": str(subtype),
                            "UnPush": str(int(True))
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str


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
            stock_tuple_list.append((str(market_code), stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        req = {"Protocol": "1023",
               "Version": "1",
               "ReqParam": {'ReqArr': [{'Market': stock[0], 'StockCode': stock[1]} for stock in stock_tuple_list]}
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
        if "SubSnapshotArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SubSnapshotArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_quote_list = rsp_data["SubSnapshotArr"]

        quote_list = [{'code': merge_stock_str(int(record['Market']), record['StockCode']),
                       'data_date': record['Date'],
                       'data_time': record['Time'],
                       'last_price': int1000_price_to_float(record['CurPrice']),
                       'open_price': int1000_price_to_float(record['Open']),
                       'high_price': int1000_price_to_float(record['High']),
                       'low_price': int1000_price_to_float(record['Low']),
                       'prev_close_price': int1000_price_to_float(record['LastClose']),
                       'volume': int(record['Volume']),
                       'turnover': int1000_price_to_float(record['Turnover']),
                       'turnover_rate': int1000_price_to_float(record['TurnoverRate']),
                       'amplitude': int1000_price_to_float(record['Amplitude']),
                       'suspension': True if int(record['Suspension']) == 1 else False,
                       'listing_date': record['ListTime']
                       }
                      for record in raw_quote_list]

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

        req = {"Protocol": "1012",
               "Version": "1",
               "ReqParam": {'Market': str(market_code),
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

        stock_code = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
        ticker_list = [{"code": stock_code,
                        "time": record['Time'],
                        "price": int1000_price_to_float(record['Price']),
                        "volume": record['Volume'],
                        "turnover": int1000_price_to_float(record['Turnover']),
                        "ticker_direction": QUOTE.REV_TICKER_DIRECTION[int(record['Direction'])],
                        "sequence": int(record["Sequence"])
                        }
                       for record in raw_ticker_list]
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

        req = {"Protocol": "1011",
               "Version": "1",
               "ReqParam": {'Market': str(market_code),
                            'StockCode': stock_code,
                            'Num': str(num),
                            'KLType': str(KTYPE_MAP[ktype]),
                            'RehabType': str(AUTYPE_MAP[autype])
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

        if "KLDataArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find KLDataArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if "KLType" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find KLType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        if rsp_data["KLDataArr"] is None or len(rsp_data["KLDataArr"]) == 0:
            return RET_OK, "", []

        k_type = rsp_data["KLType"]
        try:
            k_type = int(k_type)
            k_type = QUOTE.REV_KTYPE_MAP[k_type]
        except TypeError:
            traceback.print_exc()
            err = sys.exc_info()[1]
            error_str = ERROR_STR_PREFIX + str(err) + str(rsp_data["KLType"])
            return RET_ERROR, error_str, None

        raw_kline_list = rsp_data["KLDataArr"]
        stock_code = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])
        kline_list = [{"code": stock_code,
                       "time_key": record['Time'],
                       "open": int1000_price_to_float(record['Open']),
                       "high": int1000_price_to_float(record['High']),
                       "low": int1000_price_to_float(record['Low']),
                       "close": int1000_price_to_float(record['Close']),
                       "volume": record['Volume'],
                       "turnover": int1000_price_to_float(record['Turnover']),
                       "k_type": k_type,
                       "pe_ratio": int1000_price_to_float(record['PERatio']),
                       "turnover_rate": int1000_price_to_float(record['TurnoverRate'])
                       }
                      for record in raw_kline_list]

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
        req = {"Protocol": "1002",
               "Version": "1",
               "ReqParam": {'Market': str(market_code), 'StockCode': stock_code, 'Num': str(10)}
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
        if "GearArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find GearArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_book = rsp_data["GearArr"]
        stock_str = merge_stock_str(int(rsp_data['Market']), rsp_data['StockCode'])

        order_book = {'stock_code': stock_str, 'Ask': [], 'Bid': []}
        if raw_order_book is None:
            return RET_OK, "", order_book

        for record in raw_order_book:
            bid_record = (int1000_price_to_float(record['BuyPrice']), int(record['BuyVol']), int(record['BuyOrder']))
            ask_record = (int1000_price_to_float(record['SellPrice']), int(record['SellVol']), int(record['SellOrder']))

            order_book['Bid'].append(bid_record)
            order_book['Ask'].append(ask_record)

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

        req = {"Protocol": "1039",
               "Version": "1",
               "ReqParam": {
                   'Cookie': '10000',
                   'StockArr': [
                        {'Market': str(market), 'StockCode': code}
                        for (market, code) in list_req_stock],
                   'start_date': start,
                   'end_date': end}
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
            list_date = [x['SuspendTime'] for x in date_arr] if date_arr else []
            str_date = ','.join(list_date) if list_date and len(list_date) > 0 else ''
            ret_susp_list.append({'code': stock_str, 'suspension_dates': str_date})

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
        req = {"Protocol": "1029",
               "Version": "1",
               "ReqParam": {"StateType": state_type,
                            }
               }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

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
    def pack_req(cls, codes, dates, fields, ktype, autype, max_num, no_data_mode):
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

        req = {"Protocol": "1038",
               "Version": "1",
               "ReqParam": {
                   'Cookie': '10000',
                   'NoDataMode': str(no_data_mode),
                   'RehabType': str(AUTYPE_MAP[autype]),
                   'KLType': str(KTYPE_MAP[ktype]),
                   'MaxKLNum': str(max_num),
                   'StockArr': [
                        {'Market': str(market), 'StockCode': code}
                        for (market, code) in list_req_stock],
                   'TimePoints': str(','.join(dates)),
                   'NeedKLData': str(','.join(list_req_field))
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
            stock_str = merge_stock_str(int(kline['Market']), kline['StockCode'])
            data_arr = kline['HistoryKLArr']
            for point_data in data_arr:
                dict_data['code'] = stock_str
                dict_data['time_point'] = point_data['TimePoint']
                dict_data['data_valid'] = int(point_data['DataValid'])
                if 'Time' in point_data:
                    dict_data['time_key'] = point_data['Time']
                if 'Open' in point_data:
                    dict_data['open'] = int10_9_price_to_float(point_data['Open'])
                if 'High' in point_data:
                    dict_data['high'] = int10_9_price_to_float(point_data['High'])
                if 'Low' in point_data:
                    dict_data['low'] = int10_9_price_to_float(point_data['Low'])
                if 'Close' in point_data:
                    dict_data['close'] = int10_9_price_to_float(point_data['Close'])
                if 'Volume' in point_data:
                    dict_data['volume'] = point_data['Volume']
                if 'Turnover' in point_data:
                    dict_data['turnover'] = int1000_price_to_float(point_data['Turnover'])
                if 'PERatio' in point_data:
                    dict_data['pe_ratio'] = int1000_price_to_float(point_data['PERatio'])
                if 'TurnoverRate' in point_data:
                    dict_data['turnover_rate'] = int1000_price_to_float(point_data['TurnoverRate'])
                if 'ChangeRate' in point_data:
                    dict_data['change_rate'] = int1000_price_to_float(point_data['ChangeRate'])

                list_ret.append(dict_data.copy())

        return RET_OK, "", (list_ret, has_next)
