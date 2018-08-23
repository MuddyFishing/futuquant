# -* -coding:utf-8 -*-
from futuquant import *
import pandas
import time


def test_subscribe():
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11112)
    ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, [])
    code_list = list(ret_data['code'])
    del code_list[1000:]  # 截取股票
    print(code_list)
    # print(quote_ctx.subscribe(code_list,
    #                           [SubType.TICKER, SubType.QUOTE]))
    #
    print(quote_ctx.query_subscription())


def test_get_market_snapshot():
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, [])
    code_list = list(ret_data['code'])
    del code_list[1:]  # 截取股票
    print(len(code_list))
    start = time.time()
    print(start)
    flag = True
    index = 0
    end = 0
    while flag:
        print(index)
        ret_code, ret_data = quote_ctx.get_market_snapshot(code_list)
        print(ret_data)
        index = index + 1
        end = time.time()
        if end - start >= 30:
            flag = False
    print(end)


# 请求次数测试
def test_request_nums():
    # -------30秒的请求次数测试
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    flag = True
    start = time.time()
    print(start)
    index = 0
    end = 0
    while flag:
        print(index)
        ret_code, ret_data, page_key = quote_ctx.request_history_kline(code='HK.00700', start='2018-08-15',
                                                                       end='2018-08-21', ktype=KLType.K_DAY,
                                                                       max_count=1)
        print(ret_data)
        index = index + 1
        end = time.time()
        if end - start >= 30:
            flag = False
    print(end)


# 请求股票支数测试
def test_request_stock_count():
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11112)
    ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, [])
    code_list = list(ret_data['code'])
    del code_list[200:]  # 截取股票
    print(len(code_list))
    # print(quote_ctx.request_history_kline(code='US.AAPL', start='2018-08-15', end='2018-08-15', ktype=KLType.K_DAY, max_count=1))
    # print(quote_ctx.request_history_kline(code='SZ.000001', start='2018-08-15', end='2018-08-15', ktype=KLType.K_DAY,
    #                                       max_count=1))
    # ------每次请求的股票只数测试
    for i in range(201):
        print(i)
        if i != 0 and i % 10 == 0:
            time.sleep(30)
        ret_code, ret_data, page_key = quote_ctx.request_history_kline(code=code_list[i], start='2018-08-15',
                                                                       end='2018-08-21', ktype=KLType.K_DAY,
                                                                       max_count=1)
        print(ret_data)


if __name__ == '__main__':
    # test_subscribe()
    # test_get_market_snapshot()
    test_request_stock_count()
    # test_request_nums()
