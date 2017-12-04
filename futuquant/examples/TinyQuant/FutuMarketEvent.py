# encoding: UTF-8
'''

'''

from vnpyInc import *
from TinyDefine import *
from datetime import datetime

class Futu_Market_State:
    MARKET_NONE = "none"
    MARKET_PRE_OPEN = 'pre_open'
    MARKET_OPEN = 'open'
    MARKET_REST = 'rest'
    MARKET_MID_OPEN = 'mid open'
    MARKET_CLOSE = 'close'
    MARKET_CLOSE_FINAL = 'close fin'

class FutuMarketEvent(object):
    def __init__(self, market, quote_context, event_engine):
        self._market = market
        self._quote_context = quote_context
        self._event_engine = event_engine

        # check market state per x second
        self._check_freq = 3
        self._check_tick = 0
        self._last_status = None
        self._today_date = datetime.now().strftime('%Y%m%d')
        self._has_notify_before_trading = False

        self._mkt_key = ""
        self._mkt_dic = {
            0: Futu_Market_State.MARKET_NONE,  # 未开盘
            1: Futu_Market_State.MARKET_PRE_OPEN,  # 竞价交易(港股)
            2: Futu_Market_State.MARKET_PRE_OPEN,  # 早盘前等待开盘(港股)
            3: Futu_Market_State.MARKET_OPEN,  # 早盘(港股)
            4: Futu_Market_State.MARKET_REST,  # 午休(A|港股)
            5: Futu_Market_State.MARKET_MID_OPEN,  # 午盘(A|港股) &&  盘中(美股)
            6: Futu_Market_State.MARKET_CLOSE,  # 交易日结束(A|港股) / 已收盘(美股)
            8: Futu_Market_State.MARKET_PRE_OPEN,  # 盘前开始(美股)
            9: Futu_Market_State.MARKET_PRE_OPEN,  # 盘前结束(美股)
            10: Futu_Market_State.MARKET_CLOSE,  # 盘后开始(美股)
            11: Futu_Market_State.MARKET_CLOSE,  # 盘后结束(美股)
            12: Futu_Market_State.MARKET_NONE,  # 盘后结束(美股)

            13: Futu_Market_State.MARKET_MID_OPEN,  # 夜市交易中(港期货)
            14: Futu_Market_State.MARKET_CLOSE_FINAL,  # 夜市收盘(港期货)
            15: Futu_Market_State.MARKET_OPEN,  # 日市交易中(港期货)
            16: Futu_Market_State.MARKET_REST,  # 日市午休(港期货)
            17: Futu_Market_State.MARKET_CLOSE,  # 日市收盘(港期货)
            18: Futu_Market_State.MARKET_PRE_OPEN,  # 日市等待开盘(港期货)
            19: Futu_Market_State.MARKET_CLOSE_FINAL,  # 港股盘后竞价
        }

        if self._market == MARKET_HK:
            self._mkt_key = 'Market_HK'
        elif self._market == MARKET_US:
            self._mkt_key = 'Market_US'
        else:
            raise RuntimeError("Market Error")

        # 注册事件
        self._event_engine.register(EVENT_TIMER, self._timer_check_market)

    @property
    def today_date(self):
        return self._today_date

    def _timer_check_market(self, event):
        self._check_tick += 1
        if self._check_tick % self._check_freq != 0:
            return

        ret, state_dict = self._quote_context.get_global_state()
        if ret != 0:
            return

        mkt_val = int(state_dict[self._mkt_key])
        new_status = self._mkt_dic[mkt_val]
        if self._last_status == new_status:
            return
        self._last_status = new_status
        self._today_date = datetime.fromtimestamp(int(state_dict['TimeStamp'])).strftime('%Y%m%d')

        if new_status == Futu_Market_State.MARKET_OPEN or new_status == Futu_Market_State.MARKET_MID_OPEN:
            # before trading 通知
            if not self._has_notify_before_trading:
                self._has_notify_before_trading = True
                event = Event(type_= EVENT_BEFORE_TRADING)
                event.dict_['TimeStamp'] = state_dict['TimeStamp']
                self._event_engine.put(event)
        elif new_status == Futu_Market_State.MARKET_CLOSE:
            list_event = [EVENT_AFTER_TRADING]
            # 目前只有港股有盘后交易,其它市场模拟发一个EVENT_AFTER_TRADING_FINAL事件
            if self._market == MARKET_SH or self._market == MARKET_SZ or self._market == MARKET_US:
                self._has_notify_before_trading = False
                list_event.append(EVENT_AFTER_TRADING_FINAL)

            for x in list_event:
                event = Event(type_=x)
                event.dict_['TimeStamp'] = state_dict['TimeStamp']
                self._event_engine.put(event)

        elif new_status == Futu_Market_State.MARKET_CLOSE_FINAL:
            self._has_notify_before_trading = False
            event = Event(type_=EVENT_AFTER_TRADING_FINAL)
            event.dict_['TimeStamp'] = state_dict['TimeStamp']
            self._event_engine.put(event)


