#-*-coding=utf-8-*-

import pandas
from futuquant import *

class GetHoldChange(object):
    #获取高管持仓列表

    def __init__(self):
        pandas.set_option('display.width', 1000)
        pandas.set_option('max_columns', 1000)

    def test1(self):
        host = '127.0.0.1'
        port=11111
        quote_ctx = OpenQuoteContext(host,port)
        print(quote_ctx.get_holding_change_list(code='US.DIS', holder_type=StockHolder.EXECUTIVE, start_date='2018-08-05 20:00:01', end_date=None))


if __name__ == '__main__':

    ghc = GetHoldChange()
    ghc.test1()