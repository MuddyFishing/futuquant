# -* -coding:utf-8 -*-
from futuquant import *
import pandas
import time


def test_subscribe():
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, [])
    code_list = list(ret_data['code'])
    del code_list[501:]  # 截取股票
    print(len(code_list))
    print(quote_ctx.subscribe(code_list,
                              [SubType.TICKER, SubType.QUOTE]))
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


def test_request_history_kline():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_code, ret_data, page_key = quote_ctx.request_history_kline(code='HK.00700', start='2017-12-20',
                                                                   end='2018-01-07', ktype=KLType.K_DAY)
    print(ret_data)


if __name__ == '__main__':
    # test_subscribe()
    test_get_market_snapshot()
    # test_request_history_kline()
