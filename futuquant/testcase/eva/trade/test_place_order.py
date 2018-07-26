#-*-coding:utf-8-*-
from futuquant import *
from futuquant.trade.open_trade_context import *
from futuquant.testcase.eva.trade.Handler import *
import pandas

class PlaceOrder(object):
    # 下单接口 place_order

    def __init__(self):
        pandas.set_option('max_columns', 100)
        pandas.set_option('display.width', 1000)
    #     # 启动协议加密
    #     SysConfig.set_init_rsa_file('E:/test/testing/conn_key.txt')
    #     SysConfig.enable_proto_encrypt(True)

    def test_sh(self):
        host = '127.0.0.1'  # mac-kathy:172.18.6.144
        port = 11112
        trade_ctx_sh = OpenHKCCTradeContext(host, port)

        #解锁交易
        ret_code_unlock, ret_data_unlock = trade_ctx_sh.unlock_trade('123123')
        print('unlock ret_code = %d'%ret_code_unlock)
        print('unlock ret_data = %s' % ret_data_unlock)
        # 设置监听
        handler_tradeOrder = TradeOrderTest()
        handler_tradeDealtrade = TradeDealTest()
        trade_ctx_sh.set_handler(handler_tradeOrder)
        trade_ctx_sh.set_handler(handler_tradeDealtrade)
        # 开启异步
        trade_ctx_sh.start()

        #下单
        # price = 14.94, qty=700, code='SH.600007'
        # price = 28.8, qty=700, code='SZ.300003'
        #price = 3.512, qty=700, code='SZ.300005'
        ret_code_place_order, ret_data_place_order = trade_ctx_sh.place_order(price = 21, qty=700, code='SZ.300003', trd_side=TrdSide.BUY, order_type=OrderType.NORMAL,adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0)
        print(ret_code_place_order)
        print(ret_data_place_order)


    def test_hk(self):
        host = '127.0.0.1'
        port = 11112
        tradehk_ctx = OpenHKTradeContext(host, port)

        ret_code_unlock_trade, ret_data_unlock_trade = tradehk_ctx.unlock_trade(password='123123')
        print('unlock_trade  ret_code= %d, ret_data= %s' % (ret_code_unlock_trade, ret_data_unlock_trade))
        # 设置监听
        handler_tradeOrder = TradeOrderTest()
        handler_tradeDealtrade = TradeDealTest()
        tradehk_ctx.set_handler(handler_tradeOrder)
        tradehk_ctx.set_handler(handler_tradeDealtrade)
        # 开启异步
        tradehk_ctx.start()
        #下单
        ret_code, ret_data = tradehk_ctx.place_order(price = 0.2, qty= 1000, code= 'HK.00700', trd_side= TrdSide.BUY, order_type= OrderType.NORMAL, adjust_limit=0, trd_env= TrdEnv.REAL,acc_id=0)
        print('真实环境',ret_code)
        print('真实环境',ret_data)

    def test_us(self):
        host = '127.0.0.1'
        port = 11111
        self.tradeus_ctx = OpenUSTradeContext(host,port)
        ret_code_unlock_trade, ret_data_unlock_trade = self.tradeus_ctx.unlock_trade(password='123123')
        print('unlock_trade  ret_code= %d, ret_data= %s' % (ret_code_unlock_trade, ret_data_unlock_trade))
        # 设置监听
        handler_tradeOrder = TradeOrderTest()
        handler_tradeDealtrade = TradeDealTest()
        self.tradeus_ctx.set_handler(handler_tradeOrder)
        self.tradeus_ctx.set_handler(handler_tradeDealtrade)
        # 开启异步
        self.tradeus_ctx.start()

        code = 'US.AAPL'
        price = 120
        qty = 2644
        trd_side = TrdSide.SELL
        order_type = OrderType.NORMAL
        # NORMAL = "NORMAL"  # 普通订单(港股的增强限价单、A股限价委托、美股的限单)
        # MARKET = "MARKET"  # 市价，目前仅美股
        # ABSOLUTE_LIMIT = "ABSOLUTE_LIMIT"  # 港股_限价(只有价格完全匹配才成交)
        # AUCTION = "AUCTION"  # 港股_竞价
        # AUCTION_LIMIT = "AUCTION_LIMIT"  # 港股_竞价限价
        # SPECIAL_LIMIT = "SPECIAL_LIMIT"  # 港股_特别限价(即市价IOC, 订单到达交易所后，或全部成交， 或部分成交再撤单， 或下单失败)
        adjust_limit = 0
        trd_env = TrdEnv.REAL
        acc_id = 0
        ret_code, ret_data = self.tradeus_ctx.place_order(price, qty, code, trd_side, order_type, adjust_limit, trd_env,acc_id)
        print('place_order  ret_code= %d ,ret_data =\n%s' % (ret_code, str(ret_data)))


    def test1(self):
        host = '127.0.0.1'
        port = 11112

        trade_hk = OpenHKTradeContext(host, port)
        trade_us = OpenUSTradeContext(host, port)
        trade_sh_m = OpenCNTradeContext(host, port)

        ret_code_hk ,ret_data_hk = trade_hk.place_order(price = 0.111, qty = 10000, code = 'HK.61162', trd_side=TrdSide.BUY, order_type=OrderType.NORMAL,
                    adjust_limit=0, trd_env=TrdEnv.SIMULATE, acc_id=0)
        print('模拟交易',ret_code_hk)
        print('模拟交易',ret_data_hk)

        # price = 3.04, qty = 10, code = 'US.DDE'
        # price = 192, qty = 10, code = 'US.AAPL'
        # print(trade_us.place_order(price = 190, qty = 1, code = 'US.AAPL', trd_side=TrdSide.BUY,
        #                            order_type=OrderType.NORMAL,
        #                            adjust_limit=0, trd_env=TrdEnv.SIMULATE, acc_id=0))

        # price = 9.62, qty = 200, code = 'SZ.002078'
        # price=10.2, qty=200, code='SH.601007'
        # print(trade_sh_m.place_order(price=9.37, qty=100, code='SH.000001', trd_side=TrdSide.BUY,
        #                            order_type=OrderType.NORMAL,
        #                            adjust_limit=0, trd_env=TrdEnv.SIMULATE, acc_id=0))

    def test2(self):
        host = '127.0.0.1'
        port = 11112
        trade_hk_real = OpenHKTradeContext(host, port)
        #结果交易
        ret_code_unlock_trade, ret_data_unlock_trade = trade_hk_real.unlock_trade(password='123123')
        print('unlock_trade  ret_code= %d, ret_data= %s' % (ret_code_unlock_trade, ret_data_unlock_trade))
        # 设置监听
        handler_tradeOrder = TradeOrderTest()
        handler_tradeDealtrade = TradeDealTest()
        trade_hk_real.set_handler(handler_tradeOrder)
        trade_hk_real.set_handler(handler_tradeDealtrade)
        # 开启异步
        trade_hk_real.start()
        # 下单
        ret_code, ret_data = trade_hk_real.place_order(price=0.2, qty=1000, code='HK.00700', trd_side=TrdSide.BUY,
                                                     order_type=OrderType.NORMAL, adjust_limit=0, trd_env=TrdEnv.REAL,
                                                     acc_id=0)
        print('真实环境', ret_code)
        print('真实环境', ret_data)
        #-------------------------------------------------------
        trade_hk_simulate = OpenHKTradeContext(host, port)
        ret_code_hk, ret_data_hk = trade_hk_simulate.place_order(price=0.111, qty=10000, code='HK.61162', trd_side=TrdSide.BUY,
                                                        order_type=OrderType.NORMAL,
                                                        adjust_limit=0, trd_env=TrdEnv.SIMULATE, acc_id=0)
        print('模拟交易', ret_code_hk)
        print('模拟交易', ret_data_hk)



if __name__ == '__main__':
    po = PlaceOrder()
    po.test2()