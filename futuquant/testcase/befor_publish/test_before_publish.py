#-*-coding:utf-8-*-

from futuquant import *
import pandas

class ALLApi(object):
    #上线前测试用例，遍历所有接口保证可执行

    def __init__(self):
        pandas.set_option('max_columns',100)
        pandas.set_option('display.width',1000)
        self.host = '127.0.0.1'
        self.port = 11111
        self.subTypes = [SubType.QUOTE, SubType.ORDER_BOOK, SubType.BROKER, SubType.TICKER, SubType.RT_DATA, SubType.K_1M,
                    SubType.K_5M, SubType.K_15M, SubType.K_30M, SubType.K_60M, SubType.K_DAY, SubType.K_WEEK,
                    SubType.K_MON]

    def test_quotation(self):
        #所有行情的同步接口
        quote_ctx = OpenQuoteContext(self.host, self.port)
        print('获取报价 get_stock_quote')
        print(quote_ctx.get_stock_quote(code_list = ['HK.00700','HK.62423','HK.800000','US.AAPL','SH.601318','SH.000001','SZ.000001']))
        print('获取逐笔 get_rt_ticker')
        print(quote_ctx.get_rt_ticker(code= 'HK.00388',num=1000))
        print(quote_ctx.get_rt_ticker(code='US.MSFT', num=1000))
        print(quote_ctx.get_rt_ticker(code='SH.601998', num=1000))
        print('获取实时K线 get_cur_kline')
        print(quote_ctx.get_cur_kline(code = 'HK.00772', num=1000, ktype=SubType.K_5M, autype=AuType.QFQ))
        print(quote_ctx.get_cur_kline(code='US.FB', num=500, ktype=SubType.K_DAY, autype=AuType.HFQ))
        print(quote_ctx.get_cur_kline(code='SZ.000885', num=750, ktype=SubType.K_WEEK, autype=AuType.NONE))
        print('获取摆盘 get_order_book')
        print(quote_ctx.get_order_book(code = 'HK.01810'))
        print(quote_ctx.get_order_book(code='US.AMZN'))
        print('获取分时数据 get_rt_data')
        print(quote_ctx.get_rt_data(code = 'HK.01357'))
        print(quote_ctx.get_rt_data(code='US.MDR'))
        print(quote_ctx.get_rt_data(code='SZ.000565'))
        print('获取经纪队列 get_broker_queue')
        print(quote_ctx.get_broker_queue(code = 'HK.01478'))
        print('订阅 subscribe')
        print(quote_ctx.subscribe(code_list = ['HK.00700','US.AAPL'], subtype_list =self.subTypes))
        print('查询订阅 query_subscription')
        print(quote_ctx.query_subscription(is_all_conn=True))
        print('获取交易日 get_trading_days')
        print(quote_ctx.get_trading_days(market = Market.HK, start_date=None, end_date=None))
        print('获取股票信息 get_stock_basicinfo')
        print(quote_ctx.get_stock_basicinfo(market = Market.HK, stock_type=SecurityType.STOCK, code_list=None))
        print(quote_ctx.get_stock_basicinfo(market=Market.HK, stock_type=SecurityType.WARRANT, code_list=None))
        print(quote_ctx.get_stock_basicinfo(market=Market.US, stock_type=SecurityType.STOCK, code_list=None))
        print('获取复权因子 get_autype_list')
        print(quote_ctx.get_autype_list(code_list = ['HK.00700','US.AAPL','SZ.300104']))
        print('获取市场快照 get_market_snapshot')
        print(quote_ctx.get_market_snapshot(code_list = ['HK.00700','US.AAPL','SZ.300104']))
        print('获取板块集合下的子板块列表 get_plate_list')
        print(quote_ctx.get_plate_list( market = Market.HK, plate_class = Plate.ALL))
        print(quote_ctx.get_plate_list(market=Market.US, plate_class=Plate.ALL))
        print(quote_ctx.get_plate_list(market=Market.SH, plate_class=Plate.ALL))
        print('获取板块下的股票列表 get_plate_stock')
        print(quote_ctx.get_plate_stock(plate_code = 'HK.BK1160'))
        print(quote_ctx.get_plate_stock(plate_code='SH.BK0045'))
        print('获取牛牛程序全局状态 get_global_state')
        print(quote_ctx.get_global_state())
        print('获取历史K线 get_history_kline')
        print(quote_ctx.get_history_kline(code='HK.02689',start=None,end=None,ktype=KLType.K_DAY,autype=AuType.QFQ,fields=[KL_FIELD.ALL]))
        print(quote_ctx.get_history_kline(code='US.NSP', start=None, end=None, ktype=KLType.K_MON, autype=AuType.HFQ,fields=[KL_FIELD.ALL]))
        print(quote_ctx.get_history_kline(code='SZ.300601', start=None, end=None, ktype=KLType.K_WEEK, autype=AuType.NONE,fields=[KL_FIELD.ALL]))
        print('获取多支股票多个单点历史K线 get_multi_points_history_kline')
        print(quote_ctx.get_multi_points_history_kline(code_list = ['HK.00700','US.JD','SH.000001'],dates=['2018-01-01', '2018-08-02'],fields=KL_FIELD.ALL,ktype=KLType.K_15M,autype=AuType.HFQ,no_data_mode=KLNoDataMode.BACKWARD))
        quote_ctx.close()

    def test_quotation_async(self):
        #所有行情的异步接口
        quote_ctx = OpenQuoteContext(self.host, self.port)
        quote_ctx.start()
        # 设置监听
        handlers = [CurKlineTest(),OrderBookTest(),RTDataTest(),TickerTest(),StockQuoteTest(),BrokerTest()]
        for handler in handlers:
            quote_ctx.set_handler(handler)
        # 订阅
        codes = ['HK.00700','HK.62423','HK.800000','US.AAPL','SH.601318','SH.000001','SZ.000001']
        quote_ctx.subscribe(code_list = codes, subtype_list = self.subTypes)
        time.sleep(5*60)   #订阅5分钟
        quote_ctx.stop()
        quote_ctx.close()

    def test_trade(self,tradeEnv = TrdEnv.REAL):
        #交易
        trade_hk = OpenHKTradeContext(self.host, self.port)
        trade_us = OpenUSTradeContext(self.host, self.port)
        if tradeEnv == TrdEnv.REAL:
            trade_cn = OpenHKCCTradeContext(self.host, self.port)   #A股通
        else:
            trade_cn = OpenCNTradeContext(self.host, self.port)   #web模拟交易
        print('交易环境：',tradeEnv)
        #解锁交易unlock
        trade_pwd = '123123'
        print('HK解锁交易',trade_hk.unlock_trade(trade_pwd))
        print('US解锁交易', trade_us.unlock_trade(trade_pwd))
        print('CN解锁交易', trade_cn.unlock_trade(trade_pwd))
        # 设置监听
        handler_tradeOrder = TradeOrderTest()
        handler_tradeDealtrade = TradeDealTest()
        trade_hk.set_handler(handler_tradeOrder)
        trade_hk.set_handler(handler_tradeDealtrade)
        trade_us.set_handler(handler_tradeOrder)
        trade_us.set_handler(handler_tradeDealtrade)
        trade_cn.set_handler(handler_tradeOrder)
        trade_cn.set_handler(handler_tradeDealtrade)
        # 开启异步
        trade_hk.start()
        trade_us.start()
        trade_cn.start()

        # 下单 place_order
        price_hk = 5.96
        qty_hk = 500
        code_hk = 'HK.1357'
        price_us = 36.28
        qty_us = 2
        code_us = 'US.JD'
        price_cn = 8.94
        qty_cn = 100
        code_cn = 'SZ.000001'
        for i in range(3):
            #港股普通订单-买入
            print('港股普通订单-买入')
            print(trade_hk.place_order(price=price_hk - i, qty=qty_hk * i,
                                 code=code_hk,
                                 trd_side=TrdSide.BUY,
                                 order_type=OrderType.NORMAL,
                                 adjust_limit=0, trd_env=tradeEnv,
                                 acc_id=0))

            #港股普通订单-卖出
            print('港股普通订单-卖出')
            print(trade_hk.place_order(price=price_hk - i, qty=qty_hk * i,
                                       code=code_hk,
                                       trd_side=TrdSide.SELL,
                                       order_type=OrderType.NORMAL,
                                       adjust_limit=0, trd_env=tradeEnv,
                                       acc_id=0))
            #美股普通订单-买入
            print('股普通订单-买入')
            print(trade_us.place_order(price=price_us - i, qty=qty_us * i,
                                       code=code_us,
                                       trd_side=TrdSide.BUY,
                                       order_type=OrderType.NORMAL,
                                       adjust_limit=0, trd_env=tradeEnv,
                                       acc_id=0))
            # 美股普通订单-卖出
            print('股普通订单-卖出')
            print(trade_us.place_order(price=price_us + i, qty=qty_us * i,
                                 code=code_us,
                                 trd_side=TrdSide.SELL,
                                 order_type=OrderType.NORMAL,
                                 adjust_limit=0, trd_env=tradeEnv,
                                 acc_id=0))
            #A股普通订单-买入
            print('A股普通订单-买入')
            print(trade_cn.place_order(price=price_cn + i, qty=qty_cn * i,
                                      code=code_cn,
                                      trd_side=TrdSide.SELL,
                                      order_type=OrderType.NORMAL,
                                      adjust_limit=0,
                                      trd_env=tradeEnv, acc_id=0))
            print('A股普通订单-卖出')
            print(trade_cn.place_order(price=price_cn + i, qty=qty_cn * i,
                                            code=code_cn,
                                            trd_side=TrdSide.SELL,
                                            order_type=OrderType.NORMAL,
                                            adjust_limit=0,
                                            trd_env=tradeEnv, acc_id=0))

        #查询今日订单 order_list_query
        ret_code_order_list_query_hk, ret_data_order_list_query_hk = trade_hk.order_list_query(order_id="",
                                                                                               status_filter_list=[],
                                                                                               code='', start='',
                                                                                               end='',
                                                                                               trd_env=tradeEnv,
                                                                                               acc_id=0)
        print('港股今日订单 ',ret_code_order_list_query_hk, ret_data_order_list_query_hk)
        ret_code_order_list_query_us, ret_data_order_list_query_us = trade_us.order_list_query(order_id="",
                                                                                               status_filter_list=[],
                                                                                               code='', start='',
                                                                                               end='',
                                                                                               trd_env=tradeEnv,
                                                                                               acc_id=0)
        print('美股今日订单 ',ret_code_order_list_query_us, ret_data_order_list_query_us)
        ret_code_order_list_query_cn, ret_data_order_list_query_cn = trade_cn.order_list_query(order_id="",
                                                                                                    status_filter_list=[],
                                                                                                    code='', start='',
                                                                                                    end='',
                                                                                                    trd_env=tradeEnv,
                                                                                                    acc_id=0)
        print('A股今日订单 ',ret_code_order_list_query_cn, ret_data_order_list_query_cn)

        # 修改订单modify_order
        order_ids_hk = ret_data_order_list_query_hk.data['order_id'].tolist()
        order_ids_us = ret_data_order_list_query_us.data['order_id'].tolist()
        order_ids_cn = ret_data_order_list_query_cn.data['order_id'].tolist()

        for order_id_hk in order_ids_hk:
            #港股-修改订单数量/价格
            print('港股改单，order_id = ',order_id_hk)
            print(trade_hk.modify_order(modify_order_op=ModifyOrderOp.NORMAL, order_id=order_id_hk , qty=qty_hk*2, price=price_hk-1, adjust_limit=0,
                                    trd_env=tradeEnv, acc_id=0))
            time.sleep(2)
            #撤单
            print('港股撤单，order_id = ', order_id_hk)
            print(trade_hk.modify_order(modify_order_op=ModifyOrderOp.CANCEL, order_id=order_id_hk, qty=0, price=0, adjust_limit=0,
                                      trd_env=tradeEnv, acc_id=0))

        for order_id_us in order_ids_us:
            #美股-修改订单数量/价格
            print('美股改单，order_id = ',order_id_us)
            print(trade_us.modify_order(modify_order_op=ModifyOrderOp.NORMAL, order_id=order_id_us , qty=qty_us*2, price=price_us-1, adjust_limit=0,
                                    trd_env=tradeEnv, acc_id=0))
            time.sleep(2)
            #撤单
            print('美股撤单，order_id = ', order_id_us)
            print(trade_us.modify_order(modify_order_op=ModifyOrderOp.CANCEL, order_id=order_id_us, qty=0, price=0, adjust_limit=0,
                                      trd_env=tradeEnv, acc_id=0))

        for order_id_cn in order_ids_cn:
            #A股-修改订单数量/价格
            print('A股改单，order_id = ',order_id_cn)
            print(trade_cn.modify_order(modify_order_op=ModifyOrderOp.NORMAL, order_id=order_id_cn , qty=qty_cn*2, price=price_cn-1, adjust_limit=0,
                                    trd_env=tradeEnv, acc_id=0))
            time.sleep(2)
            #撤单
            print('A股撤单，order_id = ', order_id_cn)
            print(trade_cn.modify_order(modify_order_op=ModifyOrderOp.CANCEL, order_id=order_id_cn, qty=0, price=0, adjust_limit=0,
                                      trd_env=tradeEnv, acc_id=0))

        #查询账户信息 accinfo_query
        print('HK 账户信息')
        print(trade_hk.accinfo_query(trd_env=tradeEnv, acc_id=0))
        print('US 账户信息')
        print(trade_us.accinfo_query(trd_env=tradeEnv, acc_id=0))
        print('CN 账户信息')
        print(trade_cn.accinfo_query(trd_env=tradeEnv, acc_id=0))

        #查询持仓列表 position_list_query
        print('HK 持仓列表')
        print(trade_hk.position_list_query( code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=tradeEnv, acc_id=0))
        print('US 持仓列表')
        print(trade_us.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=tradeEnv, acc_id=0))
        print('CN 持仓列表')
        print(trade_cn.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=tradeEnv, acc_id=0))

        #查询历史订单列表 history_order_list_query
        print('HK 历史订单列表')
        print(trade_hk.history_order_list_query(status_filter_list=[], code='', start='', end='',
                                 trd_env=tradeEnv, acc_id=0))
        print('US 历史订单列表')
        print(trade_us.history_order_list_query(status_filter_list=[], code='', start='', end='',
                                                trd_env=tradeEnv, acc_id=0))
        print('CN 历史订单列表')
        print(trade_cn.history_order_list_query(status_filter_list=[], code='', start='', end='',
                                                trd_env=tradeEnv, acc_id=0))

        #查询今日成交列表 deal_list_query
        print('HK 今日成交列表')
        print(trade_hk.deal_list_query(code="", trd_env=tradeEnv, acc_id=0))
        print('US 今日成交列表')
        print(trade_us.deal_list_query(code="", trd_env=tradeEnv, acc_id=0))
        print('CN 今日成交列表')
        print(trade_cn.deal_list_query(code="", trd_env=tradeEnv, acc_id=0))

        #查询历史成交列表 history_deal_list_query
        print('HK 历史成交列表')
        print(trade_hk.history_deal_list_query(code = '', start='', end='', trd_env=tradeEnv, acc_id=0))
        print('US 历史成交列表')
        print(trade_us.history_deal_list_query(code='', start='', end='', trd_env=tradeEnv, acc_id=0))
        print('CN 历史成交列表')
        print(trade_cn.history_deal_list_query(code='', start='', end='', trd_env=tradeEnv, acc_id=0))


class CurKlineTest(CurKlineHandlerBase):
    '''获取实时K线 get_cur_kline 和 CurKlineHandlerBase'''

    def on_recv_rsp(self, rsp_pb):
        ret_code, ret_data = super(CurKlineTest, self).on_recv_rsp(rsp_pb)
        # 打印,记录日志
        print('CurKlineHandlerBase ', ret_code)
        print(ret_data)
        return RET_OK, ret_data


class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, ret_data = super(OrderBookTest, self).on_recv_rsp(rsp_pb)
        # 打印
        print('OrderBookHandlerBase ', ret_code)
        print(ret_data)
        return RET_OK, ret_data


class RTDataTest(RTDataHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, ret_data = super(RTDataTest, self).on_recv_rsp(rsp_pb)
        # 打印信息
        print('RTDataHandlerBase ', ret_code)
        print(ret_data)
        return RET_OK, ret_data


class TickerTest(TickerHandlerBase):
    '''获取逐笔 get_rt_ticker 和 TickerHandlerBase'''

    def on_recv_rsp(self, rsp_pb):
        ret_code, ret_data = super(TickerTest, self).on_recv_rsp(rsp_pb)
        # 打印
        print('TickerHandlerBase ', ret_code)
        print(ret_data)
        return RET_OK, ret_data


class StockQuoteTest(StockQuoteHandlerBase):
    # 获取报价get_stock_quote和StockQuoteHandlerBase

    def on_recv_rsp(self, rsp_str):
        ret_code, ret_data = super(StockQuoteTest, self).on_recv_rsp(
            rsp_str)  # 基类的on_recv_rsp方法解包返回了报价信息，格式与get_stock_quote一样
        # 打印
        print('StockQuoteTest ', ret_code)
        print(ret_data)
        return RET_OK, ret_data


class BrokerTest(BrokerHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, stock_code, ret_data = super(BrokerTest, self).on_recv_rsp(rsp_pb)
        # 打印
        print('BrokerHandlerBase ', ret_code)
        print(stock_code)
        print(ret_data)

        return RET_OK, ret_data


class TradeOrderTest(TradeOrderHandlerBase):
    '''订单状态推送'''
    def on_recv_rsp(self, rsp_pb):
        ret_code,ret_data = super(TradeOrderTest, self).on_recv_rsp(rsp_pb)
        print('TradeOrderHandlerBase  ret_code = %d, ret_data = \n%s'%(ret_code,str(ret_data)))

        return RET_OK,ret_data


class TradeDealTest(TradeDealHandlerBase):
    '''订单成交推送 '''
    def on_recv_rsp(self, rsp_pb):
        ret_code,ret_data = super(TradeDealTest, self).on_recv_rsp(rsp_pb)
        print('TradeDealHandlerBase  ret_code = %d, ret_data = \n%s' % (ret_code,str(ret_data)))
        return RET_OK,ret_data


if __name__ == '__main__':
    aa = ALLApi()
    aa.test_quotation()
    aa.test_quotation_async()
    aa.test_trade_real()
    aa.test_trade_simulate()



