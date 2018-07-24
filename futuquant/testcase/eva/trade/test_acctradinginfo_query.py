#-*-coding:utf-8-*-

from futuquant import *
import pandas

class AccTradeInfoQuery(object):

    def test1(self):
        pandas.set_option('max_columns', 1000)
        pandas.set_option('display.width', 1000)

        # trade_ctx_sh = OpenHKTradeContext(host = '127.0.0.1',port=11112)
        trade_ctx = OpenUSTradeContext(host='127.0.0.1', port=11113)
        print(trade_ctx.unlock_trade('123123'))
        ret_code, ret_data = trade_ctx.acctradinginfo_query(order_type = OrderType.NORMAL, code='BABA', price=192.67, order_id=0, adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=281756460277401516)
        print(ret_code)
        print(ret_data)


if __name__ == '__main__':
    atiq = AccTradeInfoQuery()
    atiq.test1()