# encoding: UTF-8
'''

'''

from vnpyInc import *
from futuquant.open_context import *
import time
from copy import copy


class FutuDataEvent(object):
    name = "FutuDataEvent"

    def __init__(self, quant_frame, quote_context, event_engine, symbol_pools):
        self._quant_frame = quant_frame
        self._quote_context = quote_context
        self._event_engine = event_engine
        self._symbol_pools = symbol_pools
        self._tick_dict = {}

        # 控制频率，1秒钟最多推送多少次
        self._push_event_freq = 10
        self._dict_last_push_time = {}

        # 注册事件
        self._event_engine.register(EVENT_TINY_TICK, self._event_tiny_tick)

        class QuoteHandler(StockQuoteHandlerBase):
            """报价处理器"""
            futu_data_event = self

            def on_recv_rsp(self, rsp_str):
                ret_code, content = super(QuoteHandler, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                    return RET_ERROR, content
                self.futu_data_event.process_quote(content)
                return RET_OK, content

        class OrderBookHandler(OrderBookHandlerBase):
            """摆盘处理器"""
            futu_data_event = self

            def on_recv_rsp(self, rsp_str):
                ret_code, content = super(OrderBookHandler, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                    return RET_ERROR, content
                self.futu_data_event.process_orderbook(content)
                return RET_OK, content

        # 设置回调处理对象
        self._quote_context.set_handler(QuoteHandler())
        self._quote_context.set_handler(OrderBookHandler())

        for symbol in symbol_pools:
            for data_type in ['QUOTE', 'ORDER_BOOK']:
                ret, data = self._quote_context.subscribe(symbol, data_type, True)
                if ret != 0:
                    self.writeCtaLog(u'订阅行情失败：%s' % data)

    def writeCtaLog(self, content):
        content = self.name + ':' + content
        if self._quant_frame is not None:
            self._quant_frame.writeCtaLog(content)

    def _notify_new_tick_event(self, tick):
        """tick推送"""
        if tick.time is EMPTY_STRING:
            return
        event = Event(type_=EVENT_TINY_TICK)
        event.dict_['data'] = tick
        self._event_engine.put(event)

    def _notify_quote_change_event(self, tiny_quote):
        """推送"""
        event = Event(type_=EVENT_QUOTE_CHANGE)
        event.dict_['data'] = tiny_quote
        self._event_engine.put(event)

    def _event_tiny_tick(self, event):
        tick = event.dict_['data']
        t_now = time.time()
        t_last, count_last = 0, 0

        # 控制频率推送行情变化
        if tick.symbol in self._dict_last_push_time:
            t_last, count_last = self._dict_last_push_time[tick.symbol]

        if t_last != t_now or count_last + 1 <= self._push_event_freq:
            t_last = t_now
            count_last += 1
            self._dict_last_push_time[tick.symbol] = (t_last, count_last)
            self._notify_quote_change_event(tick)

    def process_quote(self, data):
        """报价推送"""
        for ix, row in data.iterrows():
            symbol = row['code']

            tick = self._tick_dict.get(symbol, None)
            if not tick:
                tick = TinyQuoteData()
                tick.symbol = symbol
                self._tick_dict[symbol] = tick

            tick.date = row['data_date']
            tick.time = row['data_time']
            tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y-%m-%d %H:%M:%S')

            tick.openPrice = row['open_price']
            tick.highPrice = row['high_price']
            tick.lowPrice = row['low_price']
            tick.preClosePrice = row['prev_close_price']

            tick.lastPrice = row['last_price']
            tick.volume = row['volume']

            new_tick = copy(tick)
            self._notify_new_tick_event(new_tick)

    def process_orderbook(self, data):
        """订单簿推送"""
        symbol = data['stock_code']

        tick = self._tick_dict.get(symbol, None)
        if not tick:
            tick = TinyQuoteData()
            tick.symbol = symbol
            self._tick_dict[symbol] = tick

        d = tick.__dict__
        for i in range(5):
            bid_data = data['Bid'][i]
            ask_data = data['Ask'][i]
            n = i + 1

            d['bidPrice%s' % n] = bid_data[0]
            d['bidVolume%s' % n] = bid_data[1]
            d['askPrice%s' % n] = ask_data[0]
            d['askVolume%s' % n] = ask_data[1]

            new_tick = copy(tick)
        self._notify_new_tick_event(new_tick)


