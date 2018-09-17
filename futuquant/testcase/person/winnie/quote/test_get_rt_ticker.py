from futuquant import *
import pandas
import sys


class TickerTest(TickerHandlerBase):
        def on_recv_rsp(self, rsp_str):
                ret_code, data = super(TickerTest, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                        print("TickerTest: error, msg: %s" % data)
                        return RET_ERROR, data
                # output = sys.stdout
                # outputfile = open('get_rt_triker2.txt', 'a')
                # sys.stdout = outputfile
                print(data)  # TickerTest自己的处理逻辑

                return RET_OK, data


class SysNotifyTest(SysNotifyHandlerBase):

    def on_recv_rsp(self, rsp_pb):
        ret_code, content = super(SysNotifyTest, self).on_recv_rsp(rsp_pb)
        notify_type, sub_type, msg = content
        if ret_code != RET_OK:
            logger.debug("SysNotifyTest: error, msg: %s" % msg)
            return RET_ERROR, content
        print(msg)
        return ret_code, content


if __name__ == '__main__':
    # test_get_rt_triker()
    # print输出到指定的get_rt_triker.txt中

    # output = sys.stdout
    # outputfile = open('get_rt_triker1.txt', 'w')
    # sys.stdout = outputfile
    # test_get_rt_triker()
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    quote_ctx.subscribe(['HK.00700'], SubType.TICKER)
    quote_ctx.start()
    handler = TickerTest()
    quote_ctx.set_handler(SysNotifyTest())
    quote_ctx.set_handler(handler)

    # outputfile.close()
    # # print(quote_ctx.unsubscribe(['HK.00700'], SubType.TICKER))
    # time.sleep(61)
    # print(quote_ctx.unsubscribe(['HK.00700'], SubType.TICKER))
    # quote_ctx.close()
