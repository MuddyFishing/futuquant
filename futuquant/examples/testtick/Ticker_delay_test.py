# -*- coding: utf-8 -*-
"""
Examples for use the python functions: get push data
"""

from futuquant import *
from time  import sleep
import math
from futuquant.common.ft_logger import logger


class TickerTest(TickerHandlerBase):
    """ 获取逐笔推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(TickerTest, self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("* TickerTest: error, msg: %s" % content)
            return RET_ERROR, content

        dt_cur = datetime.now()
        t_cur=time.time()
        #dt_cur.time()

        for ix, item in content.iterrows():
            timeStr = item['time']
            recvTime = item['recv_timestamp']
            ticktimestamp = time.mktime(time.strptime(timeStr, "%Y-%m-%d %H:%M:%S"))
            #print("====================================")
            s1=timeStr.split(" ")[1]
            #Tick
            #print(s1)

            #print(ticktimestamp)
            #print(recvTime)
            loc_time=time.localtime(math.trunc(recvTime))
            ss =time.strftime("%H:%M:%S",loc_time)
            s2=ss+"."+str(recvTime).split(".")[1][0:3]
            #openD
            #print(s2)

            #print(t_cur)
            curTimeStr=dt_cur.strftime("%H:%M:%S %f")
            s3=curTimeStr.split(" ")[0]+"."+curTimeStr.split(" ")[1][0:3]
            #Me
            #print(s3)

            openDdelay=math.trunc((recvTime-ticktimestamp)*1000)/1000
            s4=str(openDdelay)+"s"
            #D-T
            #print(s4)

            medelay=math.trunc((t_cur-ticktimestamp)*1000)/1000
            s5=str(medelay)+"s"
            #M-T
            #print(s5)

            s6=str(round((medelay-openDdelay)*1000))+ "ms"
            #M-D
            #print(s6)

            #数据最终到达用户延迟大于几秒输出
            if medelay>1:
                print(s1+"  "+s2+"  "+s3+"  "+s4+"  "+s5+"  "+s6)

        return RET_OK, content




def quote_test_tick():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

    # 设置异步回调接口
    quote_ctx.set_handler(TickerTest())

    quote_ctx.start()

    #windows 北京时区 utc +8:00
    #code_list = ['HK.00700','HK_FUTURE.999010']

    #北京时间 美国时间 不能同时测

    #windows 美国 时区utc -5:00  自动夏令
    code_list = ["HK.00700"]


    print(quote_ctx.subscribe(code_list, SubType.TICKER))


    #quote_ctx.close()



if __name__ == '__main__':
    quote_test_tick()




