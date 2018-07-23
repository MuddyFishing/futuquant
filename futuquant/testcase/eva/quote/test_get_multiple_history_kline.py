#-*-coding:utf-8-*-

from futuquant import *
import pandas

class GetMulHtryKl(object):

    def test1(self):
        pandas.set_option('display.width',1000)
        pandas.set_option('max_columns',1000)

        quote_ctx = OpenQuoteContext(host='127.0.0.1',port=11111)
        codelist = ['HK.999011']
        start = '2018-06-29'    #'2018-07-01'
        end = '2018-07-13'
        ktype = KLType.K_30M
        autype = AuType.QFQ
        ret_code, ret_data = quote_ctx.get_multiple_history_kline(codelist = codelist,start = start,end = end,ktype = ktype,autype = autype)
        print(ret_code)
        print(ret_data)
        quote_ctx.close()



if __name__ == '__main__':
    GetMulHtryKl().test1()