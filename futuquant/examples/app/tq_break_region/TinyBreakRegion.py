# encoding: UTF-8

'''
    实盘策略范例，接口用法见注释及范例代码
'''
import talib
from futuquant.examples.TinyQuant.TinyStrateBase import *
from futuquant.examples.TinyQuant.TinyQuantFrame import *
from futuquant.quote.open_quote_context import *
from futuquant.trade.open_trade_context import *
import datetime

class TinyBreakRegion(TinyStrateBase):
    """策略名称, setting.json中作为该策略配置的key"""
    name = 'tiny_break_region_sample'

    """策略需要用到行情数据的股票池"""
    symbol_pools = ['HK.00700']

    def __init__(self):
        super(TinyBreakRegion, self).__init__()
        """请在setting.json中配置参数"""
        #self.money = None
        #self.chicang = None
        #self.up = 0
        #self.down = 0
        self.before_minute_price = 0



    def on_init_strate(self):
        """策略加载完配置后的回调
        1. 可修改symbol_pools 或策略内部其它变量的初始化
        2. 此时还不能调用futu api的接口
        """

    def on_start(self):

        pass

    def on_quote_changed(self, tiny_quote):
        pass

    def on_bar_min1(self, tiny_bar):
        """每一分钟触发一次回调"""
        bar = tiny_bar
        symbol = bar.symbol
        price = bar.open

        up, down = self.track(symbol)
        now = datetime.datetime.now()
        work_time = now.replace(hour=9, minute=30, second=0)
        if now == work_time:
            self.before_minute_price = price
            return
        if self.before_minute_price == 0:
            self.before_minute_price = price
            return
        if self.before_minute_price < up and price > up:
            self.do_trade(symbol, price, "buy")
        elif self.before_minute_price > down and price < down:
            self.do_trade(symbol, price, "sell")
        self.before_minute_price = price



    def on_bar_day(self, tiny_bar):
        """收盘时会触发一次日k回调"""
        pass




    def on_before_trading(self, date_time):
        """开盘时触发一次回调, 脚本挂机切换交易日时，港股会在09:30:00回调"""
        pass

    def on_after_trading(self, date_time):
        """收盘时触发一次回调, 脚本挂机时，港股会在16:00:00回调"""
        str_log = "on_after_trading - %s" % date_time.strftime('%Y-%m-%d %H:%M:%S')
        self.log(str_log)


    def track(self, symbol):
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11122)
        now = datetime.datetime.now()
        end_str = now.strftime('%Y-%m-%d')
        start = now - datetime.timedelta(days=365)
        start_str = start.strftime('%Y-%m-%d')
        _, temp = quote_ctx.get_history_kline(symbol, start=start_str, end=end_str)
        #print(temp)
        high = temp['high'].values
        low = temp['low'].values
        open = temp['open'].values
        """确定上下轨"""
        '''
        y_amplitude = []
        for i in range(len(high)):
            temp = high[i] - low[i]
            y_amplitude.append(temp)
        '''
        y_amplitude = high - low
        print(y_amplitude)
        y_a_r = y_amplitude[-1] / open[-2]
        if y_a_r > 0.05:
            up_ = open[-1] + 0.5 * y_amplitude[-1]
            down_ = open[-1] - 0.5 * y_amplitude[-1]
        else:
            up_ = open[-1] + 2 / 3 * y_amplitude[-1]
            down_ = open[-1] - 2 / 3 * y_amplitude[-1]
        #print(up_, down_)
        return up_, down_

    def test(self):
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11122)
        print(quote_ctx.unsubscribe(['HK.00700'], [SubType.QUOTE]))
        print(quote_ctx.get_rt_data('HK.00700'))

        quote_ctx.close()

    def do_trade(self, symbol, price, trd_side):
        # 获取账户信息
        trade_ctx = OpenTradeContextBase(host='127.0.0.1', port=11122)
        _, accinfo = trade_ctx.accinfo_query()
        accinfo_cash = accinfo.cash.values[0]
        accinfo_market_val = accinfo.market_val.values[0]
        trade_ctx.close()

        pwd_unlock = '230048' #交易密码
        trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11122)
        trd_ctx.unlock_trade(pwd_unlock)

        if trd_side == 'buy':
            qty = int(accinfo_cash / price)
            trd_ctx.place_order(price=price, qty=qty, code=symbol, trd_side=TrdSide.BUY)
        elif trd_side == 'sell':
            qty = int(accinfo_market_val / price)
            trd_ctx.place_order(price=price, qty=qty, code=symbol, trd_side=TrdSide.SELL)
        trd_ctx.close()


if __name__ == '__main__':
    my_strate = TinyBreakRegion()
    #my_strate.test()
    frame = TinyQuantFrame(my_strate)
    frame.run()
