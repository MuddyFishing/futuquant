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


class USDealPushHandler(USTradeDealHandlerBase):
    """
    美股成交推送
    """
    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, content = super(USDealPushHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("USDealPushHandler: error, msg: %s " % content)
            return RET_ERROR, content
        print("USDealPushHandler\n", content)
        return RET_OK, content


class HKOrderPushHandler(HKTradeOrderHandlerBase):
    """
    港股定单状态推送
    """
    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, content = super(HKOrderPushHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("HKOrderPushHandler: error, msg: %s " % content)
            return RET_ERROR, content
        print("HKOrderPushHandler\n", content)
        return RET_OK, content


class HKDealPushHandler(HKTradeDealHandlerBase):
    """
    港股成交推送
    """
    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, content = super(HKDealPushHandler, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("HKDealPushHandler: error, msg: %s " % content)
            return RET_ERROR, content
        print("HKDealPushHandler\n", content)
        return RET_OK, content

if __name__ == "__main__":
    api_ip = '127.0.0.1'  # ''119.29.141.202'
    api_port = 11111
    unlock_pwd = '979899'

    '''
    # 港股模拟环境下单及推送
    trade_context = OpenHKTradeContext(host=api_ip, port=api_port)
    trade_context.unlock_trade(unlock_pwd)
    trade_context.set_handler(HKOrderPushHandler())
    trade_context.set_handler(HKDealPushHandler())
    trade_context.start()

    # print('\nHK position_list_query:\n')
    # print(trade_context.position_list_query(strcode='', stocktype='',
    #                                     pl_ratio_min='', pl_ratio_max='', envtype=1))

    # print(trade_context.position_list_query(strcode='', stocktype='',
    #                                     pl_ratio_min='', pl_ratio_max='', envtype=1))

    # print('\nHK history_order_list_query:\n')
    # print(trade_context.history_order_list_query(statusfilter='2,3', strcode='',
    #                                             start='2017-10-01', end='2017-11-31', envtype=1))

    # print('\nHK order_list_query:\n')
    # print(trade_context.order_list_query(orderid='', statusfilter='', strcode='',
    #                                     start='09:30:00', end='24:00:00', envtype=1))

    # print('\nHK history_deal_list_query:\n')
    # print(trade_context.history_deal_list_query(strcode='', start='2017-10-01', end='2017-11-31', envtype=1))

    # print('\nHK deal_list_query:\n')
    # print(trade_context.deal_list_query(envtype=1))

    print('\nHK place_order:')
    orderid_list = [] # ['836204', '836195'] # 传空表示定阅全部订单
    trade_context.subscribe_order_deal_push(orderid_list, True, envtype=1)
    # print(trade_context.place_order(price=4.50, qty=1000, strcode='HK.03883', orderside=0, ordertype=0, envtype=1,
    #                              order_deal_push=False))
    print(trade_context.place_order(price=11.31, qty=1000, strcode='HK.01357', orderside=0, ordertype=0, envtype=1,
                                   order_deal_push=True, price_mode=PriceRegularMode.UPPER))
    '''

    #'''
    #美股正式环境下单及推送
    trade_context = OpenUSTradeContext(host=api_ip, port=api_port)
    print(trade_context.unlock_trade(unlock_pwd))
    trade_context.set_handler(USOrderPushHandler())
    trade_context.set_handler(USDealPushHandler())
    trade_context.start()

    # print('\nUS position_list_query:\n')
    # print(trade_context.position_list_query(strcode='', stocktype='STOCK',
    #                                     pl_ratio_min='-20.5', pl_ratio_max='0', envtype=0))

    # print('\nUS. history_order_list_query:\n')
    # print(trade_context.history_order_list_query(statusfilter='', strcode='', start='2017-10-01', end='2017-11-31', envtype=0))

    # print('\nUS. order_list_query:\n')
    # print(trade_context.order_list_query(statusfilter='', strcode='US.MIN', start='', end='', envtype=0))

    # print('\nUS. history_deal_list_query:\n')
    # print(trade_context.history_deal_list_query(strcode='', start='2017-10-01', end='2017-11-31', envtype=0))
    # print('\nUS. deal_list_query:\n')
    # print(trade_context.deal_list_query(envtype=0))

    # trade_context.subscribe_order_deal_push('', True, 0)
    # print('\nUS place_order:')
    print(trade_context.place_order(price="3.55", qty=1, strcode='US.MIN', orderside=0, ordertype=2, envtype=0, order_deal_push=True, price_mode=PriceRegularMode.LOWER))
    # '''
