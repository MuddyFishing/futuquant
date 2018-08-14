# -*-coding:utf-8-*-

from futuquant import *
from futuquant.common.constant import *
import pandas


def test_cur_kline():
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    quote_ctx.subscribe(['HK.00700'], SubType.K_MON)
    print(quote_ctx.get_cur_kline('HK.00700', 8, SubType.K_MON , AuType.QFQ))
    quote_ctx.close()


if __name__ == '__main__':
    test_cur_kline()
