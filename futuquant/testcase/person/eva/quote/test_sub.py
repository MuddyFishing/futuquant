#-*-coding:utf-8-*-
import futuquant
from futuquant.common.constant import *
import time

class Sub(object):

    def test1(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1', port=11111)
        ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.HK,SecurityType.STOCK)
        codes = ret_data['code'].tolist()[:5]
        # codes = ['HK.800000']#['HK.00700','HK.16847','US.AAPL','US..DJI','US.DGP','SZ.000001','SH.000001']
        ktype = SubType.TICKER
        print('subscribe',quote_ctx.subscribe(codes,ktype))
        # for code in codes:
        #     print('subscribe',quote_ctx.subscribe(code,ktype))
        #     print('subscribe',quote_ctx.query_subscription())

        # print(quote_ctx.get_cur_kline(code,1,ktype,AuType.QFQ))
        print(quote_ctx.query_subscription())
        time.sleep(60)
        # for code in codes:
        #     print('unsubscribe',quote_ctx.unsubscribe(code,ktype))
        #     print('unsubscribe',quote_ctx.query_subscription())
        print('unsubscribe',quote_ctx.unsubscribe(codes, ktype))
        print(quote_ctx.query_subscription())

        quote_ctx.close()

    def test2(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1', port=11114)
        code = 'HK.00700'
        ktype = SubType.BROKER
        print(quote_ctx.subscribe(code, ktype))
        # print(quote_ctx.query_subscription())
        # time.sleep(60)
        print(quote_ctx.unsubscribe(code, ktype))
        # print(quote_ctx.query_subscription())
        quote_ctx.close()

    def test3(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1', port=11111)
        code = 'HK.00700'
        ktype = SubType.BROKER
        print(quote_ctx.subscribe(code, ktype))

    def test4(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1', port=11113)
        print(quote_ctx.query_subscription())
        ret_code, ret_data = quote_ctx.get_stock_basicinfo(market=Market.HK, stock_type=SecurityType.STOCK,code_list=None)
        codes = ret_data['code'].tolist()
        print(quote_ctx.subscribe(code_list = codes[:1001], subtype_list=SubType.QUOTE))
        print(quote_ctx.query_subscription())
        quote_ctx.close()

    def test5(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1', port=11114)
        # ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK,code_list=[])
        # codes = ret_data['code'].tolist()
        # subTypes = [SubType.QUOTE, SubType.ORDER_BOOK,SubType.BROKER, SubType.TICKER, SubType.RT_DATA]
        # subTypes_KL = [SubType.K_1M,SubType.K_5M,SubType.K_15M, SubType.K_30M, SubType.K_60M,SubType.K_DAY, SubType.K_WEEK, SubType.K_MON]
        # print(quote_ctx.subscribe(code_list = codes[:10], subtype_list=subTypes_KL))    #使用8*n个订阅位
        # print(quote_ctx.query_subscription())
        # print(quote_ctx.subscribe(code_list=codes[:12], subtype_list=subTypes))    #使用5*n个订阅位
        print(quote_ctx.query_subscription())

if __name__ == '__main__':
    sub = Sub()
    sub.test5()