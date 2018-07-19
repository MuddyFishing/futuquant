#-*-coding:utf-8-*-

import futuquant
from futuquant.quote.quote_response_handler import TickerHandlerBase
from futuquant.common.constant import *
from evatest.utils.logUtil import Logs

class GetRtTicker(object):
    #获取逐笔 get_rt_ticker 和 TickerHandlerBase

    def test1(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1',port=11111)
        quote_ctx.start()
        # 设置异步数据监听
        handler = TickerTest()
        quote_ctx.set_handler(handler)
        codes = ['HK.00700']
        for code in codes:
            #订阅股票
            quote_ctx.subscribe(code,SubType.TICKER)
            # 调用待测接口
            ret_code,ret_data = quote_ctx.get_rt_ticker(code,1000)
            print(ret_code)
            print(ret_data)


class TickerTest(TickerHandlerBase):
    '''获取逐笔 get_rt_ticker 和 TickerHandlerBase'''
    logger = Logs().getNewLogger(name='TickerTest_00700')
    def on_recv_rsp(self, rsp_pb):
        ret_code, ret_data = super(TickerTest, self).on_recv_rsp(rsp_pb)
        # 打印,记录日志
        TickerTest.logger.info('TickerTest')
        TickerTest.logger.info(ret_code)
        TickerTest.logger.info(ret_data)
        return RET_OK, ret_data

if __name__ =='__main__':
    grt = GetRtTicker()
    grt.test1()