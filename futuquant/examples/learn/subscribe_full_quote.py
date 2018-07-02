# -*- coding: utf-8 -*-
"""
Examples for use the python functions: get push data
"""

from futuquant import *
from time import sleep
from futuquant.common.ft_logger import logger
import multiprocessing as mp
from threading import Thread, RLock
import pandas as pd


"""
    简介：
        1. futu api一个牛牛号的默认定阅额度是500, 逐笔的权重是5, 故最多只能定阅100支股票的逐笔(ticker)
        2. 港股全市场正股约2300支， 需要启动23个进程才能接收全量ticker（建议在centos上运行)
        3. 本脚本创建多个对象多个进程来定阅行情, 达到收集尽可能多的股票实时数据
        4. 仅供参考学习
    接口说明:
        1. property: timestamp_adjust 得到本地与futu server的时间差（local - futu) 秒
        2. property: codes_pool 指定股票池，如果不指定，将读取config配置从股票列表中顺序取一批数量股票
        3. property: config 配置信息，具体参考 SubscribeFullQuote.DEFAULT_SUB_CONFIG中说明
        4. property: success_sub_codes 成功定阅的股票
        5. start 启动运行，注意正确配置config参数，否则程序将无法正常运行
        6. close 结束运行
        7. set_handler 指定接收回调的实例 ，必须是FullQuoteHandleBase的派生对象
        8.范例参考class下的main
"""


class FullQuoteHandleBase(object):
    def on_recv_rsp(self, data_dict):
        """
        :param data_dict: futu api的各类行情数据dataframe转成的dict对象，具体字段请参考futu api对象
        StockQuoteHandlerBase / OrderBookHandlerBase /  CurKlineHandlerBase /
        TickerHandlerBase / RTDataHandlerBase / BrokerHandlerBase
        :return: None
        """
        print(data_dict)


class SubscribeFullQuote(object):
    # 定阅权重
    DICT_QUOTE_WEIGHT = {
        SubType.TICKER: 5,
        SubType.ORDER_BOOK: 5,
        SubType.BROKER: 5,
        SubType.K_1M: 2,
        SubType.K_5M: 2,
        SubType.K_15M: 2,
        SubType.K_30M: 2,
        SubType.K_60M: 2,
        SubType.K_DAY: 2,
        SubType.K_MON: 2,
        SubType.RT_DATA: 2,
        SubType.QUOTE: 1,
    }
    # 默认配置信息
    DEFAULT_SUB_CONFIG = {
        "ip": "127.0.0.1",                      # FutuOpenD运行IP
        "port_begin": 11111,                    # port FutuOpenD开放的第一个端口号

        "port_count": 1,                       # 启动了多少个FutuOPenD进程，每个进程的port在port_begin上递增
        "sub_one_size": 100,                    # 最多向一个FutuOpenD定阅多少支股票
        "is_adjust_sub_one_size": True,         # 依据当前剩余定阅量动态调整一次的定阅量(测试白名单不受定阅额度限制可置Flase)
        'one_process_ports': 1,                 # 用多进程提高性能，一个进程处理多少个端口

        # 若使用property接口 "codes_pool" 指定了定阅股票， 以下配置无效
        "sub_max": 4000,                                            # 最多定阅多少支股票(需要依据定阅额度和进程数作一个合理预估）
        "sub_stock_type_list": [SecurityType.STOCK],                # 选择要定阅的股票类型
        "sub_market_list": [Market.HK],                             # 要定阅的市场
    }
    def __init__(self, subtype=SubType.TICKER):
        self.__sub_config = copy(self.DEFAULT_SUB_CONFIG)
        self.__subtype = subtype

        if subtype not in self.DICT_QUOTE_WEIGHT.keys():
            raise Exception("invalid subtype!")

        self.__mp_manage = mp.Manager()
        self.__share_sub_codes = self.__mp_manage.list()   # 共享记录进程已经定阅的股票
        self.__share_left_codes = self.__mp_manage.list()  # 共享记录进程剩余要定阅的股票

        self.__ns_share = self.__mp_manage.Namespace()
        self.__ns_share.is_process_ready = False
        self.__ns_share.is_main_exit = False
        self.__share_queue_tick = mp.Queue()

        self.__timestamp_adjust = 0  # 时间与futu server时间校准偏差 : (本地时间 - futu时间) 秒
        self.__codes_pool = []
        self.__process_list = []
        self.__loop_thread = None
        self.__tick_thread = None
        self.__is_start_run = False
        self._tick_handler = FullQuoteHandleBase()
        self.__all_process_ready = False

    @property
    def timestamp_adjust(self):
        return self.__timestamp_adjust

    @property
    def codes_pool(self):
        return self.__codes_pool

    @codes_pool.setter
    def codes_pool(self, codes):
        if type(codes) is not list:
            codes = [codes]
        self.__codes_pool = copy(codes)

    @property
    def success_sub_codes(self):
        return [code for code in self.__share_sub_codes]

    @property
    def config(self):
        return self.__sub_config

    @config.setter
    def config(self, dict_config):
        for keys in dict_config.keys():
            if keys in self.__sub_config:
                self.__sub_config[keys] = dict_config[keys]

    @classmethod
    def cal_timstamp_adjust(cls, quote_ctx):
        # 计算本地时间与futu 时间的偏差, 3次取最小值
        diff_ret = None
        ret = RET_ERROR
        for x in range(3):
            while ret != RET_OK:
                ret, data = quote_ctx.get_global_state()
                if ret != RET_OK:
                    sleep(0.1)
                    continue
                one_diff = time.time() - data['local_timestamp']
            diff_ret = min(diff_ret, one_diff) if diff_ret is not None else one_diff

        return diff_ret

    @classmethod
    def cal_all_codes(cls, quote_ctx, market_list, stock_type_list, max_count):
        all_codes = []
        for market in market_list:
            for stock_type in stock_type_list:
                ret = RET_ERROR
                while ret != RET_OK:
                    ret, data = quote_ctx.get_stock_basicinfo(market, stock_type)
                    if ret != RET_OK:
                        sleep(0.1)
                        continue
                    codes = list(data['code'])
                    [all_codes.append(code) for code in codes]
                    break
                if len(all_codes) >= max_count:
                    all_codes = all_codes[0: max_count]
                    break
        return all_codes

    @classmethod
    def loop_subscribe_codes(cls, quote_ctx, codes, subtype):
        ret = RET_ERROR
        while ret != RET_OK:
            ret, data = quote_ctx.subscribe(codes, subtype)
            if ret == RET_OK:
                break
            else:
                print("loop_subscribe_codes :{}".format(data))
            sleep(1)

    @classmethod
    def loop_get_subscription(cls, quote_ctx):
        ret = RET_ERROR
        while ret != RET_OK:
            ret, data = quote_ctx.query_subscription(True)
            if ret == RET_OK:
                return data
            else:
                print("loop_get_subscription:{}".format(data))
            sleep(0.1)

    def set_handler(self, handler):
        self._tick_handler = handler

    def start(self):

        if self.__is_start_run:
            return
        self.__is_start_run = True

        ip = self.__sub_config['ip']
        port_begin = self.__sub_config['port_begin']
        quote_ctx = OpenQuoteContext(ip, port_begin)

        # 如果外面不指定定阅股票，就从股票列表中取出
        if len(self.__codes_pool) == 0:
            self.__codes_pool = self.cal_all_codes(quote_ctx, self.__sub_config['sub_market_list'],
                                self.__sub_config['sub_stock_type_list'], self.__sub_config['sub_max'])

        if len(self.__codes_pool) == 0:
            raise Exception("codes pool is empty")

        # 共享记录剩余的要定阅的股票
        self.__share_left_codes = self.__mp_manage.list()
        [self.__share_left_codes.append(code) for code in self.__codes_pool]

        self.__timestamp_adjust = self.cal_timstamp_adjust(quote_ctx)
        quote_ctx.close()

        # 创建进程定阅
        port_idx = 0
        sub_one_size = self.__sub_config['sub_one_size']
        is_adjust_sub_one_size = self.__sub_config['is_adjust_sub_one_size']
        all_port_count = self.__sub_config['port_count']
        one_process_ports = self.__sub_config['one_process_ports']
        one_process_ports = min(one_process_ports, all_port_count)

        self.__ns_share.is_main_exit = False
        # 创建多个进程定阅ticker
        while len(self.__share_left_codes) > 0 and port_idx < all_port_count:

            # 备份下遗留定阅股票
            left_codes = []
            [left_codes.append(code) for code in self.__share_left_codes]

            self.__ns_share.is_process_ready = False
            process = mp.Process(target=self.process_fun, args=(self.__subtype, ip, port_begin+port_idx,
                                one_process_ports, sub_one_size, is_adjust_sub_one_size, self.__share_queue_tick,
                                self.__share_sub_codes, self.__share_left_codes, self.__ns_share))
            process.start()
            while process.is_alive() and not self.__ns_share.is_process_ready:
                print("wait process to subscribe ...")
                sleep(1)

            if process.is_alive():
                port_idx += one_process_ports
                self.__process_list.append(process)
            else:
                self.__share_left_codes = self.__mp_manage.list()
                [self.__share_left_codes.append(code) for code in left_codes]

        #log info
        logger.debug("all_sub_code count={} codes={}".format(len(self.__share_sub_codes), self.__share_sub_codes))
        logger.debug("process count={}".format(len(self.__process_list)))

        # 创建tick 处理线程
        self.__tick_thread = Thread(
                target=self._thread_tick_check, args=())
        # self.__tick_thread.setDaemon(True)
        self.__tick_thread.start()

        # 创建loop 线程
        """
        if create_loop_run:
            self.__loop_thread = Thread(
                target=self._thread_loop_hold, args=())
            self.__loop_thread.start()
        """

    def close(self):
        if not self.__is_start_run:
            return
        self.__ns_share.is_main_exit = True

        for proc in self.__process_list:
            proc.join()
        self.__process_list.clear()

        self.__is_start_run = False
        if self.__loop_thread:
            self.__loop_thread.join(timeout=10)
            self.__loop_thread = None

        if self.__tick_thread:
            self.__tick_thread.join(timeout=10)
            self.__tick_thread = None

    def _thread_loop_hold(self):
        while not self.__is_start_run:
            sleep(0.1)

    def _thread_tick_check(self):
        while self.__is_start_run:
            try:
                while self.__share_queue_tick.empty() is False:
                    dict_data = self.__share_queue_tick.get_nowait()
                    if self._tick_handler:
                        self._tick_handler.on_recv_rsp(dict_data)
                sleep(0.01)
            except Exception as e:
                pass

    @classmethod
    def process_fun(cls, subtype, ip, port, port_count, sub_one_size, is_adjust_sub_one_size,
                            share_queue_tick, share_sub_codes, share_left_codes, ns_share):
        """
        :param ip:
        :param port: 超始端口
        :param port_count: 端口个数
        :param sub_one_size: 一个端口定阅的个数
        :param is_adjust_sub_one_size:  依据当前剩余定阅量动态调整一次的定阅量(测试白名单不受定阅额度限制可置Flase)
        :param share_queue_tick:  进程共享 - tick数据队列
        :param share_sub_codes:   进程共享 - 定阅成功的股票
        :param share_left_codes:  进程共享 - 剩余需要定阅的量
        :param ns_share:          进程共享 - 变量 is_process_ready 进程定阅操作完成 , is_main_exit 主进程退出标志
        :return:
        """
        if not port or sub_one_size <= 0:
            return

        def ProcessPushData(ret_code, content):
            if ret_code != RET_OK or content is None:
                return RET_ERROR, content

            if type(content) is pd.DataFrame:
                data_tmp = content.to_dict(orient='index')
                for x in data_tmp.values():
                    if type(x) is dict:
                        x['process_timestamp'] = time.time()
                    share_queue_tick.put(x)
            elif type(content) is list:
                for x in content:
                    if type(x) is dict:
                        x['process_timestamp'] = time.time()
                    share_queue_tick.put(x)
            else:
                if type(content) is dict:
                    content['process_timestamp'] = time.time()
                share_queue_tick.put(content)

            return RET_OK, content

        class ProcessTickerHandle(TickerHandlerBase):
            def on_recv_rsp(self, rsp_pb):
                """数据响应回调函数"""
                ret_code, content = super(ProcessTickerHandle, self).parse_rsp_pb(rsp_pb)

                return ProcessPushData(ret_code, content)

        class ProcessQuoteHandle(StockQuoteHandlerBase):
            def on_recv_rsp(self, rsp_pb):
                """数据响应回调函数"""
                ret_code, content = super(ProcessQuoteHandle, self).parse_rsp_pb(rsp_pb)
                return ProcessPushData(ret_code, content)

        class ProcessOrderBookHandle(OrderBookHandlerBase):
            def on_recv_rsp(self, rsp_pb):
                """数据响应回调函数"""
                ret_code, content = super(ProcessOrderBookHandle, self).parse_rsp_pb(rsp_pb)
                return ProcessPushData(ret_code, content)

        class ProcessKlineHandle(CurKlineHandlerBase):
            def on_recv_rsp(self, rsp_pb):
                """数据响应回调函数"""
                ret_code, content = super(ProcessKlineHandle, self).parse_rsp_pb(rsp_pb)
                return ProcessPushData(ret_code, content)

        class ProcessRTDataHandle(RTDataHandlerBase):
            def on_recv_rsp(self, rsp_pb):
                """数据响应回调函数"""
                ret_code, content = super(ProcessRTDataHandle, self).parse_rsp_pb(rsp_pb)
                return ProcessPushData(ret_code, content)

        class ProcessBrokerHandle(BrokerHandlerBase):
            def on_recv_rsp(self, rsp_pb):
                """数据响应回调函数"""
                ret_code, content = super(ProcessBrokerHandle, self).parse_rsp_pb(rsp_pb)
                return ProcessPushData(ret_code, content)

        quote_ctx_list  = []
        def create_new_quote_ctx(host, port):
            obj = OpenQuoteContext(host=host, port=port)
            quote_ctx_list.append(obj)
            obj.set_handler(ProcessTickerHandle())
            obj.set_handler(ProcessQuoteHandle())
            obj.set_handler(ProcessOrderBookHandle())
            obj.set_handler(ProcessKlineHandle())
            obj.set_handler(ProcessRTDataHandle())
            obj.set_handler(ProcessBrokerHandle())
            obj.start()
            return obj

        port_index = 0
        all_sub_codes = []
        quote_weight = cls.DICT_QUOTE_WEIGHT[subtype]
        while len(share_left_codes) > 0 and port_index < port_count:
            quote_ctx = create_new_quote_ctx(ip, port + port_index)
            cur_sub_one_size = sub_one_size
            data = cls.loop_get_subscription(quote_ctx)

            # 已经定阅过的不占用额度可以直接定阅
            codes = data['sub_list'][subtype] if subtype in data['sub_list'] else []
            codes_to_sub = []
            for code in codes:
                if code not in share_left_codes:
                    continue
                all_sub_codes.append(code)
                share_left_codes.remove(code)
                codes_to_sub.append(code)

            if len(codes_to_sub):
                cls.loop_subscribe_codes(quote_ctx, codes_to_sub, subtype)
                cur_sub_one_size -= len(codes_to_sub)

            # 依据剩余额度，调整要定阅的数量
            if is_adjust_sub_one_size:
                size_remain = int(data['remain'] / quote_weight)
                cur_sub_one_size = cur_sub_one_size if cur_sub_one_size < size_remain else size_remain

            # 执行定阅
            cur_sub_one_size = cur_sub_one_size if cur_sub_one_size < len(share_left_codes) else len(share_left_codes)
            if cur_sub_one_size > 0:
                codes = share_left_codes[0: cur_sub_one_size]
                [share_left_codes.remove(x) for x in codes]
                # share_left_codes = share_left_codes[cur_sub_one_size:]
                [all_sub_codes.append(x) for x in codes]
                cls.loop_subscribe_codes(quote_ctx, codes, subtype)

            port_index += 1

        # 共享记录定阅成功的股票，并标志该进程定阅完成
        [share_sub_codes.append(code) for code in all_sub_codes]
        ns_share.is_process_ready = True

        # 等待结束信息
        while ns_share.is_main_exit is False:
            sleep(0.2)

        for quote_ctx in quote_ctx_list:
            quote_ctx.close()
        quote_ctx_list = []


class CheckDelayTickerHandle(FullQuoteHandleBase):
    def __init__(self, sub_full_obj):
        self.__sub_full = sub_full_obj

    def on_recv_rsp(self, data_dict):

        code = data_dict['code']

        tm_now = time.time()
        adjust_secs = self.__sub_full.timestamp_adjust
        tm_recv = data_dict['recv_timestamp']
        delay_sec = tm_now - tm_recv - adjust_secs
        process_delay = tm_now - data_dict['process_timestamp']

        delay_secs_check = 1.5
        if abs(delay_sec) >= delay_secs_check:
            is_process_delay = abs(process_delay) >= delay_secs_check
            logger.critical("* adjust:{} delay:{}  p_delay:({}, {}) Ticker cirtical :{}".format(adjust_secs, delay_sec,
                                                                    is_process_delay, process_delay, data_dict))


if __name__ =="__main__":

    # 创建逐笔定阅对象
    sub_obj = SubscribeFullQuote(SubType.TICKER)

    # 指定回调处理对象类: 当前是逐笔， 如果是其它类型定阅，请自行定义函数实现
    sub_obj.set_handler(CheckDelayTickerHandle(sub_obj))

    # 若指定codes_pool,  配置中 sub_max / sub_stock_type_list / sub_market_list 将忽略
    # sub_obj.codes_pool = ['US.AAPL', 'HK.00700', 'HK.00772']

    # 指定config, 不指定使用默认配置数据 : SubscribeFullQuote.DEFAULT_SUB_CONFIG
    my_config = {
        "ip": "127.0.0.1",                      # FutuOpenD运行IP
        "port_begin": 11111,                    # port FutuOpenD开放的第一个端口号

        "port_count": 1,                        # 启动了多少个FutuOPenD进程，每个进程的port在port_begin上递增
        "sub_one_size": 100,                    # 最多向一个FutuOpenD定阅多少支股票
        "is_adjust_sub_one_size": True,         # 依据当前剩余定阅量动态调整一次的定阅量(测试白名单不受定阅额度限制可置Flase)
        'one_process_ports': 2,                 # 用多进程提高性能，一个进程处理多少个端口

        # 若使用property接口 "codes_pool" 指定了定阅股票， 以下配置无效
        "sub_max": 4000,                                            # 最多定阅多少支股票(需要依据定阅额度和进程数作一个合理预估）
        "sub_stock_type_list": [SecurityType.STOCK],                # 选择要定阅的股票类型
        "sub_market_list": [Market.US],                             # 要定阅的市场
    }
    sub_obj.config = my_config

    # 启动运行
    print("* begin run ...")
    sub_obj.start()
    all_sub_codes = sub_obj.success_sub_codes
    print("* all sub count:{}, codes:{}".format(len(all_sub_codes), all_sub_codes))
    print("* all is ready and running ...")

    # 运行24小时后退出
    sleep(24 * 3600)

    sub_obj.close()







