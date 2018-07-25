#-*-coding:utf-8-*-

from futuquant import *

class GetTradingDays(object):

    def test1(self):
        quote_ctx = OpenQuoteContext(host='127.0.0.1',port=11111)
        # quote_ctx.start()   #开启异步数据接收
        market = Market.US
        start_date = '2017-1-1'
        end_date = '2017-12-31'
        ret_code,ret_data = quote_ctx.get_trading_days(market, start_date, end_date)

        print('ret_code = %d'%ret_code)
        print(ret_data)
        print(len(ret_data))

        quote_ctx.close()


if __name__ == '__main__':
    gtd = GetTradingDays()
    gtd.test1()