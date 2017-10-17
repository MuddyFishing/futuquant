# -*- coding: utf-8 -*-
"""
Examples for use the python functions: get push data
"""
from futuquant.open_context import *

class USOrderPushHandler(USTradeOrderHandlerBase):
    """
    美股定单
    """
    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, content = super(USOrderPushHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("USOrderPushHandler: error, msg: %s " % content)
            return RET_ERROR, content
        print("USOrderPushHandler\n", content)
        return RET_OK, content


class HKOrderPushHandler(HKTradeOrderHandlerBase):
    """
    港股定单
    """
    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, content = super(HKOrderPushHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("HKOrderPushHandler: error, msg: %s " % content)
            return RET_ERROR, content
        print("HKOrderPushHandler\n", content)
        return RET_OK, content

if __name__ == "__main__":
    api_ip = '127.0.0.1' #''119.29.141.202'
    api_port = 11111
    unlock_pwd = '979899'

    #港股模拟环境下单及推送
    trade_context = OpenHKTradeContext(host=api_ip, port=api_port)
    trade_context.unlock_trade(unlock_pwd)
    trade_context.set_handler(HKOrderPushHandler())
    trade_context.start()
    trade_context.place_order(price=4.27, qty=1000, strcode='HK.03883', orderside=0, ordertype=0, envtype=1,
                              orderpush=True)

    '''
    #美股正式环境下单及推送
    trade_context = OpenUSTradeContext(host=api_ip, port=api_port)
    trade_context.unlock_trade("unlock_pwd")
    trade_context.set_handler(USOrderPushHandler())
    trade_context.start()
    trade_context.place_order(price=155.0, qty=1, strcode='US.AAPL', orderside=0, ordertype=2, envtype=0, orderpush=True)
    '''
