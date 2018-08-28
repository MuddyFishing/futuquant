#-*-coding:utf-8-*-
import pandas

from futuquant.testcase.person.eva.trade.Handler import *
from futuquant.trade.open_trade_context import *
from futuquant import *
import logging


class TradeUS(object):
    # 下单接口，查询持仓
    #背景：用户反馈ubuntu和mac同时挂机，ubuntu下单后查询持仓不是最新数据，mac查询到最新持仓。

    def __init__(self):
        pandas.set_option('max_columns', 100)
        pandas.set_option('display.width', 1000)

    def test_ubuntu(self):

        host = '127.0.0.1'
        port = 11115

        quote_ctx = OpenQuoteContext(host,11111)
        trade_us = OpenUSTradeContext(host,port)

        ret_code,ret_data = quote_ctx.get_stock_basicinfo( market = Market.US, stock_type=SecurityType.STOCK)
        codes = ret_data['code'].tolist()
        # codes = ['US.XNET','US.X','US.WB','US.RUSL','US.DUC','US.BZUN','US.BRK.A','US.BIDU','US.BITA','US.A']
        acc_id = 281756460277401311

        logger = self.getNewLogger('ubuntu_11115(2)')
        logger.info('unlock' )
        logger.info(trade_us.unlock_trade('123123'))
        logger.info('subscribe')
        logger.info(quote_ctx.subscribe(codes,SubType.QUOTE))
        for code in codes:
            ret_code,ret_data = quote_ctx.get_stock_quote(code)
            price = ret_data['last_price'].tolist()[0]
            logger.info('place_order 【买入】')
            logger.info('code='+code+' price='+str(price))
            logger.info(trade_us.place_order(price = price, qty=1, code = code, trd_side=TrdSide.BUY, order_type=OrderType.NORMAL,adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=acc_id))
            time.sleep(5)
            logger.info('position_list_query')
            logger.info(trade_us.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=TrdEnv.REAL, acc_id=acc_id))
            logger.info('place_order 【卖出】')
            logger.info('code=' + code + ' price=' + str(price))
            logger.info(trade_us.place_order(price=price, qty=1, code=code, trd_side=TrdSide.SELL, order_type=OrderType.NORMAL,adjust_limit=0, trd_env=TrdEnv.REAL, acc_id=acc_id))
            time.sleep(5)
            logger.info('position_list_query')
            logger.info(trade_us.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=TrdEnv.REAL,acc_id=acc_id))
            time.sleep(30*60)

    def test_mac(self):
        host = '172.18.6.144'  # mac-patrick
        port = 11111
        acc_id = 281756460277401311 #100063
        trade_us = OpenUSTradeContext(host, port)
        trade_us.unlock_trade('123123')
        logger = self.getNewLogger('mac_11111(2)')
        for i in range(1000):
            logger.info('position_list_query')
            logger.info(trade_us.position_list_query(code='', pl_ratio_min=None, pl_ratio_max=None,
                                                                         trd_env=TrdEnv.REAL, acc_id=acc_id))
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
    # TradeUS().test_ubuntu()
    TradeUS().test_mac()