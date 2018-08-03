#-*-coding:utf-8-*-
from futuquant.trade.open_trade_context import *
import pandas

class OrderListQuery(object):
    # 查询今日订单列表 order_list_query

    def __init__(self):
        pandas.set_option('max_columns', 100)
        pandas.set_option('display.width', 1000)

    def test_hk(self):
        host = '127.0.0.1'
        port = 11112
        tradehk_ctx = OpenHKTradeContext(host, port)
        # self.tradehk_ctx = OpenUSTradeContext(host,port)
        ret_code_unlock_trade, ret_data_unlock_trade = tradehk_ctx.unlock_trade(password='123123')
        print('unlock_trade  ret_code= %d, ret_data= %s' % (ret_code_unlock_trade, ret_data_unlock_trade))
        ret_code,ret_data = tradehk_ctx.order_list_query(order_id="", status_filter_list=[], code='', start='', end='',trd_env=TrdEnv.REAL, acc_id=0)

        print(ret_code)
        print(ret_data)

    def test_sh(self):
        host = '127.0.0.1'
        port = 11112
        trade_sh = OpenHKCCTradeContext(host, port)
        trade_sh_m = OpenCNTradeContext(host, port)

        trade_sh.unlock_trade('123123')

        print(trade_sh.order_list_query())
        print(trade_sh_m.order_list_query(trd_env=TrdEnv.SIMULATE))

    def test1(self):
        host = '127.0.0.1'
        port = 11112

        trade_hk = OpenHKTradeContext(host, port)
        trade_us = OpenUSTradeContext(host, port)
        trade_sh_m = OpenCNTradeContext(host, port)

        print(trade_hk.order_list_query(order_id="", status_filter_list=[], code='', start='', end='',
                         trd_env=TrdEnv.SIMULATE, acc_id=0))
        print(trade_us.order_list_query(order_id="", status_filter_list=[], code='', start='', end='',
                                          trd_env=TrdEnv.SIMULATE, acc_id=0))
        print(trade_sh_m.order_list_query(order_id="", status_filter_list=[], code='', start='', end='',
                                        trd_env=TrdEnv.SIMULATE, acc_id=0))


if __name__ == '__main__':
    olq = OrderListQuery()
    # olq.test_sh()
    olq.test1()