# encoding: UTF-8

'''
双均线策略，通过建立m天移动平均线，n天移动平均线，则两条均线必有交点。若m>n，n天平均线“上穿越”m天均线则为买入点，反之为卖出点。
该策略基于不同天数均线的交叉点，抓住股票的强势和弱势时刻，进行交易。
'''

import talib
from futuquant.examples.TinyQuant.TinyStrateBase import *
from futuquant.examples.TinyQuant.TinyQuantFrame import *
from futuquant.quote.open_quote_context import *
from futuquant.trade.open_trade_context import *
import datetime

class TinyStrateMeanLine(TinyStrateBase):
    name = 'tiny_strate_mean_line'
    symbol_pools = ['HK.00700']
    pwd_unlock = '123456'

    def __init__(self):
        super(TinyStrateMeanLine, self).__init__()
        """请在setting.json中配置参数"""
        self.param1 = None
        self.param2 = None
        """0: 空仓 1：满仓"""
        self.flag = 0

    def on_init_strate(self):
        """策略加载完配置"""
        pass

    def on_quote_changed(self, tiny_quote):
        """报价、摆盘实时数据变化时，会触发该回调"""
        pass

    def on_bar_min1(self, tiny_quote):
        """每一分钟触发一次回调"""
        """收盘前五分钟，调用"""
        data = tiny_quote
        symbol = data.symbol
        price = data.open
        #print(price)

        now = datetime.datetime.now()
        work_time = now.replace(hour=15, minute=55, second=0)

        if now >= work_time:
            ma_20 = self.get_sma(20, symbol)
            ma_60 = self.get_sma(60, symbol)
            if ma_20 >= ma_60 and self.flag==0:
                #金叉买入
                self.do_trade(symbol, price, "buy")
                self.flag = 1
            elif ma_20 < ma_60 and self.flag==1:
                #死叉卖出
                self.do_trade(symbol, price, "sell")
                self.flag = 0


    def on_bar_day(self, tiny_quote):
        """收盘时会触发一次日k数据推送"""
        pass

    def on_before_trading(self, date_time):
        """开盘时触发一次回调, 港股是09:30:00"""
        pass

    def on_after_trading(self, date_time):
        """收盘时触发一次回调, 港股是16:00:00"""
        pass

    def get_sma(self, n, symbol):
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        now = datetime.datetime.now()
        end_str = now.strftime('%Y-%m-%d')
        start = now - datetime.timedelta(days=365)
        start_str = start.strftime('%Y-%m-%d')
        temp = quote_ctx.get_history_kline(symbol, start=start_str, end=end_str)
        temp_data = temp[1]['close']
        result = talib.EMA(temp_data, n)
        quote_ctx.close()
        return result.values[-1]

    def do_trade(self, symbol, price, trd_side):
        # 获取账户信息
        trd_ctx = OpenHKTradeContext(host='172.24.31.139', port=11111)
        trd_ctx.unlock_trade(self.pwd_unlock)
        result, accinfo = trd_ctx.accinfo_query()
        if result != 0:
            return
        accinfo_cash = accinfo.cash.values[0]
        accinfo_market_val = accinfo.market_val.values[0]


        if trd_side == 'buy':
            qty = int(accinfo_cash / price)
            trd_ctx.place_order(price=price, qty=qty, code=symbol, trd_side=TrdSide.BUY)
        elif trd_side == 'sell':
            qty = int(accinfo_market_val / price)
            trd_ctx.place_order(price=price, qty=qty, code=symbol, trd_side=TrdSide.SELL)

        trd_ctx.close()


    def test(self):
        pwd_unlock = '123456' #输入交易密码
        trade_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
        _, lock_message = trade_ctx.unlock_trade(pwd_unlock)
        print(lock_message)
        _ , accinfo = trade_ctx.accinfo_query()
        print(trade_ctx.accinfo_query(trd_env='SIMULATE'))
        accinfo_cash = accinfo.cash.values[0]
        accinfo_market_val = accinfo.market_val.values[0]
        print(accinfo_cash, accinfo_market_val)
        trade_ctx.close()

if __name__ == '__main__':
    my_strate = TinyStrateMeanLine()
    #my_strate.test()
    frame = TinyQuantFrame(my_strate)
    frame.run()
