#-*-coding:utf-8-*-

import futuquant
from futuquant.common.constant import *

class GetHistoryKline(object):

    def test1(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1',port=11111)
        code = 'HK.00700'
        start = '2018-07-01'
        end = '2018-05-17'
        ktype = KLType.K_WEEK
        autype = AuType.QFQ
        fields = KL_FIELD.ALL_REAL

        ret_code , ret_data = quote_ctx.get_history_kline(code, start, end, ktype, autype, fields)

        print(ret_code)
        print(ret_data)
        quote_ctx.close()

if __name__ == '__main__':
    ghk = GetHistoryKline()
    ghk.test1()