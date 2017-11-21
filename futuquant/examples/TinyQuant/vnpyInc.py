# encoding: UTF-8

'''
    用到的vnpy的相关接口
'''

from __future__ import division
import json
import os
import traceback
import threading

from vnpy.event import *
from vnpy.event.eventType import *
from vnpy.trader.vtObject import VtLogData, VtTickData, VtBarData

from vnpy.trader.vtEngine import LogEngine
from vnpy.trader.vtFunction import getJsonPath
from vnpy.trader.vtConstant import (EMPTY_STRING, EMPTY_UNICODE,
                                    EMPTY_FLOAT, EMPTY_INT)
from vnpy.trader.app.ctaStrategy.ctaTemplate import ArrayManager

EVENT_TINY_LOG = 'tiny_quant_log'
EVENT_INI_FUTU_API = 'init futu api'

EVENT_BEFORE_TRADING = 'before trading'
EVENT_AFTER_TRADING = 'after trading'

EVENT_TINY_TICK = 'tiny tick'
EVENT_QUOTE_CHANGE ='tiny quote data change'

EVENT_CUR_KLINE_PUSH = 'cur kline push'
EVENT_CUR_KLINE_BAR = 'kline min1 bar'

MARKET_HK = 'HK'
MARKET_US = 'US'

# futu api k线定阅类型转定义
KTYPE_DAY = 'K_DAY'
KTYPE_MIN1 = 'K_1M'
KTYPE_MIN5 = 'K_5M'
KTYPE_MIN15 = 'K_15M'
KTYPE_MIN30 = 'K_30M'
KTYPE_MIN60 = 'K_60M'

# 定义array_manager中的kline数据最大个数
MAP_KLINE_SIZE = {KTYPE_DAY: 200,
                  KTYPE_MIN1: 3000,
                  KTYPE_MIN5: 1000,
                  KTYPE_MIN15: 500,
                  KTYPE_MIN30: 500,
                  KTYPE_MIN60: 500,
                  }


class GLOBAL(object):
    """ datetime.strptime 有线程安全问题"""
    dt_lock = threading._RLock()

class TinyQuoteData(object):
    """行情数据类"""
    def __init__(self):
        # 代码相关
        self.symbol = EMPTY_STRING  # 合约代码

        # 成交数据
        self.lastPrice = EMPTY_FLOAT  # 最新成交价
        self.volume = EMPTY_INT  # 今天总成交量
        self.time = EMPTY_STRING  # 时间 11:20:56.0
        self.date = EMPTY_STRING  # 日期 20151009
        self.datetime = None

        # 常规行情
        self.openPrice = EMPTY_FLOAT  # 今日开盘价
        self.highPrice = EMPTY_FLOAT  # 今日最高价
        self.lowPrice = EMPTY_FLOAT  # 今日最低价
        self.preClosePrice = EMPTY_FLOAT

        # 五档行情
        self.bidPrice1 = EMPTY_FLOAT
        self.bidPrice2 = EMPTY_FLOAT
        self.bidPrice3 = EMPTY_FLOAT
        self.bidPrice4 = EMPTY_FLOAT
        self.bidPrice5 = EMPTY_FLOAT

        self.askPrice1 = EMPTY_FLOAT
        self.askPrice2 = EMPTY_FLOAT
        self.askPrice3 = EMPTY_FLOAT
        self.askPrice4 = EMPTY_FLOAT
        self.askPrice5 = EMPTY_FLOAT

        self.bidVolume1 = EMPTY_INT
        self.bidVolume2 = EMPTY_INT
        self.bidVolume3 = EMPTY_INT
        self.bidVolume4 = EMPTY_INT
        self.bidVolume5 = EMPTY_INT

        self.askVolume1 = EMPTY_INT
        self.askVolume2 = EMPTY_INT
        self.askVolume3 = EMPTY_INT
        self.askVolume4 = EMPTY_INT
        self.askVolume5 = EMPTY_INT


class TinyBarData(object):
    """K线数据"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(TinyBarData, self).__init__()

        self.symbol = EMPTY_STRING  # 代码

        self.open = EMPTY_FLOAT
        self.high = EMPTY_FLOAT
        self.low = EMPTY_FLOAT
        self.close = EMPTY_FLOAT
        self.volume = EMPTY_INT  # 成交量
        self.datetime = None

