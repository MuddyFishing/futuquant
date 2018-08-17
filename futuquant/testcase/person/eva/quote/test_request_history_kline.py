#-*-coding=utf-8-*-

import pandas
from futuquant import *
from futuquant.testcase.person.eva.datas.collect_stock import *

class RequestHstyKl(object):
    #请求历史K线

    def __init__(self):
        pandas.set_option('display.width', 1000)
        pandas.set_option('max_columns', 1000)

    def test1(self):
        host = '127.0.0.1'
        port = 11112
        quote_ctx = OpenQuoteContext('127.0.0.1',11111)
        # s = time.time()
        # print(s)
        req_key = None
        for i in range(900):
            print(i)
            ret_code,ret_data, req_key = quote_ctx.request_history_kline(code='HK.00700',
                                  start='2018-8-1',
                                  end='2018-8-16',
                                  ktype=KLType.K_1M,
                                  autype=AuType.NONE,
                                  fields=KL_FIELD.ALL_REAL,
                                  max_count=331,
                                  page_req_key=req_key )
            print(ret_code,ret_data, req_key)

        # e = time.time()
        # print(s)
        # print('时延（秒）：',e - s)

if __name__ == '__main__':
    rhk = RequestHstyKl()
    rhk.test1()

