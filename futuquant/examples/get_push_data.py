# -*- coding: utf-8 -*-
"""
Examples for use the python functions: get push data
"""

from futuquant import *
from time import sleep

#设置dataframe结构的显示------pandas display设置
pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', None) # pandas.set_option() 可以设置pandas相关的参数，从而改变默认参数。 打印pandas数据事，默认是输出100行，多的话会输出....省略号。
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('colheader_justify', 'right') #value显示居右

class StockQuoteTest(StockQuoteHandlerBase):
    """
    获得报价推送数据
    """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(StockQuoteTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            logger.debug("StockQuoteTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("StockQuoteTest : %s" % content)
        return RET_OK, content


class CurKlineTest(CurKlineHandlerBase):
    """ kline push"""
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(CurKlineTest, self).on_recv_rsp(rsp_pb)
        if ret_code == RET_OK:
            print("CurKlineTest : %s\n" % content)
        return RET_OK, content


class RTDataTest(RTDataHandlerBase):
    """ 获取分时推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(RTDataTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("RTDataTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("RTDataTest :%s \n" % content)
        return RET_OK, content


class TickerTest(TickerHandlerBase):
    """ 获取逐笔推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(TickerTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("TickerTest\n", content)
        return RET_OK, content


class OrderBookTest(OrderBookHandlerBase):
    """ 获得摆盘推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(OrderBookTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % content)
            return RET_ERROR, content
        print("OrderBookTest\n", content)
        return RET_OK, content


class BrokerTest(BrokerHandlerBase):
    """ 获取经纪队列推送数据 """
    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, content = super(BrokerTest, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("BrokerTest: error, msg: %s " % content)
            return RET_ERROR, content
        print("BrokerTest bid \n", content[0])
        print("BrokerTest ask \n", content[1])
        return RET_OK, content


class HeartBeatTest(HeartBeatHandlerBase):
    """ 心跳的推送 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, time = super(HeartBeatTest, self).on_recv_rsp(rsp_pb)
        if ret_code == RET_OK:
            print("heart beat server time = ", time)
        return ret_code, time


class SysNotifyTest(SysNotifyHandlerBase):
    """sys notify"""
    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        ret_code, content = super(SysNotifyTest, self).on_recv_rsp(rsp_pb)

        if ret_code == RET_OK:
            main_type, sub_type, msg = content
            print("SysNotify main_type='{}' sub_type='{}' msg='{}'".format(main_type, sub_type, msg))
        else:
            print("SysNotify error:{}".format(content))
        return ret_code, content


class TradeOrderTest(TradeOrderHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeOrderTest, self).on_recv_rsp(rsp_pb)

        if ret == RET_OK:
            trd_env, trd_mkt, order_dict = content
            print("TradeOrderTest trd_env={}, trd_mt={}, order={}".format(trd_env, trd_mkt, order_dict))

        return ret, content


class TradeDealTest(TradeDealHandlerBase):
    """ order update push"""
    def on_recv_rsp(self, rsp_pb):
        ret, content = super(TradeDealTest, self).on_recv_rsp(rsp_pb)

        if ret == RET_OK:
            trd_env, trd_mkt, deal_dict = content
            print("TradeDealTest trd_env={}, trd_mt={}, deal={}".format(trd_env, trd_mkt, deal_dict))

        return ret, content


def quote_test():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    quote_ctx.set_handler(StockQuoteTest())
    quote_ctx.set_handler(CurKlineTest())
    quote_ctx.set_handler(RTDataTest())
    quote_ctx.set_handler(TickerTest())
    quote_ctx.set_handler(OrderBookTest())
    quote_ctx.set_handler(BrokerTest())
    quote_ctx.set_handler(HeartBeatTest())
    quote_ctx.set_handler(SysNotifyTest())
    quote_ctx.start()

    # 获取推送数据
    code_list = ['HK.00700', 'HK.02318']
    sub_type_list = [SubType.RT_DATA, SubType.BROKER]

    # """
    print(quote_ctx.get_global_state())
    print(quote_ctx.subscribe(code_list, sub_type_list, push=True))
    print(quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.ETF))
    print(quote_ctx.get_cur_kline(code_list[0], 10, SubType.K_DAY, AuType.QFQ))

    print(quote_ctx.get_rt_data(code_list[0]))
    print(quote_ctx.get_rt_ticker(code_list[0], 10))

    print(quote_ctx.get_broker_queue(code_list[0]))
    print(quote_ctx.get_order_book(code_list[0]))
    print(quote_ctx.get_history_kline('HK.00700', start='2017-06-20', end='2017-06-22'))
    # """
    print(quote_ctx.get_multi_points_history_kline(code_list, ['2017-06-20', '2017-06-22', '2017-06-23'], KL_FIELD.ALL,
                                                   KLType.K_DAY, AuType.QFQ))
    print(quote_ctx.get_autype_list("HK.00700"))

    print(quote_ctx.get_trading_days(Market.HK, '2018-11-01', '2018-11-20'))
    print(quote_ctx.get_suspension_info('SZ.300104', '2010-02-01', '2018-11-20'))

    print(quote_ctx.get_market_snapshot('HK.21901'))
    print(quote_ctx.get_market_snapshot(code_list))

    print(quote_ctx.get_plate_list(Market.HK, Plate.ALL))
    print(quote_ctx.get_plate_stock('HK.BK1001'))

    sleep(10)
    quote_ctx.close()


def trade_hk_test():
    trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
    trd_ctx.set_handler(TradeOrderTest())
    trd_ctx.set_handler(TradeDealTest())
    trd_ctx.start()
    # 交易请求必须先解锁 !!!
    pwd_unlock = '979899'
    print(trd_ctx.unlock_trade(pwd_unlock))

    # print(trd_ctx.accinfo_query())
    # print(trd_ctx.position_list_query(pl_ratio_min=-50, pl_ratio_max=50))
    # print(trd_ctx.order_list_query(status_filter_list=[OrderStatus.DISABLED]))
    print(trd_ctx.get_acc_list())
    # print(trd_ctx.order_list_query(status_filter_list=[OrderStatus.SUBMITTED]))

    order_id = 8366620264715058660
    # print(trd_ctx.place_order(381.0, 100, "HK.00700", TrdSide.SELL))
    # print(trd_ctx.modify_order(ModifyOrderOp.NORMAL, order_id, 380.0, 200))

    # print(trd_ctx.deal_list_query(strcode="00700"))
    # print(trd_ctx.history_order_list_query(status_filter_list=[OrderStatus.FILLED_ALL, OrderStatus.FILLED_PART],
    #                                      strcode="00700", start="", end="2018-2-1"))

    # print(trd_ctx.history_deal_list_query(strcode="", start="", end="2018-6-1"))

    sleep(15)
    trd_ctx.close()


if __name__ =="__main__":
    quote_test()
    # trade_hk_test()



