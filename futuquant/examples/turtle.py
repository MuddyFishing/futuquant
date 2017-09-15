# -*- coding: utf-8 -*-

import talib as ta   # 请自行安装
import numpy as np
import datetime
import time

from futuquant import *


class Turtle(object):
    """
    Turtle trading system
    """
    # API parameter setting
    api_svr_ip = '119.29.141.202'   # 账户登录的牛牛客户端PC的IP, 本机默认为127.0.0.1
    api_svr_port = 11111            # 富途牛牛端口，默认为11111
    unlock_password = "123456"      # 美股和港股交易解锁密码
    trade_env = 1                   # 0: 真实交易 1: 仿真交易（仿真交易无密码验证，美股暂不支持仿真）

    # initial strategy parameter setting
    short_in_date = 20      # 系统1入市的trailing date
    long_in_date = 55       # 系统2入市的trailing date
    short_out_date = 10     # 系统1 exiting market trailing date
    long_out_date = 20      # 系统2 exiting market trailing date
    dollars_per_share = 1   # 标的股票每波动一个最小单位，1手股票的总价格变化量，在国内最小变化量是0.01元，所以就是0.01×100=1
    loss = 0.1              # 可承受的最大损失率
    adjust = 0.8            # 若超过最大损失率，则调整率为：
    number_days = 20        # 计算N值的天数
    unit_limit = 4          # 最大允许单元
    ratio = 0.8             # 系统1所配金额占总金额比例

    # variable setting
    unit = 1000         # 初始单元
    N = []              # A list storing info of N
    ATR = []            # A list storing info of ATR
    days = 0            # Record the number of days for this trading system
    break_price1 = 0    # 系统1的突破价格
    break_price2 = 0    # 系统2的突破价格
    sys1 = 0            # 系统1建的仓数
    sys2 = 0            # 系统2建的仓数
    system1 = True      # 系统1执行且系统2不执行

    def __init__(self, stock):
        """
        Constructor
        """
        self.stock = stock
        self.quote_ctx, self.trade_ctx = self.context_setting()

    def context_setting(self):
        """
        API trading and quote context setting
        """
        if self.unlock_password == "":
            raise Exception("请先配置交易解锁密码! password: {}".format(self.unlock_password))

        quote_ctx = OpenQuoteContext(host=self.api_svr_ip, port=self.api_svr_port)
        if 'HK.' in self.stock:
            trade_ctx = OpenHKTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
            if self.trade_env == 0:
                ret_code, ret_data = trade_ctx.unlock_trade(self.unlock_password)
                if ret_code == 0:
                    print('解锁交易成功!')
                else:
                    print("请求交易解锁失败, 请确认解锁密码! password: {}".format(self.unlock_password))
        elif 'US.' in self.stock:
            if self.trade_env != 0:
                raise Exception("美股交易接口不支持仿真环境 trade_env: {}".format(self.trade_env))
            trade_ctx = OpenUSTradeContext(host=self.api_svr_ip, port=self.api_svr_port)
        else:
            raise Exception("stock输入错误 stock: {}".format(self.stock))

        return quote_ctx, trade_ctx

    def cal_ATR(self):
        """
        calculate the ATR, which is can replace N
        """
        today = datetime.datetime.today()
        pre_day = (today - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d')
        ret_code, ret_data = self.quote_ctx.get_history_kline(self.stock, start=pre_day)
        if ret_code != 0:
            raise Exception('k线数据获取异常, 请重试: {}'.format(ret_data))

        high = ret_data['high'].values
        low = ret_data['low'].values
        close = ret_data['close'].values

        atr = ta.ATR(high, low, close, timeperiod=14)[-1]
        self.ATR.append(atr)

    def cal_N(self):
        """
        calculate the current N
        """
        today = datetime.datetime.today()
        # 如果交易天数小于等于20天
        if self.days <= self.number_days:
            pre_day = (today - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d')
            ret_code, price = self.quote_ctx.get_history_kline(self.stock, start=pre_day)
            if ret_code != 0:
                raise Exception('k线数据获取异常, 请重试: {}'.format(price))
            lst = []
            for i in range(0, self.days):
                h_l = price['high'][i] - price['low'][i]
                h_c = price['high'][i] - price['close'][i]
                c_l = price['close'][i] - price['low'][i]
                # 计算 True Range
                True_Range = max(h_l, h_c, c_l)
                lst.append(True_Range)

            # 计算前days(小于等于20)天的True_Range平均值，即当前N的值：
            current_N = np.mean(np.array(lst))
            self.N.append(current_N)

        # 如果交易天数超过20天
        else:
            pre_day = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            ret_code, price = self.quote_ctx.get_history_kline(self.stock, start=pre_day)
            if ret_code != 0:
                raise Exception('k线数据获取异常, 请重试: {}'.format(price))

            h_l = price['high'][0] - price['low'][0]
            h_c = price['high'][0] - price['close'][0]
            c_l = price['close'][0] - price['low'][0]
            # Calculate the True Range
            True_Range = max(h_l, h_c, c_l)
            # 计算前number_days（大于20）天的True_Range平均值，即当前N的值：
            current_N = (True_Range + (self.number_days - 1) * self.N[-1]) / self.number_days
            self.N.append(current_N)

    def market_in(self, current_price, cash, in_date):
        """
        入市函数，决定系统1、系统2是否应该入市，更新系统1和系统2的突破价格
        海龟将所有资金分为2部分：一部分资金按系统1执行，一部分资金按系统2执行
        """
        # Get the price for the past "in_date" days
        today = datetime.datetime.today()
        pre_day = (today - datetime.timedelta(days=in_date)).strftime('%Y-%m-%d')
        ret_code, price = self.quote_ctx.get_history_kline(self.stock, start=pre_day)
        if ret_code != 0:
            raise Exception('k线数据获取异常, 请重试: {}'.format(price))

        # Build position if current price is higher than highest in past
        if current_price > max(price['close']):
            # 计算可以买该股票的股数
            num_of_shares = cash / current_price
            if num_of_shares >= self.unit:
                print("PLACE ORDER - stock: {}, price: {}".format(self.stock, current_price))
                if self.system1:
                    if self.sys1 < int(self.unit_limit * self.unit):
                        ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.unit),
                                                                        strcode=self.stock, orderside=0,
                                                                        envtype=self.trade_env)
                        self.sys1 += int(self.unit)
                        self.break_price1 = current_price
                        if not ret_code:
                            print('market_in MAKE BUY ORDER\n\tcode = {} price = {}'
                                  .format(self.stock, current_price))
                        else:
                            print('market_in: MAKE BUY ORDER FAILURE!'.format(ret_data))
                else:
                    if self.sys2 < int(self.unit_limit * self.unit):
                        ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.unit),
                                                                        strcode=self.stock, orderside=0,
                                                                        envtype=self.trade_env)
                        self.sys2 += int(self.unit)
                        self.break_price2 = current_price
                        if not ret_code:
                            print('market_in MAKE BUY ORDER\n\tcode = {} price = {}'
                                  .format(self.stock, current_price))
                        else:
                            print('market_in: MAKE BUY ORDER FAILURE!'.format(ret_data))

    def market_add(self, current_price, cash):
        """
        加仓函数
        """
        if self.system1:
            break_price = self.break_price1
        else:
            break_price = self.break_price2
        # 每上涨0.5N，加仓一个单元
        if current_price >= break_price + 0.5 * self.N[-1]:
            num_of_shares = cash / current_price
            # 加仓
            if num_of_shares >= self.unit:
                print("ADD POSITION - stock: {}, price: {}".format(self.stock, current_price))
                if self.system1:
                    if self.sys1 < int(self.unit_limit * self.unit):
                        ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.unit),
                                                                        strcode=self.stock, orderside=0,
                                                                        envtype=self.trade_env)
                        self.sys1 += int(self.unit)
                        self.break_price1 = current_price
                        if not ret_code:
                            print('market_add MAKE BUY ORDER\n\tcode = {} price = {}'
                                  .format(self.stock, current_price))
                        else:
                            print('market_add: MAKE BUY ORDER FAILURE!'.format(ret_data))
                else:
                    if self.sys2 < int(self.unit_limit * self.unit):
                        ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.unit),
                                                                        strcode=self.stock, orderside=0,
                                                                        envtype=self.trade_env)
                        self.sys2 += int(self.unit)
                        self.break_price2 = current_price
                        if not ret_code:
                            print('market_add MAKE BUY ORDER\n\tcode = {} price = {}'
                                  .format(self.stock, current_price))
                        else:
                            print('market_add: MAKE BUY ORDER FAILURE!'.format(ret_data))

    def market_out(self, current_price, out_date):
        """
        离场函数
        """
        today = datetime.datetime.today()
        pre_day = (today - datetime.timedelta(days=out_date)).strftime('%Y-%m-%d')
        # Function for leaving the market
        ret_code, price = self.quote_ctx.get_history_kline(self.stock, start=pre_day)
        if ret_code != 0:
            raise Exception('k线数据获取异常, 请重试: {}'.format(price))

        # 若当前价格低于前out_date天的收盘价的最小值, 则卖掉所有持仓
        if current_price < min(price['close']):
            print("MARKET OUT - stock: {}, price: {}".format(self.stock, current_price))
            if self.system1:
                if self.sys1 > 0:
                    ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.sys1),
                                                                    strcode=self.stock, orderside=1,
                                                                    envtype=self.trade_env)
                    self.sys1 = 0
                    if not ret_code:
                        print('market_out MAKE BUY ORDER\n\tcode = {} price = {}'
                              .format(self.stock, current_price))
                    else:
                        print('market_out: MAKE SELL ORDER FAILURE: {}'.format(ret_data))
            else:
                if self.sys2 > 0:
                    ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.sys2),
                                                                    strcode=self.stock, orderside=1,
                                                                    envtype=self.trade_env)
                    self.sys2 = 0
                    if not ret_code:
                        print('market_out MAKE BUY ORDER\n\tcode = {} price = {}'
                              .format(self.stock, current_price))
                    else:
                        print('market_out: MAKE SELL ORDER FAILURE: {}'.format(ret_data))

    def stop_loss(self, current_price):
        """
        止损函数
        """
        # 损失大于2N，卖出股票
        if self.system1:
            break_price = self.break_price1
        else:
            break_price = self.break_price2

        # If the price has decreased by 2N, then clear all position
        if current_price < (break_price - 2 * self.N[-1]):
            print("STOP LOSS - stock: {}, price: {}".format(self.stock, current_price))
            if self.system1:
                ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.sys1),
                                                                strcode=self.stock, orderside=1,
                                                                envtype=self.trade_env)
                self.sys1 = 0
                if not ret_code:
                    print('stop_loss MAKE BUY ORDER\n\tcode = {} price = {}'
                          .format(self.stock, current_price))
                else:
                    print('stop_loss: MAKE SELL ORDER FAILURE: {}'.format(ret_data))
            else:
                ret_code, ret_data = self.trade_ctx.place_order(price=current_price, qty=int(self.sys2),
                                                                strcode=self.stock, orderside=1,
                                                                envtype=self.trade_env)
                self.sys2 = 0
                if not ret_code:
                    print('stop_loss MAKE BUY ORDER\n\tcode = {} price = {}'
                          .format(self.stock, current_price))
                else:
                    print('stop_loss: MAKE SELL ORDER FAILURE: {}'.format(ret_data))

    def handle_data(self):
        """
        根据数据判断是否有交易信号产生，并根据信号下单(日线级)
        """
        dt = datetime.datetime.now()  # 当前时间
        ret_code, data = self.quote_ctx.get_market_snapshot([self.stock])
        if ret_code != 0:
            print('市场快照数据获取异常, 正在重试中... {}'.format(data))
            time.sleep(10)
            return
        current_price = data['last_price'][0]  # 当前价格N
        if dt.hour == 9 and dt.minute == 30:
            self.days += 1
            self.cal_N()    # 计算N的值

        if self.days > self.number_days:
            # 当前持有的股票和现金的总价值
            ret_code, acc_info = self.trade_ctx.accinfo_query(envtype=self.trade_env)
            if ret_code != 0:
                raise Exception('账户信息获取失败! 请重试: {}'.format(acc_info))
            value = acc_info['ZQSZ'][0]
            cash = acc_info['KQXJ'][0]     # 可花费的现金
            if self.sys1 == 0 and self.sys2 == 0:
                # 若损失率大于self.loss，则调整（减小）可持有现金和总价值
                if value < (1 - self.loss) * acc_info['ZCJZ'][0]:
                    cash *= self.adjust
                    value *= self.adjust

            # 计算美元波动的价格
            dollar_volatility = self.dollars_per_share * self.N[-1]
            # 依本策略，计算买卖的单位
            self.unit = value * 0.01 / dollar_volatility

            # 系统1的操作
            self.system1 = True
            if self.sys1 == 0:
                self.market_in(current_price, self.ratio * cash, self.short_in_date)
            else:
                self.stop_loss(current_price)
                self.market_add(current_price, self.ratio * cash)
                self.market_out(current_price, self.short_out_date)

            # 系统2的操作
            self.system1 = False
            if self.sys2 == 0:
                self.market_in(current_price, (1 - self.ratio) * cash, self.long_in_date)
            else:
                self.stop_loss(current_price)
                self.market_add(current_price, (1 - self.ratio) * cash)
                self.market_out(current_price, self.long_out_date)


if __name__ == "__main__":
    STOCK = 'HK.00700'

    turtle = Turtle(STOCK)
    print("策略启动成功！")
    while True:
        turtle.handle_data()
        time.sleep(20)
