# encoding: UTF-8

'''

'''
from __future__ import division

from vnpyInc import *
from TinyDefine import *
from TinyStrateBase import TinyStrateBase
from FutuMarketEvent import *
from FutuDataEvent import *
from futuquant import *

class TinyQuantFrame(object):
    """策略frame"""
    settingFileName = 'setting.json'
    settingfilePath = getJsonPath(settingFileName, __file__)

    def __init__(self, tinyStrate):
        """frame settings"""
        self._api_ip = None
        self._api_port = None
        self._market = None
        self._env_type = None
        self._trade_password = None

        self._global_settings = {}
        self._is_init = False

        self._tiny_strate = tinyStrate
        self._logger = LogEngine()
        self._event_engine = EventEngine2()

        # 这里没有用None,因为None在 __loadSetting中当作错误参数检查用了
        self._quote_ctx = 0
        self._trade_ctx = 0
        self._check_market_event = 0
        self._futu_data_event = 0

        self._is_start = False
        self._is_init = self.__loadSetting()
        if self._is_init:
            self.__initLogEngine()
            self._tiny_strate.init_strate(self._global_settings, self, self._event_engine)

    @property
    def today_date(self):
        """今天的日期，服务器数据"""
        return self._check_market_event.today_date

    def get_rt_tiny_quote(self, symbol):
        """得到股票的实时行情数据"""
        return self._futu_data_event.get_rt_tiny_quote(symbol)

    def get_kl_min1_am(self, symbol):
        """一分钟k线的array manager数据"""
        return self._futu_data_event.get_kl_min1_am(symbol)

    def get_kl_day_am(self, symbol):
        """日k线的array manager数据"""
        return self._futu_data_event.get_kl_day_am(symbol)

    def buy(self, price, volume, symbol, price_mode=PriceRegularMode.UPPER):
        """买入"""
        ret = None
        data = None
        if self._market == MARKET_HK:
            ret, data = self._trade_ctx.place_order(price=price, qty=volume, strcode=symbol, orderside=0, ordertype=0,
                                envtype=self._env_type, order_deal_push=False, price_mode=price_mode)
        else:
            ret, data = self._trade_ctx.place_order(price=price, qty=volume, strcode=symbol, orderside=0, ordertype=2,
                                envtype=self._env_type, order_deal_push=False, price_mode=price_mode)
        if ret != 0:
            return ret, data
        order_id = 0
        for ix, row in data.iterrows():
            order_id = str(row['orderid'])

        return 0, order_id

    def sell(self, price, volume, symbol, price_mode=PriceRegularMode.LOWER):
        """卖出"""
        ret = -1
        data = None
        if self._market == MARKET_HK:
            ret, data = self._trade_ctx.place_order(price=price, qty=volume, strcode=symbol, orderside=1, ordertype=0,
                                envtype=self._env_type, order_deal_push=False, price_mode=price_mode)
        else:
            ret, data = self._trade_ctx.place_order(price=price, qty=volume, strcode=symbol, orderside=1, ordertype=2,
                                envtype=self._env_type, order_deal_push=False, price_mode=price_mode)
        if ret != 0:
            return ret, data
        order_id = 0
        for ix, row in data.iterrows():
            order_id = str(row['orderid'])

        return 0, order_id

    def cancel_order(self, order_id):
        """取消订单"""
        ret, data = self._trade_ctx.set_order_status(status=0, orderid=order_id, envtype=self._env_type)

        # ret不为0时， data为错误字符串
        if ret == 0:
            return 0, ''
        else:
            return ret, data

    def get_tiny_trade_order(self, order_id):
        """得到订单信息"""
        ret, data = self._trade_ctx.order_list_query(orderid=order_id, statusfilter='', strcode='', start='',
                                                         end='', envtype=self._env_type)
        if ret != 0:
            return ret, data

        order = TinyTradeOrder()
        for ix, row in data.iterrows():
            if order_id != str(row['orderid']):
                continue
            order.symbol = row['code']
            order.order_id = order_id
            if int(row['order_side']) == 0:
                order.direction = TRADE_DIRECT_BUY
            elif int(row['order_side']) == 1:
                order.direction = TRADE_DIRECT_SELL
            else:
                raise Exception("get_tiny_trade_order error order_side=%s" % (row['order_side']))
            order.price = float(row['price'])
            order.total_volume = int(row['qty'])
            order.trade_volume = int(row['dealt_qty'])
            order.submit_time = datetime.fromtimestamp(int(row['submited_time'])).strftime('%Y%m%d %H:%M:%S')
            order.updated_time = datetime.fromtimestamp(int(row['updated_time'])).strftime('%Y%m%d %H:%M:%S')
            order.trade_avg_price = float(row['dealt_avg_price']) if row['dealt_avg_price'] else 0
            order.order_status = int(row['status'])
            break
        return 0, order

    def get_tiny_position(self, symbol):
        """得到股票持仓"""
        ret, data = self._trade_ctx.position_list_query(strcode=symbol, envtype=self._env_type)
        if 0 != ret:
            return None

        for _, row in data.iterrows():
            if row['code'] != symbol:
                continue
            pos = TinyPosition()
            pos.symbol = symbol
            pos.position = int(row['qty'])
            pos.frozen = pos.position - int(row['can_sell_qty'])
            pos.price = float(row['cost_price'])
            pos.market_value = float(row['market_val'])
            return pos
        return None

    def writeCtaLog(self, content):
        log = VtLogData()
        log.logContent = content
        log.gatewayName = 'FUTU'
        event = Event(type_=EVENT_TINY_LOG)
        event.dict_['data'] = log
        self._event_engine.put(event)

    def __loadSetting(self):
        """读取策略配置"""
        with open(self.settingfilePath, 'rb') as f:
            df = f.read()
            f.close()
            if type(df) is not str:
                df = str(df, encoding='utf8')
            self._global_settings = json.loads(df)
            if self._global_settings is None or 'frame' not in self._global_settings:
                raise Exception("setting.json - no frame config!'")

            # 设置frame参数
            frame_setting = self._global_settings['frame']
            d = self.__dict__
            for key in d.keys():
                if key in frame_setting.keys():
                    d[key] = frame_setting[key]

            # check paramlist
            for key in d.keys():
                if d[key] is None:
                    str_error = "setting.json - 'frame' config no key:'%s'" % key
                    raise Exception(str_error)

            # check _env_type / market
            if self._env_type != 0 and self._env_type != 1:
                str_error = "setting.json - 'frame' config '_env_type' can only is 0 or 1!"
                raise Exception(str_error)

            if self._market != MARKET_HK and self._market != MARKET_US:
                str_error = "setting.json - 'frame' config '_market' can only is 'HK' or 'US'!"
                raise Exception(str_error)

            if self._market == MARKET_US and self._env_type != 0:
                str_error = "setting.json - 'frame' config '_env_type' can only is 0 if _market is US!"
                raise Exception(str_error)

        return True

    def __initLogEngine(self):
        # 设置日志级别
        frame_setting = self._global_settings['frame']
        levelDict = {
            "debug": LogEngine.LEVEL_DEBUG,
            "info": LogEngine.LEVEL_INFO,
            "warn": LogEngine.LEVEL_WARN,
            "error": LogEngine.LEVEL_ERROR,
            "critical": LogEngine.LEVEL_CRITICAL,
        }
        level = levelDict.get(frame_setting["logLevel"], LogEngine.LEVEL_CRITICAL)
        self._logger.setLogLevel(level)

        # 设置输出
        if frame_setting['logConsole']:
            self._logger.addConsoleHandler()

        if frame_setting['logFile']:
            self._logger.addFileHandler()

        # log事件监听
        self._event_engine.register(EVENT_TINY_LOG, self._logger.processLogEvent)
        self._event_engine.register(EVENT_INI_FUTU_API, self._process_init_api)

    def _process_init_api(self, event):
        if type(self._quote_ctx) != int or type(self._trade_ctx) != int:
            return

        # 创建futu api对象
        self._quote_ctx = OpenQuoteContext(self._api_ip, self._api_port)
        if self._market == MARKET_HK:
            self._trade_ctx = OpenHKTradeContext(self._api_ip, self._api_port)
        elif self._market == MARKET_US:
            self._trade_ctx = OpenUSTradeContext(self._api_ip, self._api_port)
        else:
            raise Exception("error param!")

        if self._env_type == 0:
            ret, _ = self._trade_ctx.unlock_trade(self._trade_password)
            if 0 != ret:
                raise Exception("error param!")

        # 开始futu api异步数据推送
        self._quote_ctx.start()
        self._trade_ctx.start()

        # 市场状态检查
        self._check_market_event = FutuMarketEvent(self._market, self._quote_ctx, self._event_engine)

        #定阅行情数据
        self._futu_data_event = FutuDataEvent(self, self._quote_ctx, self._event_engine, self._tiny_strate.symbol_pools)

        # 启动事件
        self._tiny_strate.on_start()

    def run(self):
        # 启动事件引擎
        if self._is_init and not self._is_start:
            self._is_start = True
            self._event_engine.put(Event(type_=EVENT_INI_FUTU_API))
            self._event_engine.start(timer=True)

if __name__ == '__main__':
    strate = TinyStrateBase()
    frame = TinyQuantFrame(strate)
    frame.run()

