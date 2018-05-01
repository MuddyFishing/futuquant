#引用futuquant包
import futuquant as ft
import numpy as np
import pandas as pd
import time
#防止输出过程中由于数据太多出现省略号,忽略数据
from futuquant.quote.response_handler import *
from futuquant.common.constant import *
#设置dataframe结构的显示------pandas display设置
pd.set_option('display.height',1000)
pd.set_option('display.max_rows',None)#pandas.set_option() 可以设置pandas相关的参数，从而改变默认参数。 打印pandas数据事，默认是输出100行，多的话会输出....省略号。
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)
pd.set_option('colheader_justify', 'right')#value显示居右

from time import sleep
from futuquant import *

'''
#获取所有板块下的子版块列表
def _example_plate_list(quote_ctx):
    #定义接口参数
    market='US'#不区分沪深，输入SZ或者SH都返回沪深市场的子板块
    #plate_class='CONCEPT'
    #plate_class='INDUSTRY'
    #plate_class = 'REGION'
    plate_class = 'ALL'
    ret_code,ret_data=quote_ctx.get_plate_list(market,plate_class)
    if ret_code == RET_ERROR:
        logger.debug(ret_code)
        logger.debug(ret_data)
        exit()
    #logger.debug(ret_code)
    return ret_data

#获取版块下的股票列表
def _example_plate_stock(quote_ctx,plate_list):
    #定义参数接口
    str=[]
    str.append(plate_list.code.values)
    tmp=0;
    logger.debug(str)
    #建立空的python结构
    #df = pd.DataFrame(columns=['code', 'lot_size', 'stock_name','stock_child_type','stock_ype'])#合并dataframe结构
    df=pd.DataFrame(columns=[])
    for x in str[0]:
        #logger.debug(x)
        tmp=tmp+1
        #logger.debug(tmp)
        ret_code,ret_data=quote_ctx.get_plate_stock(x)
        if ret_code == RET_ERROR:
            logger.debug(ret_code)
            logger.debug(ret_data)
            exit()
        df=df.append(ret_data,ignore_index=True)
    #删除dataframe结构中重复的行，该过程遇到重复的行置为true，凡是为true的删除
    #IsDuplicated = df.duplicated()
    #logger.debug(IsDuplicated)
    #logger.debug(type(IsDuplicated))
    df = df.drop_duplicates()
    #删掉重复的股票后，索引不连续，重置索引
    df=df.reset_index(drop=True)
    #logger.debug(df)
    return df

#获取股票的实时K线
def _example_stock_cur_kline(quote_ctx,plate_stock):
    #定义接口参数
    #ktype = 'K_MON'
    # ktype='K_DAY'
    # #ktype='K_1M'
    # autype = 'qfq'
    # fields = None
    code_list=[]
    code_list.append(plate_stock.code.values)
    #logger.debug('code_list')
    #logger.debug(code_list)
    code=code_list[0]
    num=2
    #market = _example_plate_list.market 本来想获取市场和K线名称直接给txt文件起名，但是测试环境和现网环境下文件名没什么分别，没法起名
    ktype="K_DAY"
    autype="qfq"
    count=0
    get_kl=0
    sum=0
    logger.debug(len(code))
    code=code.tolist()#将numpy.ndarray类型妆化为list类型
    logger.debug(code)
    #合并dataframe结构
    #建立空的dataframe结构
    #df2 = pd.DataFrame(columns=['code','time_key','open','close','high','low','volume','turnover','pe_ratio','turnover_rate'])
    df2=pd.DataFrame(columns=[])
    while len(code):
        if(len(code)>=250):
            while count < 250:
                # 1、订阅股票
                ret_status, ret_data = quote_ctx.subscribe(code[count], ktype)  #
                count = count + 1
                if ret_status != RET_OK:
                    logger.debug("%s %s : %s" % (code[count], ktype, ret_data))
                    exit()
                # 2、查询订阅接口，判断是否订阅成功
                ret_status, ret_data = quote_ctx.query_subscription()  # 查询订阅接口,判断是否退订成功
                if ret_status == RET_ERROR:
                    logger.debug(ret_status)
                    exit()
                #sub_data = ret_data
                #logger.debug("订阅的股票有：")
                #logger.debug(sub_data)
            # 3、订阅一支股票，获取一支股票的K线
            while get_kl < 250:
                ret_code, ret_data = quote_ctx.get_cur_kline(code[get_kl], num, ktype, autype)  # 订阅一支股票，获取一支股票的K线
                sum = sum + 1
                if ret_code == RET_ERROR:
                    logger.debug(ret_code)
                    logger.debug(ret_data)
                    exit()
                cur_kline_table = ret_data
                logger.debug(sum)
                logger.debug(cur_kline_table)
                df2=df2.append(cur_kline_table,ignore_index=True)
                get_kl = get_kl + 1
            logger.debug(df2)
            # 跳出循环后
            # 1、退订股票
            time.sleep(60)
            count = 0  # 将count置为0
            get_kl = 0
            tmp = 0
            delete = 0
            while tmp < 250:
                ret_status, ret_data = quote_ctx.unsubscribe(code[tmp], ktype)  # 订阅一定的股票，再退订股票，防止达到订阅上限
                if ret_status == RET_ERROR:
                    logger.debug(ret_status)
                    logger.debug(ret_data)
                    exit()
                tmp = tmp + 1  # 控制循环
            # 2、查询订阅接口,判断是否退订成功
            ret_status, ret_data = quote_ctx.query_subscription()
            if ret_status == RET_ERROR:
                logger.debug(ret_status)
                exit()
            unsub_code = ret_data
            logger.debug('退订的股票有：')
            logger.debug(unsub_code)
            # 3、删除列表中的股票
            while delete < 250:
                code.pop(0)
                delete = delete + 1
            logger.debug('删除一些股票后，还剩余哪些股票：')
            logger.debug(code)
        elif (len(code) < 250):
            while (count < len(code)):
                # 1、订阅股票
                ret_status, ret_data = quote_ctx.subscribe(code[count], ktype)  #
                count = count + 1
                if ret_status != RET_OK:
                    logger.debug("%s %s : %s" % (code[count], ktype, ret_data))
                    exit()
                # 2、查询订阅接口，判断是否订阅成功
                ret_status, ret_data = quote_ctx.query_subscription()  # 查询订阅接口,判断是否退订成功
                if ret_status == RET_ERROR:
                    logger.debug(ret_status)
                    exit()
                # sub_data = ret_data
                # logger.debug("订阅的股票有：")
                # logger.debug(sub_data)
                # 3、订阅一支股票，获取一支股票的K线
            while get_kl < len(code):
                ret_code, ret_data = quote_ctx.get_cur_kline(code[get_kl], num, ktype, autype)  # 订阅一支股票，获取一支股票的K线
                sum = sum + 1
                if ret_code == RET_ERROR:
                    logger.debug(ret_code)
                    logger.debug(ret_data)
                    exit()
                cur_kline_table = ret_data
                logger.debug(sum)
                logger.debug(cur_kline_table)
                #logger.debug(type(cur_kline_table))
                df2=df2.append(cur_kline_table,ignore_index=True)
                get_kl = get_kl + 1
            logger.debug(df2)
            # 将输出的股票信息应用print函数导入txt文件
            f = open("ALL_stock_Kline/US_K_DAY_test.txt", 'w')  # out.txt文件和test.py在同一目录
            logger.debug(df2, file=f)  # 输出结果在f文件中打印出来
            f.close()  # 关闭文件并且保存

            logger.debug("完成所有股票的处理")
            break

    #将股票信息存储到txt文件
'''
class StockQuoteTest(StockQuoteHandlerBase):
    """
    获得报价推送数据
    """

    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, content = super(StockQuoteTest, self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            logger.debug("StockQuoteTest: error, msg: %s" % content)
            return RET_ERROR, content
        logger.debug("StockQuoteTest", content)
        return RET_OK, content

class HeartBeatTest(HeartBeatHandlerBase):
    """
    心跳的推送
    """
    def on_recv_rsp(self, rsp_str):
        """数据响应回调函数"""
        ret_code, timestamp = super(HeartBeatTest, self).on_recv_rsp(rsp_str)
        if ret_code == RET_OK:
            print("heart beat server timestamp = ", timestamp)
        return ret_code, timestamp

if __name__ =="__main__":
    # 实例化行情上下文对象
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111, proto_fmt=ProtoFMT.Json)

    # 获取推送数据
    code_list = ['HK.00700', 'HK.02318']
    sub_type_list = [SubType.ORDER_BOOK, SubType.K_DAY]
    # print(quote_ctx.get_global_state())
    print(quote_ctx.subscribe(code_list, sub_type_list, push=False))
    # print(quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.ETF))
    # print(quote_ctx.get_cur_kline(code_list[0], 10, SubType.K_DAY, AuType.QFQ))
    # print(quote_ctx.get_rt_data(code_list[0]))
    # print(quote_ctx.get_rt_ticker(code_list[0], 10))

    # print(quote_ctx.get_broker_queue(code_list[0]))
    # print(quote_ctx.get_order_book(code_list[0]))
    # print(quote_ctx.get_history_kline('HK.00700', start='2017-06-20', end='2017-06-22'))

    # print(quote_ctx.get_multi_points_history_kline(code_list, ['2017-06-20', '2017-06-22', '2017-06-23'], KL_FIELD.ALL, KLType.K_DAY, AuType.QFQ))
    # print(quote_ctx.get_autype_list("HK.00700"))

    # print(quote_ctx.get_trading_days(Market.HK, '2018-11-01', '2018-11-20'))
    # print(quote_ctx.get_suspension_info('SZ.300104', '2010-02-01', '2018-11-20'))

    # print(quote_ctx.get_market_snapshot('HK.21901'))
    # print(quote_ctx.get_market_snapshot(code_list))

    print(quote_ctx.get_plate_list(Market.HK, Plate.ALL))
    # print(quote_ctx.get_plate_stock('HK.BK1001'))

    sleep(3)
    quote_ctx.close()
