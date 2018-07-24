#-*-coding:utf-8-*-

import futuquant

class GetMarketSnapshot(object):
    # 获取市场快照 get_market_snapshot

    def test1(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1',port=11111)

        ret_code, ret_data = quote_ctx.get_stock_basicinfo(market='HK', stock_type='STOCK')
        # code_list = ret_data['code'].tolist()[0:20]
        code_list = ['HK.24505','HK.00700']
        ret_code, ret_data = quote_ctx.get_market_snapshot('HK.00700')
        quote_ctx.close()
        print(ret_code)
        print(ret_data)
        # for data in ret_data.iterrows():
        #     print(data)

if __name__ == '__main__':
    gms = GetMarketSnapshot()
    gms.test1()