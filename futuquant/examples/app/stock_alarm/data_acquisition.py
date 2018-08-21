# -*- coding: utf-8 -*-
from futuquant import *
import data_strategy


class TickerTest(TickerHandlerBase):
    """ 获取逐笔推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(TickerTest, self).parse_rsp_pb(rsp_pb)
        if ret_code != RET_OK:
            print("* TickerTest: error, msg: %s" % content)
            return RET_ERROR, content
        # print("* TickerTest\n", content)
        data_strategy.detect_and_send(content)
        return RET_OK, content


def quote_test(code_list, host, port):
    quote_ctx = OpenQuoteContext(host, port)
    print("Server lim.app:%s connected..." % port)
    # 设置异步回调接口
    quote_ctx.set_handler(TickerTest())
    quote_ctx.start()

    ret, msg = quote_ctx.subscribe(code_list, SubType.TICKER)
    if ret != RET_OK:
        return ret, msg
    print(quote_ctx.query_subscription())
    return RET_OK, ""


