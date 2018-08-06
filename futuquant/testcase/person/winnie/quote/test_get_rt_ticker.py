from futuquant import *
import pandas
import sys


class TickerTest(TickerHandlerBase):
        def on_recv_rsp(self, rsp_str):
                ret_code, data = super(TickerTest, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                        print("CurKlineTest: error, msg: %s" % data)
                        return RET_ERROR, data
                # print('hello')
                print("TickerTest ", data)  # TickerTest自己的处理逻辑

                return RET_OK, data


def test_get_rt_triker():
    # print输出到指定的get_rt_triker.txt中
    output = sys.stdout
    outputfile = open('get_rt_triker.txt', 'w')
    sys.stdout = outputfile

    quote_ctx = OpenQuoteContext(host='172.18.10.58', port=11111)
    # 订阅
    quote_ctx.subscribe(['HK.00700'], [SubType.TICKER])
    # 设置显示
    # pandas.set_option('max_columns', 100)
    # pandas.set_option('display.width ', 1000)
    print(quote_ctx.get_rt_ticker('HK.00700', 1000))
    quote_ctx.close()
    outputfile.close()


if __name__ == '__main__':
    # test_get_rt_triker()
    # print输出到指定的get_rt_triker.txt中

    # output = sys.stdout
    # outputfile = open('get_rt_triker.txt', 'w')
    # sys.stdout = outputfile

    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    quote_ctx.start()
    handler = TickerTest()
    quote_ctx.set_handler(handler)

    print(quote_ctx.subscribe(['HK.00700'], SubType.TICKER))
    # print(quote_ctx.unsubscribe(['HK.00700'], SubType.TICKER))
    time.sleep(61)
    print(quote_ctx.unsubscribe(['HK.00700'], SubType.TICKER))
    quote_ctx.close()
