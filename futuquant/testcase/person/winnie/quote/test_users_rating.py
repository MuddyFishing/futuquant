# -* -coding:utf-8 -*-
from futuquant import *
import pandas
import datetime


def test_subscribe():
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    # print(quote_ctx.subscribe(['HK.00700', 'US.AAPL', 'SH.000001'], SubType.TICKER))
    # ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, [])
    # code_list = list(ret_data['code'])
    # del code_list[200:]  # 200只期权
    # print(code_list)
    # i = datetime.datetime.now()
    # print(i)
    # for j in range(20):
    #     print(j)
    #     print(quote_ctx.get_market_snapshot(code_list))
    # i = datetime.datetime.now()
    # print(i)
    print(quote_ctx.request_history_kline(code='HK.00700', start='2017-12-20', end='2018-01-07', ktype=KLType.K_DAY))
    # print(quote_ctx.query_subscription())


if __name__ == '__main__':
    test_subscribe()
