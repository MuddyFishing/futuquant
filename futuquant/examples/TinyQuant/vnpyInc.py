# encoding: UTF-8

'''
    用到的vnpy的相关接口
'''

from __future__ import division
import json
import os
import traceback


from vnpy.event import *
from vnpy.event.eventType import *
from vnpy.trader.vtObject import VtLogData, VtTickData
from vnpy.trader.vtEngine import LogEngine
from vnpy.trader.vtFunction import getJsonPath
from vnpy.trader.vtConstant import (EMPTY_STRING, EMPTY_UNICODE,
                                    EMPTY_FLOAT, EMPTY_INT)

EVENT_TINY_LOG = 'tiny_quant_log'
EVENT_INI_FUTU_API = 'init futu api'

EVENT_BEFORE_TRADING = 'before trading'
EVENT_AFTER_TRADING = 'after trading'
EVENT_TINY_TICK = 'tiny tick'
EVENT_QUOTE_CHANGE ='tiny quote data change'

MARKET_HK = 'HK'
MARKET_US = 'US'


class TinyQuoteData(object):
    """行情数据类"""

    # ----------------------------------------------------------------------
    def __init__(self):
        # 代码相关
        self.symbol = EMPTY_STRING  # 合约代码

        # 成交数据
        self.lastPrice = EMPTY_FLOAT  # 最新成交价
        self.volume = EMPTY_INT  # 今天总成交量
        self.time = EMPTY_STRING  # 时间 11:20:56
        self.date = EMPTY_STRING  # 日期 2015-10-09
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
