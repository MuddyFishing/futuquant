#-*-coding:utf-8-*-
from futuquant.trade.open_trade_context import *
import pandas

class AccinfoQuery(object):
    # 查询账户信息 accinfo_query

    def __init__(self):
        pandas.set_option('max_columns',100)
        pandas.set_option('display.width',1000)

    def test1(self):
        host = '127.0.0.1'
        port = 11113
        # tradehk_ctx = OpenHKTradeContext(host, port)
        tradehk_ctx = OpenUSTradeContext(host, port)
        ret_code_unlock_trade, ret_data_unlock_trade = tradehk_ctx.unlock_trade(password='123123')
        print('unlock_trade  ret_code= %d, ret_data= %s' % (ret_code_unlock_trade, ret_data_unlock_trade))
        ret_code_acc_list ,ret_data_acc_list = tradehk_ctx.get_acc_list()
        acc_list = ret_data_acc_list['acc_id'].tolist()
        for acc in acc_list:
            print('acc = %s'%acc)
            print(tradehk_ctx.accinfo_query(trd_env=TrdEnv.REAL, acc_id=acc))


    def test_sh(self):
        host = '127.0.0.1'  # mac-kathy:172.18.6.144
        port = 11113
        trade_ctx_sh = OpenHKCCTradeContext(host, port)

        # 解锁交易
        ret_code_unlock, ret_data_unlock = trade_ctx_sh.unlock_trade('123123')
        print('unlock ret_code = %d' % ret_code_unlock)
        print('unlock ret_data = %s' % ret_data_unlock)
        # 获取账户资金数据
        ret_code_accinfo, ret_data_accinfo = trade_ctx_sh.accinfo_query(trd_env=TrdEnv.REAL, acc_id=281756468867335908)
        print(ret_code_accinfo)
        print(ret_data_accinfo)



if __name__ == '__main__':
    aq = AccinfoQuery()
    aq.test1()
