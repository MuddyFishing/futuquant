# encoding: UTF-8

'''

'''
from vnpyInc import *
from abc import ABCMeta, abstractmethod
from datetime import datetime

class TinyStrateBase(object):
    """策略frame"""
    name = 'tiny_strate_base'
    symbol_pools = ['HK.00700']

    def __init__(self):
        # 这里没有用None,因为None在 __loadSetting中当作错误参数检查用了
        self._no_use_val = 0
        self._quant_frame = 0
        self._event_engine = 0
        pass

    @abstractmethod
    def on_quote_changed(self, tiny_quote):
        # TinyQuoteData
        data = tiny_quote
        str_log = "on_quote_changed open=%s high=%s close=%s low=%s" % (data.openPrice, data.highPrice, data.lastPrice, data.lowPrice)
        self.writeCtaLog(str_log)

    @abstractmethod
    def on_before_trading(self, date_time):
        str_log = "on_before_trading - %s" % date_time.strftime('%Y-%m-%d %H:%M:%S')
        self.writeCtaLog(str_log)

    @abstractmethod
    def on_after_trading(self, date_time):
        str_log = "on_after_trading - %s" % date_time.strftime('%Y-%m-%d %H:%M:%S')
        self.writeCtaLog(str_log)

    def writeCtaLog(self, content):
        """记录CTA日志"""
        content = self.name + ':' + content
        if self._quant_frame is not None:
            self._quant_frame.writeCtaLog(content)

    def init_strate(self, global_setting, quant_frame, event_engine):

        if type(self._quant_frame) is not int:
            return True

        self._quant_frame = quant_frame
        self._event_engine = event_engine
        init_ret = self.__loadSetting(global_setting)

        # 注册事件
        self._event_engine.register(EVENT_BEFORE_TRADING, self.__event_before_trading)
        self._event_engine.register(EVENT_AFTER_TRADING, self.__event_after_trading)
        self._event_engine.register(EVENT_QUOTE_CHANGE, self.__event_quote_change)
        self.writeCtaLog("init_strate '%s' ret = %s" % (self.name, init_ret))

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
        date_time = datetime.fromtimestamp(int(event.dict_['TimeStamp']))
        self.on_before_trading(date_time)

    def __event_after_trading(self, event):
        date_time = datetime.fromtimestamp(int(event.dict_['TimeStamp']))

        self.on_after_trading(date_time)

    def __event_quote_change(self, event):
        tiny_quote = event.dict_['data']

        self.on_quote_changed(tiny_quote)


        



