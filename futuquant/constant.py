# -*- coding: utf-8 -*-
"""
    Constant collection
"""
from copy import copy

# 需要安装的最低牛牛客户端版本号
NN_VERSION_MIN = '3.42.4952'

MKT_MAP = {"HK": 1,
           "US": 2,
           "SH": 3,
           "SZ": 4,
           "HK_FUTURE": 6
           }

WRT_TYPE_MAP = {"CALL": 1,
                "PUT": 2,
                "BULL": 3,
                "BEAR": 4,
                "N/A": 0
                }

PLATE_CLASS_MAP = {"ALL": 0,
                   "INDUSTRY": 1,
                   "REGION": 2,
                   "CONCEPT": 3
                   }

SEC_TYPE_MAP = {"STOCK": 3,
                "IDX": 6,
                "ETF": 4,
                "WARRANT": 5,
                "BOND": 1,
                "N/A": 0
                }

SUBTYPE_MAP = {"TICKER": 4,
               "QUOTE": 1,
               "ORDER_BOOK": 2,
               "K_1M": 11,
               "K_5M": 7,
               "K_15M": 8,
               "K_30M": 9,
               "K_60M": 10,
               "K_DAY": 6,
               "K_WEEK": 12,
               "K_MON": 13,
               "RT_DATA": 5,
               "BROKER": 14
               }

KTYPE_MAP = {"K_1M": 1,
             "K_5M": 6,
             "K_15M": 7,
             "K_30M": 8,
             "K_60M": 9,
             "K_DAY": 2,
             "K_WEEK": 3,
             "K_MON": 4
             }

AUTYPE_MAP = {'None': 0,
              "qfq": 1,
              "hfq": 2
              }

TICKER_DIRECTION = {"TT_BUY": 1,
                    "TT_SELL": 2,
                    "TT_NEUTRAL": 3
                    }

ORDER_STATUS = {"CANCEL": 0,
                "INVALID": 1,
                "VALID": 2,
                "DELETE": 3
                }

ENVTYPE_MAP = {"TRUE": 0,
               "SIMULATE": 1
               }

RET_OK = 0
RET_ERROR = -1
ERROR_STR_PREFIX = 'ERROR. '
EMPTY_STRING = ''

# 指定时间为非交易日时，对应的k线数据取值模式， get_multi_points_history_kline 参数用到
KL_NO_DATA_MODE_NONE = '0'       # 返回无数据
KL_NO_DATA_MODE_FORWARD = '1'    # 往前取数据
KL_NO_DATA_MODE_BACKWARD = '2'   # 往后取数据

# noinspection PyPep8Naming
class TRADE(object):
    REV_MKT_MAP = {MKT_MAP[x]: x for x in MKT_MAP}
    REV_SEC_TYPE_MAP = {SEC_TYPE_MAP[x]: x for x in SEC_TYPE_MAP}
    REV_SUBTYPE_MAP = {SUBTYPE_MAP[x]: x for x in SUBTYPE_MAP}
    REV_KTYPE_MAP = {KTYPE_MAP[x]: x for x in KTYPE_MAP}
    REV_AUTYPE_MAP = {AUTYPE_MAP[x]: x for x in AUTYPE_MAP}
    REV_TICKER_DIRECTION = {TICKER_DIRECTION[x]: x for x in TICKER_DIRECTION}
    REV_ORDER_STATUS = {ORDER_STATUS[x]: x for x in ORDER_STATUS}
    REV_ENVTYPE_MAP = {ENVTYPE_MAP[x]: x for x in ENVTYPE_MAP}
    REV_ENVTYPE_STR_MAP = {str(ENVTYPE_MAP[x]): x for x in ENVTYPE_MAP}

    # 港股支持模拟和真实环境
    @staticmethod
    def check_envtype_hk(envtype):
        return str(envtype) in TRADE.REV_ENVTYPE_STR_MAP

    # 美股目前不支持模拟环境
    @staticmethod
    def check_envtype_us(envtype):
        return str(envtype) == u'0'

# noinspection PyPep8Naming
class QUOTE(object):
    REV_MKT_MAP = {MKT_MAP[x]: x for x in MKT_MAP}
    REV_WRT_TYPE_MAP = {WRT_TYPE_MAP[x]: x for x in WRT_TYPE_MAP}
    REV_PLATE_CLASS_MAP = {PLATE_CLASS_MAP[x]: x for x in PLATE_CLASS_MAP}
    REV_SEC_TYPE_MAP = {SEC_TYPE_MAP[x]: x for x in SEC_TYPE_MAP}
    REV_SUBTYPE_MAP = {SUBTYPE_MAP[x]: x for x in SUBTYPE_MAP}
    REV_KTYPE_MAP = {KTYPE_MAP[x]: x for x in KTYPE_MAP}
    REV_AUTYPE_MAP = {AUTYPE_MAP[x]: x for x in AUTYPE_MAP}
    REV_TICKER_DIRECTION = {TICKER_DIRECTION[x]: x for x in TICKER_DIRECTION}


class KL_FIELD(object):
    ALL = ''
    DATE_TIME = '1'
    OPEN = '2'
    CLOSE = '3'
    HIGH = '4'
    LOW = '5'
    PE_RATIO = '6'
    TURNOVER_RATE = '7'
    TRADE_VOL = '8'
    TRADE_VAL = '9'
    CHANGE_RATE = '10'
    ALL_REAL = [DATE_TIME, OPEN, CLOSE, HIGH, LOW, PE_RATIO, TURNOVER_RATE, TRADE_VOL, TRADE_VAL, CHANGE_RATE]
    DICT_KL_FIELD_STR = {DATE_TIME: 'time_key',
                         OPEN: 'open',
                         CLOSE: 'close',
                         HIGH: 'high',
                         LOW: 'low',
                         PE_RATIO: 'pe_ratio',
                         TURNOVER_RATE: 'turnover_rate',
                         TRADE_VOL: 'volume',
                         TRADE_VAL: 'turnover',
                         CHANGE_RATE: 'change_rate'
                         }
    @classmethod
    def get_field_list(cls, str_filed):
        ret_list = []
        data = str(str_filed).split(',')
        if KL_FIELD.ALL in data:
            ret_list = copy(KL_FIELD.ALL_REAL)
        else:
            for x in data:
                if x in KL_FIELD.ALL_REAL:
                    ret_list.append(x)
        return ret_list

    @classmethod
    def normalize_field_list(cls, fields):
        list_ret = []
        if KL_FIELD.ALL in fields:
            list_ret = copy(KL_FIELD.ALL_REAL)
        else:
            for x in fields:
                if x in KL_FIELD.ALL_REAL and x not in list_ret:
                    list_ret.append(x)
        return list_ret
