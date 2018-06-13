# -*- coding: utf-8 -*-
"""
Examples for use the python functions: get push data
"""

from futuquant import *
from time import sleep
from futuquant.common.ft_logger import logger

"""
    简介：
        1.futu api一个牛牛号的默认定阅额度是500, 逐笔的权重是5, 故最多只能定阅100支股票
        2.港股全市场正股约2300支， 需要启动23个进程（建议在centos上运行)
        3.本脚本创建多个对象来定阅ticker, 达到收集尽可能多的股票逐笔数据的目的
        4.仅供参考学习
"""

# 逐笔的权重
TICK_WEIGHT = 5


# 配置信息
sub_config = {
    "sub_max": 4000,                                            # 最多定阅多少支股票(需要依据定阅额度和进程数作一个合理预估）
    "sub_stock_type_list": [SecurityType.STOCK],                # 选择要定阅的股票类型
    "sub_market_list": [Market.US],                             # 要定阅的市场
    "ip": "127.0.0.1",                                          # ip
    "port_begin": 11111,                                        # port FutuOpenD开放的第一个端口号
    "port_count": 40,                                            # 启动了多少个FutuOPenD进程，每个进程的port在port_begin上递增
    "sub_one_size": 100,                                        # 最多向一个FutuOpenD定阅多少支股票
    "is_adjust_sub_one_size": True                             # 依据当前剩余定阅量动态调整一次的定阅量(测试白名单不受定阅额度限制可置Flase)
}


# 全局对象
all_quote_ctx = []              # 记录所有创建的quote_ctx对象
all_sub_codes = []              # 记录所有已经定阅的股票
timestamp_adjust = 0         # 时间与futu server时间校准偏差 : (本地时间 - futu时间) 秒


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
            time_str = item['time']

            dt_tick = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            delay_sec = (dt_cur.minute * 60 + dt_cur.second) - timestamp_adjust - (dt_tick.minute * 60 + dt_tick.second)
            if delay_sec > 10:
                logger.critical("* Ticker cirtical :{}".format(item))
            elif delay_sec > 2:
                logger.error("* Ticker error :{}".format(item))

        return RET_OK, content


def cal_timstamp_adjust(quote_ctx):
    # 计算本地时间与futu 时间的偏差
    ret = RET_ERROR
    while ret != RET_OK:
        ret, data = quote_ctx.get_global_state()
        if ret != RET_OK:
            sleep(0.1)
        return (int(time.time()) - int(data['timestamp']))


def cal_all_codes(quote_ctx, market_list, stock_type_list):
    all_codes = []
    for market in market_list:
        for stock_type in stock_type_list:
            ret = RET_ERROR
            while ret != RET_OK:
                ret, data = quote_ctx.get_stock_basicinfo(market, stock_type)
                if ret != RET_OK:
                    sleep(0.1)
                codes = list(data['code'])
                [all_codes.append(code) for code in codes]
                break
    return all_codes


def loop_subscribe_codes(quote_ctx, codes):
    ret = RET_ERROR
    while ret != RET_OK:
        ret, data = quote_ctx.subscribe(codes, SubType.TICKER)
        if ret == RET_OK:
            break
        else:
            print("loop_subscribe_codes :{}".format(data))
        sleep(1)


def loop_get_subscription(quote_ctx):
    ret = RET_ERROR
    while ret != RET_OK:
        ret, data = quote_ctx.query_subscription(True)
        if ret == RET_OK:
            return data
        sleep(0.1)


def create_new_quote_ctx(host, port):
    obj = OpenQuoteContext(host=host, port=port)
    all_quote_ctx.append(obj)
    obj.set_handler(TickerTest())
    obj.start()
    return obj


def full_subscribe_tick():
    # 读取配置参数
    sub_max = sub_config['sub_max']
    sub_stock_type_list = sub_config['sub_stock_type_list']
    sub_market_list = sub_config['sub_market_list']
    ip = sub_config['ip']
    port_begin = sub_config['port_begin']
    port_count = sub_config['port_count']
    sub_one_size = sub_config['sub_one_size']
    is_adjust_sub_one_size = sub_config['is_adjust_sub_one_size']

    # 创建第一个对象
    quote_ctx = create_new_quote_ctx(ip, port_begin)

    # 收集要定阅的codes
    all_codes = cal_all_codes(quote_ctx, sub_market_list, sub_stock_type_list)
    sub_max = sub_max if sub_max < len(all_codes) else len(all_codes)

    if len(all_codes) != sub_max:
        all_codes = all_codes[0: sub_max]

    # 循环定阅
    port_idx = 0
    while port_idx < port_count:
        cur_sub_one_size = sub_one_size
        data = loop_get_subscription(quote_ctx)

        # 已经定阅过的不占用额度可以直接定阅
        codes = data['sub_list'][SubType.TICKER] if SubType.TICKER in data['sub_list'] else []
        codes_to_sub = []
        for code in codes:
            if code not in all_codes:
                continue
            all_sub_codes.append(code)
            all_codes.remove(code)
            codes_to_sub.append(code)

        if len(codes_to_sub):
            loop_subscribe_codes(quote_ctx, codes_to_sub)
            cur_sub_one_size -= len(codes_to_sub)

        # 依据剩余额度，调整要定阅的数量
        data = loop_get_subscription(quote_ctx)
        if is_adjust_sub_one_size:
            size_remain = int(data['remain'] / TICK_WEIGHT)
            cur_sub_one_size = cur_sub_one_size if cur_sub_one_size < size_remain else size_remain

        # 执行定阅
        cur_sub_one_size = cur_sub_one_size if cur_sub_one_size < len(all_codes) else len(all_codes)
        if cur_sub_one_size > 0:
            codes = all_codes[0: cur_sub_one_size]
            all_codes = all_codes[cur_sub_one_size:]
            loop_subscribe_codes(quote_ctx, codes)

        if len(all_codes) == 0:
            break

        # 创建新对象
        port_idx += 1
        if port_idx < port_count:
            quote_ctx = create_new_quote_ctx(ip, port_begin + port_idx)


def main_thread_do_something(quote_ctx, timeout=None):
    if 0 == len(all_sub_codes):
        return
    code = all_sub_codes[0]
    last_time = time.time()
    begin_time = last_time
    data = None
    vol = 0
    last_seq = 0
    while timeout is None or time.time() - begin_time < timeout:
        if data is None or time.time() - last_time > 10:
            last_time = time.time()
            ret, data = quote_ctx.get_rt_ticker(code)
            if ret != RET_OK:
                data = None
            logger.debug("code:{} total vol:{}".format(code, vol))

        sleep(0.1)
        if data is None:
            continue
        for ix, row in data.iterrows():
            seq = row['sequence']
            if seq > last_seq:
                vol += row['volume']
                last_seq = seq


def close_all():
    for quote_ctx in all_quote_ctx:
        quote_ctx.close()
    all_quote_ctx = []
    all_sub_codes = []
    timestamp_adjust = 0


if __name__ =="__main__":

    # 向多个futuOpenD定阅ticker数据
    full_subscribe_tick()

    # 计算本地时间与futu时间差
    timestamp_adjust = cal_timstamp_adjust(all_quote_ctx[0])

    print("count={}, all_sub_codes:{}".format(len(all_sub_codes), all_sub_codes))

    # 主线程做点计算逻辑，timout到达时， 就结束程序运行
    main_thread_do_something(all_quote_ctx[0], 3600 * 24)

    # 正常关闭对象
    close_all()







