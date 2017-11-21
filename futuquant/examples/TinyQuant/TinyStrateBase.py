# encoding: UTF-8

'''

'''
from vnpyInc import *
from abc import ABCMeta, abstractmethod
from datetime import datetime

class TinyStrateBase(object):
    """策略名称, setting.json中作为该策略配置的key"""
    name = 'tiny_strate_base'

    """策略需要用到行情数据的股票池"""
    symbol_pools = ['HK.00700', 'HK.00001']

    def __init__(self):
        # 这里没有用None,因为None在 __loadSetting中当作错误参数检查用了
        self._quant_frame = 0
        self._event_engine = 0
        self._market_opened= False

    @abstractmethod
    def on_start(self):
        """策略启动入口"""
        pass

    @abstractmethod
    def on_quote_changed(self, tiny_quote):
        """报价、摆盘实时数据变化时，会触发该回调"""
        # TinyQuoteData
        data = tiny_quote
        str_log = "on_quote_changed symbol=%s open=%s high=%s close=%s low=%s" % (data.symbol, data.openPrice, data.highPrice, data.lastPrice, data.lowPrice)
        self.log(str_log)

    @abstractmethod
    def on_bar_min1(self, tiny_bar):
        """每一分钟触发一次回调"""
        bar = tiny_bar
        dt = bar.datetime.strftime("%Y%m%d %H:%M:%S")
        str_log = "on_bar_min1 symbol=%s open=%s high=%s close=%s low=%s vol=%s dt=%s" % (
            bar.symbol, bar.open, bar.high, bar.close, bar.low, bar.volume, dt)
        self.log(str_log)

    @abstractmethod
    def on_bar_day(self, tiny_bar):
        """收盘时会触发一次日k数据推送"""
        bar = tiny_bar
        dt = bar.datetime.strftime("%Y%m%d %H:%M:%S")
        str_log = "on_bar_day symbol=%s open=%s high=%s close=%s low=%s vol=%s dt=%s" % (
            bar.symbol, bar.open, bar.high, bar.close, bar.low, bar.volume, dt)
        self.log(str_log)

    @abstractmethod
    def on_before_trading(self, date_time):
        """开盘时触发一次回调, 港股是09:30:00"""
        str_log = "on_before_trading - %s" % date_time.strftime('%Y-%m-%d %H:%M:%S')
        self.log(str_log)

    @abstractmethod
    def on_after_trading(self, date_time):
        """收盘时触发一次回调, 港股是16:00:00"""
        str_log = "on_after_trading - %s" % date_time.strftime('%Y-%m-%d %H:%M:%S')
        self.log(str_log)

    def get_kl_min1_am(self, symbol):
        """一分钟k线的array manager数据"""
        return self._quant_frame.get_kl_min1_am(symbol)

    def get_kl_day_am(self, symbol):
        """日k线的array manager数据"""
        return self._quant_frame.get_kl_day_am(symbol)

    def log(self, content):
        """写log的接口"""
        content = self.name + ':' + content
        if self._quant_frame is not None:
            self._quant_frame.writeCtaLog(content)

    def init_strate(self, global_setting, quant_frame, event_engine):
        """TinyQuantFrame 初始化策略的接口"""

        if type(self._quant_frame) is not int:
            return True

        self._quant_frame = quant_frame
        self._event_engine = event_engine
        init_ret = self.__loadSetting(global_setting)

        # 注册事件
        self._event_engine.register(EVENT_BEFORE_TRADING, self.__event_before_trading)
        self._event_engine.register(EVENT_AFTER_TRADING, self.__event_after_trading)
        self._event_engine.register(EVENT_QUOTE_CHANGE, self.__event_quote_change)
        self._event_engine.register(EVENT_CUR_KLINE_BAR, self.__event_cur_kline_bar)

        self.log("init_strate '%s' ret = %s" % (self.name, init_ret))

        return init_ret

    def __loadSetting(self, global_setting):
        # 从json配置中读取数据
        if self.name not in global_setting:
            str_error = "setting.json - no config '%s'!" % self.name
            raise Exception(str_error)

        cta_setting = global_setting[self.name]

        d = self.__dict__
        for key in d.keys():
            if key in cta_setting.keys():
                d[key] = cta_setting[key]

        # check paramlist
        for key in d.keys():
            if d[key] is None:
                str_error = "setting.json - '%s' config no key:'%s'" % (self.name, key)
                raise Exception(str_error)

        return True

    def __event_before_trading(self, event):
        self._market_opened= True
        date_time = datetime.fromtimestamp(int(event.dict_['TimeStamp']))
        self.on_before_trading(date_time)

    def __event_after_trading(self, event):
        self._market_opened= False
        date_time = datetime.fromtimestamp(int(event.dict_['TimeStamp']))

        self.on_after_trading(date_time)

    def __event_quote_change(self, event):
        # 没开盘不向外推送数据
        if not self._market_opened:
            return

        tiny_quote = event.dict_['data']
        self.on_quote_changed(tiny_quote)

    def __event_cur_kline_bar(self, event):
        symbol = event.dict_['symbol']
        bar = event.dict_['data']
        ktype = event.dict_['ktype']

        if ktype == KTYPE_MIN1:
            self.on_bar_min1(bar)
        elif ktype == KTYPE_DAY:
            self.on_bar_day(bar)






