#-*-coding:utf-8-*-

from futuquant import *
import pandas

class GetAutypeList():
    # 获取复权因子get_autype_list
    def __init__(self):
        pandas.set_option('display.width', 1000)
        pandas.set_option('max_columns', 1000)


    def test1(self):
        quote_ctx = OpenQuoteContext(host='127.0.0.1',port=11111)
        code_list =  ['HK.00700']
        ret_code, ret_data = quote_ctx.get_autype_list(code_list)
        quote_ctx.close()

        print(ret_code)
        print(ret_data)
        # for data in ret_data.iterrows():
        #     print(data)

    def test2(self):
        quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
        ret_code, ret_data = quote_ctx.get_stock_basicinfo(Market.US, SecurityType.STOCK)
        code_list = []
        if ret_code == RET_OK:
            code_list = ret_data['code'].tolist()
        for i in range(10):
            print(quote_ctx.get_autype_list(code_list))
            print(i+1)
        quote_ctx.close()

if __name__ == '__main__':
    gal = GetAutypeList()
    gal.test2()
