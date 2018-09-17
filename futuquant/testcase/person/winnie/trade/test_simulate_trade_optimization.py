# -*- coding: utf-8 -*-
import time
from futuquant import *
from futuquant.testcase.person.winnie.trade.Handler import *


class SimulateTradeOptimization(object):
    def test_simulate_trade_hk_get_position_and_funds(self):
        trade_ctx_hk = OpenHKTradeContext(host='127.0.0.1', port=11111)
        '''
        执行步骤：
        0、获取持仓和资金
        1、下单
        2、sleep 30秒
        3、获取持仓和资金
        '''
        ret_code_fund, ret_data_fund_before = trade_ctx_hk.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret_code_fund is RET_ERROR:
            return
        print(ret_data_fund_before)
        ret_code_posi, ret_data_posi_before = trade_ctx_hk.position_list_query(code='HK.00700', trd_env=TrdEnv.SIMULATE)
        if ret_code_posi is RET_ERROR:
            return
        print(ret_data_posi_before)
        pwd_unlock = '123123'
        trade_ctx_hk.unlock_trade(pwd_unlock)
        ret_code, ret_data = trade_ctx_hk.place_order(price=200, qty=100, code='HK.00700',
                                                      trd_side=TrdSide.BUY, trd_env=TrdEnv.SIMULATE)
        if ret_code is RET_ERROR:
            return
        time.sleep(30)
        ret_code, ret_data_fund_after = trade_ctx_hk.accinfo_query(trd_env=TrdEnv.SIMULATE)
        if ret_code is RET_ERROR:
            return
        print(ret_data_fund_after)
        ret_code_posi, ret_data_posi_after = trade_ctx_hk.position_list_query(code='HK.00700', trd_env=TrdEnv.SIMULATE)
        if ret_code_posi is RET_ERROR:
            return
        print(ret_data_posi_after)

    def test_push_order_state(self):
        trade_ctx_hk = OpenHKTradeContext(host='127.0.0.1', port=11111)
        handler_tradeOrder = TradeOrderTest()
        handler_tradeDealtrade = TradeDealTest()
        trade_ctx_hk.set_handler(handler_tradeOrder)
        trade_ctx_hk.set_handler(handler_tradeDealtrade)
        # 开启异步
        trade_ctx_hk.start()

        # ret_code, ret_data = trade_ctx_hk.place_order(price=2, qty=5000, code='HK.00434',
        #                                               trd_side=TrdSide.SELL, trd_env=TrdEnv.SIMULATE)
        # print(ret_data)
        print(trade_ctx_hk.order_list_query(trd_env=TrdEnv.SIMULATE))


if __name__ == '__main__':
    sto = SimulateTradeOptimization()
    sto.test_push_order_state()