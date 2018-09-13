#-*-coding:utf-8-*-
import pandas

from futuquant.testcase.person.eva.trade.Handler import *
from futuquant.trade.open_trade_context import *
from futuquant import *
import datetime
import logging


class TradeUS(object):
    # 下单接口，查询持仓
    #背景：用户反馈ubuntu和mac同时挂机，ubuntu下单后查询持仓不是最新数据，mac查询到最新持仓。

    def __init__(self):
        pandas.set_option('max_columns', 100)
        pandas.set_option('display.width', 1000)

    def test_plateOrder_noPush(self):

        host = '127.0.0.1'
        port = 11113

        quote_ctx = OpenQuoteContext(host,11112)
        trade_us = OpenUSTradeContext(host,port)
        #日志
        logger = self.getNewLogger('plate_order_time_out_100063')
        #解锁交易
        logger.info('unlock '+str(trade_us.unlock_trade('123123')))
        # 获取美股股票列表
        ret_code_quote, ret_data = quote_ctx.get_stock_basicinfo(market=Market.US, stock_type=SecurityType.STOCK,code_list=[])
        codes = ret_data['code'].tolist()
        #逐只股票获取报价并下单
        for code in codes:
            logger.info('subscribe')
            logger.info(quote_ctx.subscribe(code, [SubType.QUOTE,SubType.ORDER_BOOK]))
            ret_code_quote,ret_data_quote = quote_ctx.get_stock_quote([code])
            ret_code_orderBook , ret_data_orderBook = quote_ctx.get_order_book(code)
            if ret_code_quote == RET_ERROR:
                logger.info('get_stock_quote '+str(ret_code_quote)+ret_data_quote)
            if  ret_code_orderBook == RET_ERROR :
                logger.info('get_order_book ' + str(ret_code_orderBook) + ret_data_orderBook)
            #获取股票现价和价差
            price_quote = ret_data_quote['last_price'].tolist()[0]
            price_spread = ret_data_quote['price_spread'].tolist()[0]
            price_spread_num = 20
            price_bid = ret_data_orderBook.get('Bid')[0][0]
            price = min(price_quote, price_bid)   #下单价格
            #下单
            acc_index = 0
            logger.info('place_order 【买入】')
            price = price - (price_spread * price_spread_num) #下买入单，低于当前价20个档位
            logger.info('code='+code+' price='+str(price))
            logger.info(trade_us.place_order(price = price, qty=1, code = code, trd_side=TrdSide.BUY, order_type=OrderType.NORMAL,adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0,acc_index=acc_index))
            time.sleep(10)
            logger.info('position_list_query')
            logger.info(trade_us.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=TrdEnv.REAL, acc_id=0,acc_index=acc_index))
            logger.info('place_order 【卖出】') #下卖出单，高于当前价20个档位
            price = price + (price_spread * price_spread_num)
            logger.info('code=' + code + ' price=' + str(price))
            logger.info(trade_us.place_order(price=price, qty=1, code=code, trd_side=TrdSide.SELL, order_type=OrderType.NORMAL,adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=0,acc_index=acc_index))
            time.sleep(10)
            logger.info('position_list_query')
            logger.info(trade_us.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=TrdEnv.REAL,acc_id=0,acc_index=acc_index))
            time.sleep(10*60)
            logger.info('unsubscribe')
            logger.info(quote_ctx.unsubscribe(code, SubType.QUOTE))

    def test_plate_order_noPush_timing(self):
        start_time = datetime.datetime( 2018, 9, 13, 15, 1, 1)
        while( start_time > datetime.datetime.now() ):
            print(datetime.datetime.now())
            sleep(60)
        #美股开盘，触发下单
        self.test_plateOrder_noPush()

    def test_mac(self):
        host = '127.0.0.1'  # mac-patrick
        port = 11111

        trade_us = OpenUSTradeContext(host, port)
        trade_us.unlock_trade('123123')
        logger = self.getNewLogger('mac_11111(2)')
        for i in range(1000):
            logger.info('position_list_query')
            logger.info(trade_us.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None,trd_env=TrdEnv.REAL, acc_id=0,acc_index=1))
            time.sleep(30*60)

    def getNewLogger(self,name,dir= None):
        '''

        :param name: 日志实例名
        :param dir: 日志所在文件夹名
        :return:
        '''
        logger = logging.getLogger(name)
        dir_path = os.getcwd() + os.path.sep + 'log'
        if dir is None:
            dir = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        dir_path = dir_path+os.path.sep+dir
        if os.path.exists(dir_path) is False:
            os.makedirs(dir_path)
        log_abs_name = dir_path + os.path.sep + name + '.txt'
        print(log_abs_name+'\n')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.FileHandler(log_abs_name)
        handler.setFormatter(formatter)
        console = logging.StreamHandler(stream=sys.stdout)

        logger.addHandler(handler)  # 设置日志输出到文件
        logger.addHandler(console)  # 设置日志输出到屏幕控制台
        logger.setLevel(logging.DEBUG)  # 设置打印的日志等级

        return logger


if __name__ == '__main__':
    trd_us = TradeUS()
    trd_us.test_plate_order_noPush_timing()

