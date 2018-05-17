# -*- coding: utf-8 -*-
"""
    跟踪止损:跟踪止损是一种更高级的条件单，需要指定如下参数，以便制造出移动止损价
    跟踪止损的详细介绍：https://www.futu5.com/faq/topic214
"""

import os
import sys
from math import floor

import matplotlib.pyplot as plt
import numpy as np
from time import sleep

sys.path.append(os.path.split(os.path.abspath(os.path.pardir))[0])

import futuquant as ft
from emailplugin import EmailNotification
from stocksell import simple_sell, smart_sell


class TrailingMethod(object):
    DROP_ABS = "DROP_ABS"  # 绝对值降低
    DROP_PER = "DROP_PER"  # 百分比降低


class SellMethod(object):
    SIMPLE_SELL = "SIMPLE_SELL"
    SMART_SELL = "SMART_SELL"


class TrailingStopHandler(ft.StockQuoteHandlerBase):
    """"跟踪止损数据回调类"""

    def __init__(self, quote_ctx, is_hk_trade, method, drop):
        super(ft.StockQuoteHandlerBase, self).__init__()
        self.quote_ctx = quote_ctx
        self.is_hk_trade = is_hk_trade
        self.method = method
        self.drop = drop
        self.finished = False
        self.stop = None
        self.price_lst = []
        self.stop_lst = []
        self.time_lst = []

        if self.method not in [TrailingMethod.DROP_ABS, TrailingMethod.DROP_PER]:
            raise Exception("trailing method is error!")

    def on_recv_rsp(self, rsp_str):
        """数据接收回调函数"""
        ret, content = super(TrailingStopHandler, self).on_recv_rsp(rsp_str)
        if ret != ft.RET_OK:
            print('StockQuote error {}'.format(content))
            return ret, content
        if self.finished:
            return ret, content
        ret, data = self.quote_ctx.get_global_state()
        if ret != ft.RET_OK:
            print('获取全局状态失败')
            trading = False
        else:
            hk_trading = (data['market_hk'] == ft.MarketState.MORNING or data['market_hk'] == ft.MarketState.AFTERNOON)
            us_trading = (data['market_us'] == ft.MarketState.MORNING)
            trading = hk_trading if self.is_hk_trade else us_trading

        if not trading:
            print('不处在交易时间段')
            return ft.RET_OK, content
        last_price = content.iloc[0]['last_price']

        if self.stop is None:
            self.stop = last_price - self.drop if self.method == TrailingMethod.DROP_ABS else last_price * (1 - self.drop)
        elif (self.stop + self.drop < last_price) if self.method == TrailingMethod.DROP_ABS else (self.stop < last_price * (1 - self.drop)):
            self.stop = last_price - self.drop if self.method == TrailingMethod.DROP_ABS else last_price * (1 - self.drop)
        elif self.stop >= last_price:
            # 交易己被触发
            self.finished = True
            print('交易被触发')

        self.price_lst.append(last_price)
        self.stop_lst.append(self.stop)
        print('last_price is {}, stop is {}'.format(last_price, self.stop))

        return ft.RET_OK, content


def trailing_stop(api_svr_ip='127.0.0.1', api_svr_port=11111, unlock_password="", code='HK.00700',
                  trade_env=ft.TrdEnv.SIMULATE, method=TrailingMethod.DROP_ABS, drop=1.0, volume=100,
                  how_to_sell=SellMethod.SMART_SELL, diff=0, rest_time=2,
                  enable_email_notification=False, receiver=''):
    """
    止损策略函数
    :param api_svr_ip: (string)ip
    :param api_svr_port: (int)port
    :param unlock_password: (string)交易解锁密码, 必需修改! 模拟交易设为一个非空字符串即可
    :param code: (string)股票
    :param trade_env: ft.TrdEnv.REAL: 真实交易 ft.TrdEnv.SIMULATE: 模拟交易
    :param method: method == TrailingMethod.DROP_ABS: 股票下跌drop价格就会止损  railingMethod.DROP_PER: 股票下跌drop的百分比就会止损
    :param drop: method == TrailingMethod.DROP_ABS, 股票下跌的价格   method == TrailingMethod.DROP_PER，股票下跌的百分比，0.01表示下跌1%则止损
    :param volume: 需要卖掉的股票数量
    :param how_to_sell: 以何种方式卖出股票， SellMethod 类型
    :param diff: 默认为0，当how_to_sell为SellMethod.DROP_ABS时，以(市价-diff)的价格卖出
    :param rest_time: 每隔REST_TIME秒，会检查订单状态, 需要>=2
    :param enable_email_notification: 激活email功能
    :param receiver: 邮件接收者
    """
    EmailNotification.set_enable(enable_email_notification)

    if how_to_sell not in [SellMethod.SIMPLE_SELL, SellMethod.SMART_SELL]:
        raise Exception('how_to_sell value error')

    if method not in [TrailingMethod.DROP_ABS, TrailingMethod.DROP_PER]:
        raise Exception('method value error')

    quote_ctx = ft.OpenQuoteContext(host=api_svr_ip, port=api_svr_port)
    is_hk_trade = 'HK.' in code
    if is_hk_trade:
        trade_ctx = ft.OpenHKTradeContext(host=api_svr_ip, port=api_svr_port)
    else:
        trade_ctx = ft.OpenUSTradeContext(host=api_svr_ip, port=api_svr_port)

    if unlock_password == "":
        raise Exception('请先配置交易密码')

    ret, data = trade_ctx.unlock_trade(unlock_password)
    if ret != ft.RET_OK:
        raise Exception('解锁交易失败')

    ret, data = trade_ctx.position_list_query(trd_env=trd_env)
    if ret != ft.RET_OK:
        raise Exception("无法获取持仓列表")

    try:
        qty = data[data['code'] == code].iloc[0]['qty']
    except:
        raise Exception('你没有持仓！无法买卖')

    qty = int(qty)
    if volume == 0:
        volume = qty
    if volume < 0:
        raise Exception('volume lower than  0')
    elif qty < volume:
        raise Exception('持仓不足')

    ret, data = quote_ctx.get_market_snapshot(code)
    if ret != ft.RET_OK:
        raise Exception('获取lot size失败')
    lot_size = data.iloc[0]['lot_size']

    if volume % lot_size != 0:
        raise Exception('volume 必须是{}的整数倍'.format(lot_size))

    ret, data = quote_ctx.subscribe(code, ft.SubType.QUOTE)
    if ret != ft.RET_OK:
        raise Exception('订阅QUOTE错误: error {}:{}'.format(ret, data))

    ret, data = quote_ctx.subscribe(code, ft.SubType.ORDER_BOOK)
    if ret != ft.RET_OK:
        print('error {}:{}'.format(ret, data))
        raise Exception('订阅order book失败: error {}:{}'.format(ret, data))

    if diff:
        if is_hk_trade:
            ret, data = quote_ctx.get_order_book(code)
            if ret != ft.RET_OK:
                raise Exception('获取order book失败: cannot get order book'.format(data))

            min_diff = round(abs(data['Bid'][0][0] - data['Bid'][1][0]), 3)
            if floor(diff / min_diff) * min_diff != diff:
                raise Exception('diff 应是{}的整数倍'.format(min_diff))
        else:
            if round(diff, 2) != diff:
                raise Exception('美股价差保留2位小数{}->{}'.format(diff, round(diff, 2)))

    if method == TrailingMethod.DROP_ABS:
        if is_hk_trade:
            if floor(drop / min_diff) * min_diff != drop:
                raise Exception('drop必须是{}的整数倍'.format(min_diff))
        else:
            if round(drop, 2) != drop:
                raise Exception('drop必须保留2位小数{}->{}'.format(drop, round(drop, 2)))

    elif method == TrailingMethod.DROP_PER:
        if drop < 0 or drop > 1:
            raise Exception('drop must in [0, 1] if method is DROP_PER')

    trailing_stop_handler = TrailingStopHandler(quote_ctx, is_hk_trade, method, drop)
    quote_ctx.set_handler(trailing_stop_handler)
    quote_ctx.start()
    while True:
        if trailing_stop_handler.finished:
            # sell the stock
            qty = volume
            sell_price = trailing_stop_handler.stop
            while qty > 0:
                if how_to_sell == SellMethod.SIMPLE_SELL:
                    data = simple_sell(quote_ctx, trade_ctx, code, sell_price - diff, qty, trade_env, ft.OrderType.SPECIAL_LIMIT)
                else:
                    data = smart_sell(quote_ctx, trade_ctx, code, qty, trade_env, ft.OrderType.SPECIAL_LIMIT)
                if data is None:
                    print('下单失败')
                    EmailNotification.send_email(receiver, '下单失败', '股票代码{}，数量{}'.format(code, volume))
                    sleep(rest_time)
                    continue

                order_id = data.iloc[0]['order_id']
                sleep(rest_time)

                while True:
                    ret, data = trade_ctx.order_list_query(order_id=order_id, trd_env=trade_env)
                    if ret != ft.RET_OK:
                        sleep(rest_time)
                        continue

                    status = data.iloc[0]['order_status']
                    dealt_qty = int(data.iloc[0]['dealt_qty'])
                    order_price = data.iloc[0]['price']
                    qty -= dealt_qty

                    if status == ft.OrderStatus.FILLED_ALL:
                        print('全部成交:股票代码{}, 成交总数{}，价格{}'.format(code, dealt_qty, order_price))
                        EmailNotification.send_email(receiver, '全部成交', '股票代码{}，成交总数{}，价格{}'
                                                     .format(code, dealt_qty, order_price))
                        break
                    elif status == ft.OrderStatus.FILLED_PART:
                        print('部分成交:股票代码{}，成交总数{}，价格{}'.format(code, dealt_qty, order_price))
                        EmailNotification.send_email(receiver, '部分成交', '股票代码{}，成交总数{}，价格{}'
                                                     .format(code, dealt_qty, order_price))
                        break
                    elif status == ft.OrderStatus.FAILED or status == ft.OrderStatus.SUBMIT_FAILED or \
                                    status == ft.OrderStatus.CANCELLED_ALL or status == ft.OrderStatus.DELETED:
                        break
                    else:
                        trade_ctx.modify_order(ft.ModifyOrderOp.CANCEL, order_id, 0, 0)
                        sleep(rest_time)
                        continue

                if how_to_sell == SellMethod.SIMPLE_SELL:
                    ret, data = quote_ctx.get_order_book(code)
                    if ret != ft.RET_OK:
                        raise Exception('获取order_book失败')
                    sell_price = data['Bid'][0][0]

            # draw price and stop
            price_lst = trailing_stop_handler.price_lst
            plt.plot(np.arange(len(price_lst)), price_lst)
            stop_list = trailing_stop_handler.stop_lst
            plt.plot(np.arange(len(stop_list)), stop_list)
            break

    quote_ctx.close()
    trade_ctx.close()


if __name__ == '__main__':
    # 全局参数配置
    ip = '127.0.0.1'
    port = 11111
    unlock_pwd = "979899"
    code = 'HK.00700'  # 'US.BABA' #'HK.00700'
    trd_env = ft.TrdEnv.REAL

    trailing_method = TrailingMethod.DROP_PER
    trailing_drop = 0.03   # 3%
    vol = 0
    how_to_sell = SellMethod.SMART_SELL
    diff = 0
    rest_time = 2  # 每隔REST_TIME秒，会检查订单状态, 需要>=2

    # 邮件通知参数
    enable_email = True
    receiver_email = 'your receive email'

    trailing_stop(ip, port, unlock_pwd, code, trd_env, trailing_method, trailing_drop, vol,
                  how_to_sell, diff, rest_time, enable_email, receiver_email)

