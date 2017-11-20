# encoding: UTF-8
'''

'''

from vnpyInc import *
from futuquant.open_context import *
import time
from copy import copy
from datetime import  datetime, timedelta

class FutuDataEvent(object):
    name = "FutuDataEvent"

    def __init__(self, quant_frame, quote_context, event_engine, symbol_pools):
        self._quant_frame = quant_frame
        self._quote_context = quote_context
        self._event_engine = event_engine
        self._symbol_pools = symbol_pools
        self._tick_dict = {}
        self._market_opened= False

        # 控制频率，1秒钟最多推送quote多少次
        self._push_event_freq = 10
        self._dict_last_push_time = {}
        self._rt_tiny_quote = TinyQuoteData()

        self._sym_kline_am_dict = {}   # am = ArrayManager
        self._sym_kline_last_dt_dic = {} # 记录最后两个bar时间
        self._sym_kline_last_event_time_dict = {} # 记录最后一次event推送的时间

        # 注册事件
        self._event_engine.register(EVENT_TINY_TICK, self._event_tiny_tick)
        self._event_engine.register(EVENT_CUR_KLINE_PUSH, self._event_cur_kline_push)
        self._event_engine.register(EVENT_BEFORE_TRADING, self.__event_before_trading)
        self._event_engine.register(EVENT_AFTER_TRADING, self.__event_after_trading)

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

        class CurKlineHandler(CurKlineHandlerBase):
            """摆盘处理器"""
            futu_data_event = self

            def on_recv_rsp(self, rsp_str):
                ret_code, content = super(CurKlineHandler, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                    return RET_ERROR, content
                self.futu_data_event.process_curkline(content)
                return RET_OK, content

        # 设置回调处理对象
        self._quote_context.set_handler(QuoteHandler())
        self._quote_context.set_handler(OrderBookHandler())
        self._quote_context.set_handler(CurKlineHandler())

        for symbol in symbol_pools:
            for data_type in ['QUOTE', 'ORDER_BOOK', 'K_DAY', 'K_1M']:
                ret, data = self._quote_context.subscribe(symbol, data_type, True)
                if ret != 0:
                    self.writeCtaLog(u'订阅行情失败：%s' % data)

    @property
    def rt_tiny_quote(self):
        """"返回当前的实时行情数据"""
        return self._rt_tiny_quote

    def get_kl_min1_am(self, symbol):
        return self._get_kl_am(symbol, KTYPE_MIN1)

    def get_kl_day_am(self, symbol):
        return self._get_kl_am(symbol, KTYPE_DAY)

    def _get_kl_am(self, symbol, ktype):
        if symbol not in self._sym_kline_am_dict.keys():
            return None
        if ktype not in self._sym_kline_am_dict[symbol].keys():
            return None
        return self._sym_kline_am_dict[symbol][ktype]

    def _rebuild_sym_kline_am(self, symbol, ktype):
        # 构造k线数据
        kline_max_size = MAP_KLINE_SIZE[ktype]
        if symbol not in self._sym_kline_am_dict:
            self._sym_kline_am_dict[symbol] = {}
        self._sym_kline_am_dict[symbol][ktype] = ArrayManager(kline_max_size)

        if symbol not in self._sym_kline_last_dt_dic:
            self._sym_kline_last_dt_dic[symbol] = {}
        dt_zero = datetime.fromtimestamp(0)
        self._sym_kline_last_dt_dic[symbol][ktype] = (dt_zero, dt_zero)

        #
        dt_bar_last1, dt_bar_last2 = self._sym_kline_last_dt_dic[symbol][ktype]
        array_manager = self._sym_kline_am_dict[symbol][ktype]

        # 导入历史数据
        dt_now = datetime.now()
        # 历史日k取近365天的数据 , 其它k线类型取近30天的数据
        dt_start = dt_now - timedelta(days= 365 if ktype == KTYPE_DAY else 30)
        str_start = dt_start.strftime("%Y-%m-%d")
        str_end = dt_now.strftime("%Y-%m-%d")
        ret, data = self._quote_context.get_history_kline(code=symbol, start=str_start, end=str_end, ktype=ktype, autype='qfq')
        if ret == 0:
            for ix, row in data.iterrows():
                bar = TinyBarData()
                bar.open = row['open']
                bar.close = row['close']
                bar.high = row['high']
                bar.low = row['low']
                bar.volume = row['volume']
                bar.symbol = symbol
                dt_bar = datetime.strptime(str(row['time_key']), "%Y-%m-%d %H:%M:%S")
                bar.datetime = dt_bar
                if dt_bar > dt_bar_last2:
                    array_manager.updateBar(bar)
                    dt_bar_last1 = dt_bar_last2
                    dt_bar_last2 = dt_bar

        # 导入今天的最新数据
        ret, data = self._quote_context.get_cur_kline(code=symbol, num=1000, ktype=ktype, autype='qfq')
        if ret == 0:
            for ix, row in data.iterrows():
                bar = TinyBarData()
                bar.open = row['open']
                bar.close = row['close']
                bar.high = row['high']
                bar.low = row['low']
                bar.volume = row['volume']
                bar.symbol = symbol
                dt_bar = datetime.strptime(str(row['time_key']), "%Y-%m-%d %H:%M:%S")
                bar.datetime = dt_bar
                if dt_bar > dt_bar_last2:
                    array_manager.updateBar(bar)
                    dt_bar_last1 = dt_bar_last2
                    dt_bar_last2 = dt_bar

        # 记录最后一次导入的时间，在实时数据来到时，会依据时间判断是否需要更新
        self._sym_kline_last_dt_dic[symbol][ktype] = (dt_bar_last1, dt_bar_last2)

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
        self._rt_tiny_quote = tiny_quote
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

    def _event_cur_kline_push(self, event):
        bars_data = event.dict_['bars_data']
        symbol = event.dict_['symbol']
        ktype = event.dict_['ktype']

        if symbol not in self._sym_kline_last_dt_dic.keys() or symbol not in self._sym_kline_am_dict.keys():
            return
        if ktype not in self._sym_kline_last_dt_dic[symbol].keys() or ktype not in self._sym_kline_am_dict[symbol].keys():
            return

        dt_last1, dt_last2 = self._sym_kline_last_dt_dic[symbol][ktype]
        array_manager = self._sym_kline_am_dict[symbol][ktype]
        if symbol not in self._sym_kline_last_event_time_dict.keys():
            self._sym_kline_last_event_time_dict[symbol] = {}
        if ktype not in self._sym_kline_last_event_time_dict[symbol].keys():
            self._sym_kline_last_event_time_dict[symbol][ktype] = 0
        event_last_dt = self._sym_kline_last_event_time_dict[symbol][ktype]

        notify_event = False
        notify_bar = None
        dt_now = datetime.now()
        cur_timestamp = int(time.time())

        for bar in bars_data:
            dt = bar.datetime # 正在数据累积中的点
            if dt > dt_now:
                if notify_bar and notify_event:
                    continue
                if event_last_dt != 0 and cur_timestamp >= event_last_dt + 60:
                    bar = TinyBarData()
                    bar.open = array_manager.openArray[-1]
                    bar.close = array_manager.closeArray[-1]
                    bar.high = array_manager.highArray[-1]
                    bar.low = array_manager.lowArray[-1]
                    bar.volume = array_manager.volumeArray[-1]
                    bar.symbol = symbol
                    bar.datetime = dt_last2

                    event_last_dt = (cur_timestamp + 59) / 60 * 60
                    notify_event = True
                    notify_bar = bar

            elif dt > dt_last2:  #插入新数据
                array_manager.updateBar(bar)
                dt_last1 = dt_last2
                dt_last2 = dt
                notify_bar = bar
                notify_event = True

            elif dt == dt_last1 or dt == dt_last2: # 更新数据点
                idx = -1 if dt == dt_last2 else -2
                array_manager.openArray[idx] = bar.open
                array_manager.closeArray[idx] = bar.close
                array_manager.highArray[idx] = bar.high
                array_manager.lowArray[idx] = bar.low
                array_manager.volumeArray[idx] = bar.volume

                # 最后一个点更新， 每隔一分钟也发送一次事件
                if dt == dt_last2 and cur_timestamp >= event_last_dt + 60:
                    event_last_dt = (cur_timestamp + 59) / 60 * 60
                    notify_bar = bar
                    notify_event = True
            else:
                continue # 已经存在的点，忽略

        self._sym_kline_last_dt_dic[symbol][ktype] = (dt_last1, dt_last2)

        #对外通知事件
        if notify_event and self._market_opened:
            self._sym_kline_last_event_time_dict[symbol][ktype] = event_last_dt

            event = Event(type_=EVENT_CUR_KLINE_BAR)
            event.dict_['symbol'] = symbol
            event.dict_['data'] = notify_bar
            event.dict_['ktype'] = ktype
            self._event_engine.put(event)

    def __event_before_trading(self, event):
        for symbol  in  self._symbol_pools:
            for ktype in [KTYPE_DAY, KTYPE_MIN1]:
                self._rebuild_sym_kline_am(symbol, ktype)
        self._market_opened = True

    def __event_after_trading(self, event):
        self._market_opened = False

    def process_quote(self, data):
        """报价推送"""
        for ix, row in data.iterrows():
            symbol = row['code']

            tick = self._tick_dict.get(symbol, None)
            if not tick:
                tick = TinyQuoteData()
                tick.symbol = symbol
                self._tick_dict[symbol] = tick

            tick.date = row['data_date'].replace('-', '')
            tick.time = row['data_time']
            if tick.date and tick.time:
                tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S')
            else:
                return

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

    def process_curkline(self, data):
        """k线实时数据推送"""
        # 每一次推送， 只会是同一个symbole + kltype
        bars_data = []
        symbol = ""
        ktype = ""
        for ix, row in data.iterrows():
            symbol = row['code']
            ktype = row['k_type']
            bar = TinyBarData()
            bar.open = row['open']
            bar.close = row['close']
            bar.high = row['high']
            bar.low = row['low']
            bar.volume = row['volume']
            bar.symbol = symbol
            bar.datetime = datetime.strptime(str(row['time_key']), "%Y-%m-%d %H:%M:%S")

            bars_data.append(bar)

        if not bars_data or not symbol or not ktype:
            return

        """这个回调是在异步线程， 使用event抛到框架数据处理线程中"""
        event = Event(type_=EVENT_CUR_KLINE_PUSH)
        event.dict_['bars_data'] = bars_data
        event.dict_['symbol'] = symbol
        event.dict_['ktype'] = ktype
        self._event_engine.put(event)




