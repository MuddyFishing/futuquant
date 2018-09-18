# -*- coding: utf-8 -*-
"""
Examples for use the python functions: get push data
"""

from futuquant import *
from time import sleep
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
        for ix, item in content.iterrows():
            time = item['time']

            dt_tick = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            delay_sec = (dt_cur.minute * 60 + dt_cur.second) - (dt_tick.minute * 60 + dt_tick.second)
            if delay_sec > 15:
                logger.critical("* Ticker cirtical :{}".format(item))
            elif delay_sec > 5:
                logger.error("* Ticker error :{}".format(item))

        return RET_OK, content



def main_thread_do_something(quote_ctx):
    code = 'HK.00700'
    last_time = time.time()
    data = None
    vol = 0
    last_seq = 0
    while True:
        if data is None or time.time() - last_time > 10:
            last_time = time.time()
            ret, data = quote_ctx.get_rt_ticker(code)
            if ret != RET_OK:
                data = None
            logger.debug("total vol:{}".format(vol))

        sleep(0.1)
        if data is None:
            continue
        for ix, row in data.iterrows():
            seq = row['sequence']
            if seq > last_seq:
                vol += row['volume']
                last_seq = seq

def quote_test_tick():
    quote_ctx = OpenQuoteContext(host='193.112.189.131', port=12111)

    # 设置异步回调接口
    quote_ctx.set_handler(TickerTest())
    quote_ctx.start()

    code_list = ['HK.00700']
    ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK)
    if ret != RET_OK:
        exit(0)
    codes = list(data['code'])
    max_len = len(data)

    # 定阅的最大数量
    sub_len = 2000
    if sub_len > max_len:
        sub_len = max_len
    import random
    random.seed(time.time())
    while True:
        if len(code_list) >= sub_len:
            break
        rnd_idx = random.randint(0, len(codes) - 1)
        code_tmp = codes[rnd_idx]
        if code_tmp not in code_list:
            code_list.append(code_tmp)

    print(quote_ctx.subscribe(code_list, SubType.TICKER))

    main_thread_do_something(quote_ctx)

    quote_ctx.close()



from multiprocessing import Process, Queue, Manager

def f(val, q, ns, share_list):
    q.put([42, None, 'hello'])
    q.put({'code': '123',
           'vol': 1,
           'price': 3.2,
           })
    ns.xx = 200
    ns.yy = '3f'
    val = 1000

    share_list.append(200)

if __name__ == '__main__':
    q = Queue()
    mg = Manager()
    ns = mg.Namespace()

    share_list = mg.list()
    share_list.append(100)
    ns.xx = 100
    ns.yy = 'abc'
    val = 100
    p = Process(target=f, args=(val, q, ns, share_list))
    p.start()
    sleep(3)

    while not q.empty():
        print(q.get())    # prints "[42, None, 'hello']"

    print(ns)
    print(share_list)

    share_list.remove(100)
    print(share_list)
    print(val)

    p.join()

    # quote_test_tick()




