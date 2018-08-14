# import time
from futuquant import *
import pandas
import sys


class StockQuoteTest(StockQuoteHandlerBase):
    def on_recv_rsp(self, rsp_str):
        ret_code, content = super(StockQuoteTest, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("StockQuoteTest: error, msg: %s" % content)
            return RET_ERROR, content
        # 设置显示
        pandas.set_option('max_columns', 100)
        pandas.set_option('display.width', 1000)
        print("StockQuoteTest \n", content)  # StockQuoteTest自己的处理逻辑

        return RET_OK, content


class TestQuote(object):
    def test1(self):
        quote_ctx = OpenQuoteContext(host='172.18.10.58', port=11111)
        # 启动异步数据
        quote_ctx.start()
        # 设置监听
        # handler = StockQuoteTest()
        # quote_ctx.set_handler(handler)
        # # 订阅
        quote_ctx.subscribe(['HK.01758'], SubType.QUOTE)
        # print('获取实时报价')

        ret_code, ret_data = quote_ctx.get_stock_quote(['HK.01758'])
        # pandas.set_option('max_columns', 100)
        # pandas.set_option('display.width ', 1000)
        print(ret_code)
        print('get:', ret_data)
        # print('获取快照')
        # print(quote_ctx.get_market_snapshot(['HK.01758']))

        # 下单
        # pwd_unlock = '123123'
        # trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
        # print(trd_ctx.unlock_trade(pwd_unlock))
        # print('下单')
        # print(trd_ctx.place_order(price=2.72, qty=2000, code="HK.01758", trd_side=TrdSide.BUY))

        # time.sleep(15)
        # quote_ctx.close()


if __name__ == '__main__':
    tq = TestQuote()
    tq.test1()



