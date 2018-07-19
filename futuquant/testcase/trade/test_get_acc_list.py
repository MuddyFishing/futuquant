#-*-coding:utf-8-*-

from futuquant import *

class GetAccList(object):
    '''获取交易业务账户列表'''

    def test_hk(self):
        host = '127.0.0.1'  # mac-kathy:172.18.6.144
        port = 11113
        trade_ctx_hk = OpenHKTradeContext(host, port)
        ret_code_acc_list, ret_data_acc_list = trade_ctx_hk.get_acc_list()
        print(ret_code_acc_list)
        print(ret_data_acc_list)

    def test_sh(self):
        host = '127.0.0.1'  # mac-kathy:172.18.6.144
        port = 11113
        trade_ctx_sh = OpenHKCCTradeContext(host, port)
        # 获取账户id 100068 281756468867335908
        ret_code_acc_list, ret_data_acc_list = trade_ctx_sh.get_acc_list()
        print(ret_code_acc_list)
        print(ret_data_acc_list)


if __name__ == '__main__':
    gal = GetAccList()
    gal.test_hk()