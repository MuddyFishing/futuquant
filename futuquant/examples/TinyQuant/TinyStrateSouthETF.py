# encoding: UTF-8

'''
   南方东英杠反ETF策略，回测数据见
   https://act.futunn.com/south-etf
'''
import talib
from TinyStrateBase import *

class TinyStrateSouthETF(TinyStrateBase):
    """策略名称, setting.json中作为该策略配置的key"""
    name = 'tiny_strate_south_etf'

    """策略需要用到行情数据的股票池"""
    symbol_pools = []

    def __init__(self):
        super(TinyStrateSouthETF, self).__init__()
        """请在setting.json中配置参数"""
        self.symbol_ref = None
        self.ref_idx = None
        self.cta_call = None
        self.cta_put = None

        self.trade_qty = None
        self.trade_price_idx = None

    def on_init_strate(self):
        """策略加载完配置"""

        # 添加必要的股票，以便能得到相应的股票行情数据
        self.symbol_pools.append(self.symbol_ref)
        if self.cta_call["enable"]:
            self.symbol_pools.append(self.cta_call["symbol"])

        if self.cta_put["enable"]:
            self.symbol_pools.append(self.cta_put["symbol"])

        # call put 的持仓量以及持仓天数
        self.cta_call['pos'] = 0
        self.cta_call['days'] = 0
        self.cta_put['pos'] = 0
        self.cta_put['days'] = 0

        # call put 一天只操作一次，记录当天是否已经操作过
        self.cta_call['done'] = False
        self.cta_put['done'] = False

        # 检查参数: 下单的滑点 / 下单的数量
        if self.trade_price_idx < 1 or self.trade_price_idx > 10:
            raise Exception("conifg trade_price_idx error!")
        if self.trade_qty < 0:
            raise Exception("conifg trade_qty error!")

    def on_start(self):
        """策略启动入口"""
        self.log("on_start")

    def on_quote_changed(self, tiny_quote):
        """报价、摆盘实时数据变化时，会触发该回调"""
        # TinyQuoteData
        if tiny_quote.symbol != self.symbol_ref:
            return

        # 执行策略
        self._process_cta(self.cta_call)
        self._process_cta(self.cta_put)

    def _process_cta(self, cta):
        if not cta['enable'] or cta['done']:
            return

        # 是否要卖出
        if cta['pos'] > 0 and cta['days'] >= cta['days_sell']:
            # TO SEND
            cta['done'] = true
            cta['pos'] = 0
            cta['days'] = 0
            return

        # 计算触发值
        is_call = cta is self.cta_call
        to_buy = False
        if self.ref_idx == 0:
            # 指标参数 0:涨跌幅 1:移动平均线
            quote = self.get_rt_tiny_quote(self.symbol_ref)
            if not quote or quote.preClosePrice <= 0 or quote.lastPrice <= 0:
                return
            if is_call:
                trigger = (quote.lastPrice - quote.preClosePrice)/float(quote.preClosePrice)
            else:
                trigger = (quote.preClosePrice - quote.lastPrice) /float(quote.preClosePrice)
            if trigger >= cta['trigger_per']:
                # TO BUY
                to_buy = True
        else:
            # 移动平均线
            am = self.get_kl_day_am(self.symbol_ref)
            array_close = am.close
            short = self.ema(array_close, cta['trigger_ema_short'], True)
            long = self.ema(array_close, cta['trigger_ema_long'], True)

            if is_call:
                if (short[-2] < long[-2]) and (short[-1] > long[-2]):
                    to_buy = True
            else:
                if (short[-2] > long[-2]) and (short[-1] < long[-2]):
                    to_buy = True

        if to_buy:
            # TO BUY
            symbol = cta['symbol']
            self.log("buy symbol = %s " % symbol)
            cta['done'] = True
            cta['pos'] = self.trade_qty
            cta['days'] = 0

    def on_bar_min1(self, tiny_bar):
        """每一分钟触发一次回调"""
        bar = tiny_bar
        dt = bar.datetime.strftime("%Y%m%d %H:%M:%S")
        str_log = "on_bar_day symbol=%s open=%s high=%s close=%s low=%s vol=%s dt=%s" % (
            bar.symbol, bar.open, bar.high, bar.close, bar.low, bar.volume, dt)
        self.log(str_log)

    def on_bar_day(self, tiny_bar):
        """收盘时会触发一次日k回调"""
        pass

    def on_before_trading(self, date_time):
        """开盘时触发一次回调, 港股是09:30:00"""

        # 开盘的时候检查，如果有持仓，就把持有天数 + 1
        if self.cta_call['pos'] > 0:
            self.cta_call['days'] += 1
        if self.cta_put['pos'] > 0:
            self.cta_put['days'] += 1

        self.cta_call['done'] = False
        self.cta_put['done'] = False

    def on_after_trading(self, date_time):
        """收盘时触发一次回调, 港股是16:00:00"""
        pass

    def ema(self, np_array, n, array=False):
        """移动均线"""
        result = talib.EMA(np_array, n)
        if array:
            return result
        return result[-1]


