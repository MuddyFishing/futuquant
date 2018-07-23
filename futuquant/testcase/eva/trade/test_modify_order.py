#-*-coding:utf-8-*-

from futuquant.trade.open_trade_context import *
from futuquant.quote.open_quote_context import *

class ModifyOrder(object):

    def test1(self):
        host = '127.0.0.1'   #mac-kathy:172.18.6.144
        port = 11112
        self.trade_ctx_hk = OpenHKTradeContext(host, port)
        ret_code_unlock_trade, ret_data_unlock_trade = self.trade_ctx_hk.unlock_trade(password='123123')
        print('unlock_trade  ret_code= %d, ret_data= %s' % (ret_code_unlock_trade, ret_data_unlock_trade))
        modify_order_op = ModifyOrderOp.NORMAL
        order_id = '4781797335570056618'
        qty = 100
        price = 17.9
        acc_id = 0
        #281756455982434220 现金0268
        #281756457982434020  现金0178
        #281756455982434020  融资0068
        ret_code, ret_data = self.trade_ctx_hk.modify_order(modify_order_op, order_id, qty, price)   #, qty, price, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=acc_id
        print(ret_code)
        print(ret_data)

    def test_sh(self):

        host = '127.0.0.1'  # mac-kathy:172.18.6.144
        port = 11113
        trade_ctx_sh = OpenHKCCTradeContext(host, port)
        trade_ctx_sh.unlock_trade('123123')

        print(trade_ctx_sh.modify_order(modify_order_op= ModifyOrderOp.CANCEL, order_id= '4781797335570056618', qty = 0, price = 0.123, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0))

if __name__ == '__main__':
    mo = ModifyOrder()
    mo.test_sh()