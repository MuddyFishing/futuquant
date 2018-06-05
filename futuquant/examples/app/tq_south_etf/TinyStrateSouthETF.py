# encoding: UTF-8

'''
   南方东英杠反ETF策略，回测数据见
   https://act.futunn.com/south-etf
'''
import talib
import time
from futuquant.examples.TinyQuant.TinyStrateBase import *

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
        self._last_dt_process = 0

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

        # 记录当天操作的订单id
        self.cta_call['order_id'] = ''
        self.cta_put['order_id'] = ''

        # 检查参数: 下单的滑点 / 下单的数量
        if self.trade_price_idx < 1 or self.trade_price_idx > 5:
            raise Exception("conifg trade_price_idx error!")
        if self.trade_qty < 0:
            raise Exception("conifg trade_qty error!")

    def on_start(self):
        """策略启动入口"""
        # 读取用户现有帐户持仓信息， 数量不超过config中指定的交易数量 'trade_qty'
        for cta in [self.cta_call, self.cta_put]:
            pos = self.get_tiny_position(cta['symbol'])
            if pos is not None:
                valid_pos = pos.position - pos.frozen
                valid_pos = valid_pos if valid_pos > 0 else 0
                valid_pos = self.trade_qty if valid_pos > self.trade_qty else valid_pos
                cta['pos'] = valid_pos

        self.log("on_start")

    def on_quote_changed(self, tiny_quote):
        """报价、摆盘实时数据变化时，会触发该回调"""

        # TinyQuoteData
        if tiny_quote.symbol != self.symbol_ref:
            return

        # 减少计算频率，每x秒一次
        dt_now = time.time()
        if dt_now - self._last_dt_process < 2:
            return
        self._last_dt_process = dt_now

        # 执行策略
        self._process_cta(self.cta_call)
        self._process_cta(self.cta_put)

    def _process_cta(self, cta):
        if not cta['enable'] or cta['done']:
            return

        cta_symbol = cta['symbol']

        # 是否要卖出
        if cta['pos'] > 0 and cta['days'] >= cta['days_sell']:
            # TO SELL
            price = self._get_splip_sell_price(cta_symbol)
            volume = cta['pos']
            if price > 0:
                ret, data = self.sell(price, volume, cta_symbol)
                # 安全起见，一天只做一次交易操作, 失败也忽略
                cta['done'] = True
                if 0 == ret:
                    cta['order_id'] = data
                self.log("sell price=%s volume=%s symbol=%s ret=%s , err=%s" % (price, volume, cta_symbol, ret, (data if 0 != ret else "")))
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
                to_buy = True
        else:
            # 移动平均线
            am = self.get_kl_day_am(self.symbol_ref)
            array_close = am.close
            short = self.ema(array_close, cta['trigger_ema_short'], True)
            long = self.ema(array_close, cta['trigger_ema_long'], True)

            if is_call:
                if (short[-2] < long[-2]) and (short[-1] > long[-1]):
                    to_buy = True
            else:
                if (short[-2] > long[-2]) and (short[-1] < long[-1]):
                    to_buy = True

        if to_buy and 0 == cta['pos']:  # 空仓才买入
            # TO BUY
            price = self._get_splip_buy_price(cta_symbol)
            volume = self.trade_qty
            if price > 0:
                ret, data = self.buy(price, volume, cta_symbol)
                # 安全起见，一天只做一次交易操作, 失败也忽略
                cta['done'] = True
                if 0 == ret:
                    cta['order_id'] = data
                self.log("buy price=%s volume=%s symbol=%s ret=%s , err=%s" %(price, volume, cta_symbol, ret, (data if 0!=ret else "")))

    def on_bar_min1(self, tiny_bar):
        """每一分钟触发一次回调"""
        bar = tiny_bar
        str_dt = bar.datetime.strftime("%Y%m%d %H:%M:%S")
        str_log = "on_bar_min1 symbol=%s dt=%s open=%s high=%s close=%s low=%s vol=%s" % (
            bar.symbol, str_dt, bar.open, bar.high, bar.close, bar.low, bar.volume)
        self.log(str_log)

    def on_bar_day(self, tiny_bar):
        """收盘时会触发一次日k回调"""
        pass

    def on_before_trading(self, date_time):
        """开盘的时候检查，如果有持仓，就把持有天数 + 1"""

        if self.cta_call['pos'] > 0:
            self.cta_call['days'] += 1
        if self.cta_put['pos'] > 0:
            self.cta_put['days'] += 1

        self.cta_call['done'] = False
        self.cta_put['done'] = False

    def on_after_trading(self, date_time):
        """收盘的时候更新持仓信息"""

        self._update_cta_pos(self.cta_call)
        self._update_cta_pos(self.cta_put)

    def ema(self, np_array, n, array=False):
        """移动均线"""
        if n < 2:
            result = np_array
        else:
            result = talib.EMA(np_array, n)
        if array:
            return result
        return result[-1]

    def _get_splip_buy_price(self, symbol):
        quote = self.get_rt_tiny_quote(symbol)
        if quote is None:
            return 0
        index = self.trade_price_idx
        return quote.__dict__['askPrice%s' % index]

    def _get_splip_sell_price(self, symbol):
        quote = self.get_rt_tiny_quote(symbol)
        if quote is None:
            return 0
        index = self.trade_price_idx
        return quote.__dict__['bidPrice%s' % index]

    def _update_cta_pos(self, cta):
        order_id = cta['order_id']
        if not order_id:
            return

        for x in range(3):
            ret, data = self.get_tiny_trade_order(order_id)
            if 0 != ret:
                continue
            if data.direction == TRADE_DIRECT_BUY:
                cta['pos'] = data.trade_volume
                cta['days'] = 0
                cta['order_id'] = ''
            elif data.direction == TRADE_DIRECT_SELL:
                cta['pos'] -= data.trade_volume
                # 如果全部卖出, 将days置为0, 否则第二天继续卖
                if cta['pos'] <= 0:
                    cta['days'] = 0
                cta['order_id'] = ''
            else:
                raise Exception("_update_cta_pos error!")
            break













