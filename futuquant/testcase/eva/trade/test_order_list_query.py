#-*-coding:utf-8-*-
from futuquant.trade.open_trade_context import *
import pandas

class OrderListQuery(object):
    # 查询今日订单列表 order_list_query

    def __init__(self):
        pandas.set_option('max_columns', 100)
        pandas.set_option('display.width', 1000)

    def test1(self):
        host = '127.0.0.1'
        port = 11112
        self.tradehk_ctx = OpenHKTradeContext(host, port)
        # self.tradehk_ctx = OpenUSTradeContext(host,port)
        ret_code_unlock_trade, ret_data_unlock_trade = self.tradehk_ctx.unlock_trade(password='123123')
        print('unlock_trade  ret_code= %d, ret_data= %s' % (ret_code_unlock_trade, ret_data_unlock_trade))
        ret_code,ret_data = self.tradehk_ctx.order_list_query(order_id="", status_filter_list=[], code='', start='', end='',trd_env=TrdEnv.REAL, acc_id=0)
        #281756455982434220 现金0268
        #281756457982434020  现金0178
        #281756455982434020  融资0068

        pandas.set_option('display.width', 3000)
        print(ret_code)
        print(ret_data)

    def test_sh(self):
        host = '127.0.0.1'  # mac-kathy:172.18.6.144
        port = 11112
        trade_ctx_sh = OpenHKCCTradeContext(host, port)
        trade_ctx_sh.unlock_trade('123123')
        pandas.set_option('display.width', 3000)
        pandas.set_option('max_columns', 100)
        print(trade_ctx_sh.order_list_query())


if __name__ == '__main__':
    olq = OrderListQuery()
    olq.test1()