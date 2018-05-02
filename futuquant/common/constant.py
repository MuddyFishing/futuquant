# -*- coding: utf-8 -*-
"""
    Constant collection
"""
from copy import copy

# 需要安装的最低牛牛客户端版本号
NN_VERSION_MIN = '3.42.4962'

ORDER_STATUS = {"CANCEL": 0, "INVALID": 1, "VALID": 2, "DELETE": 3}

MESSAGE_HEAD_FMT = "<1s1sI2B2I8B"
RET_OK = 0
RET_ERROR = -1
ERROR_STR_PREFIX = 'ERROR. '
EMPTY_STRING = ''


# 协议格式
class ProtoFMT(object):
    Protobuf = 0
    Json = 1


# 交易环境
class EnvType(object):
    REAL = "REAL",
    SIMULATE = "SIMULATE",

ENVTYPE_MAP = {EnvType.REAL: 0, EnvType.SIMULATE: 1}


# 市场标识字符串
class Market(object):
    HK = "HK"
    US = "US"
    SH = "SH"
    SZ = "SZ"
    HK_FUTURE = "HK_FUTURE"
    US_OPTION = "US_OPTION"
    NONE = "N/A"

MKT_MAP = {
    Market.NONE: 0,
    Market.HK: 1,
    Market.HK_FUTURE: 2,
    Market.US: 11,
    Market.US_OPTION: 12,
    Market.SH: 21,
    Market.SZ: 22
}


# 股票类型
class SecurityType(object):
    STOCK = "STOCK"
    IDX = "IDX"
    ETF = "ETF"
    WARRANT = "WARRANT"
    BOND = "BOND"
    NONE = "N/A"

SEC_TYPE_MAP = {
    SecurityType.STOCK: 3,
    SecurityType.IDX: 6,
    SecurityType.ETF: 4,
    SecurityType.WARRANT: 5,
    SecurityType.BOND: 1,
    SecurityType.NONE: 0
}


# 窝轮类型
class WrtType(object):
    CALL = "CALL"
    PUT = "PUT"
    BULL = "BULL"
    BEAR = "BEAR"
    NONE = "N/A"

WRT_TYPE_MAP = {WrtType.CALL: 1, WrtType.PUT: 2, WrtType.BULL: 3, WrtType.BEAR: 4, WrtType.NONE: 0}


# 定阅类型
class SubType(object):
    TICKER = "TICKER"
    QUOTE = "QUOTE"
    ORDER_BOOK = "ORDER_BOOK"
    K_1M = "K_1M"
    K_5M = "K_5M"
    K_15M = "K_15M"
    K_30M = "K_30M"
    K_60M = "K_60M"
    K_DAY = "K_DAY"
    K_WEEK = "K_WEEK"
    K_MON = "K_MON"
    RT_DATA = "RT_DATA"
    BROKER = "BROKER"

SUBTYPE_MAP = {
    SubType.QUOTE: 1,
    SubType.ORDER_BOOK: 2,
    SubType.TICKER: 4,
    SubType.RT_DATA: 5,
    SubType.K_DAY: 6,
    SubType.K_5M: 7,
    SubType.K_15M: 8,
    SubType.K_30M: 9,
    SubType.K_60M: 10,
    SubType.K_1M: 11,
    SubType.K_WEEK: 12,
    SubType.K_MON: 13,
    SubType.BROKER: 14
}


# k线类型
class KLType(object):
    K_1M = "K_1M"
    K_5M = "K_5M"
    K_15M = "K_15M"
    K_30M = "K_30M"
    K_60M = "K_60M"
    K_DAY = "K_DAY"
    K_WEEK = "K_WEEK"
    K_MON = "K_MON"

KTYPE_MAP = {
    KLType.K_1M: 1,
    KLType.K_5M: 6,
    KLType.K_15M: 7,
    KLType.K_30M: 8,
    KLType.K_60M: 9,
    KLType.K_DAY: 2,
    KLType.K_WEEK: 3,
    KLType.K_MON: 4
}


# k线复权定义
class AuType(object):
    QFQ = "qfq"
    HFQ = "hfq"
    NONE = "None"

AUTYPE_MAP = {AuType.NONE: 0, AuType.QFQ: 1, AuType.HFQ: 2}


# 指定时间为非交易日时，对应的k线数据取值模式， get_multi_points_history_kline 参数用到
class KLNoDataMode(object):
    NONE = 0     # 返回无数据
    FORWARD = 1  # 往前取数据
    BACKWARD = 2  # 往后取数据


# k线数据字段
class KL_FIELD(object):
    ALL = ''
    DATE_TIME = '1'
    OPEN = '2'
    CLOSE = '3'
    HIGH = '4'
    LOW = '5'
    PE_RATIO = '6'
    TURNOVER_RATE = '7'
    TRADE_VOL = '8'
    TRADE_VAL = '9'
    CHANGE_RATE = '10'
    LAST_CLOSE = '11'

    ALL_REAL = [
        DATE_TIME, OPEN, CLOSE, HIGH, LOW, PE_RATIO, TURNOVER_RATE, TRADE_VOL,
        TRADE_VAL, CHANGE_RATE, LAST_CLOSE
    ]

    FIELD_FLAG_VAL_MAP = {
        DATE_TIME: 0,
        HIGH: 1,
        OPEN: 2,
        LOW: 4,
        CLOSE: 8,
        LAST_CLOSE: 16,
        TRADE_VOL: 32,
        TRADE_VAL: 64,
        TURNOVER_RATE: 128,
        PE_RATIO: 256,
        CHANGE_RATE: 512,
    }

    DICT_KL_FIELD_STR = {
        DATE_TIME: 'time_key',
        OPEN: 'open',
        CLOSE: 'close',
        HIGH: 'high',
        LOW: 'low',
        PE_RATIO: 'pe_ratio',
        TURNOVER_RATE: 'turnover_rate',
        TRADE_VOL: 'volume',
        TRADE_VAL: 'turnover',
        CHANGE_RATE: 'change_rate',
        LAST_CLOSE: 'last_close'
    }

    @classmethod
    def get_field_list(cls, str_filed):
        ret_list = []
        data = str(str_filed).split(',')
        if KL_FIELD.ALL in data:
            ret_list = copy(KL_FIELD.ALL_REAL)
        else:
            for x in data:
                if x in KL_FIELD.ALL_REAL:
                    ret_list.append(x)
        return ret_list

    @classmethod
    def normalize_field_list(cls, fields):
        list_ret = []
        if KL_FIELD.ALL in fields:
            list_ret = copy(KL_FIELD.ALL_REAL)
        else:
            for x in fields:
                if x in KL_FIELD.ALL_REAL and x not in list_ret:
                    list_ret.append(x)
        return list_ret

    @classmethod
    def kl_fields_to_flag_val(cls, fields):
        fields_normal = KL_FIELD.normalize_field_list(fields)
        ret_flags = 0
        for x in fields_normal:
            ret_flags += KL_FIELD.FIELD_FLAG_VAL_MAP[x]
        return ret_flags

# 成交逐笔的方向
class TickerDirect(object):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"

TICKER_DIRECTION = {
    TickerDirect.BUY: 1,
    TickerDirect.SELL: 2,
    TickerDirect.NEUTRAL: 3
}


class Plate(object):
    ALL = "ALL"
    INDUSTRY = "INDUSTRY"
    REGION = "REGION"
    CONCEPT = "CONCEPT"

PLATE_CLASS_MAP = {
    Plate.ALL: 0,
    Plate.INDUSTRY: 1,
    Plate.REGION: 2,
    Plate.CONCEPT: 3
}


# 交易报价调整类型
class PriceRegularMode(object):
    """
    港股报价需符合价位表的要求， 详见https://www.futu5.com/faq/topic1683
    价格依据价位表规整模式,如腾讯当前的价位差是0.2, price = 471.1, UPPER price = 471.2 LOWER price = 471.0
        price_mode参数会调整price至符合价位的正确报价
    """
    IGNORE = '0'  # 不调整
    UPPER = '1'  # 向上调整
    LOWER = '2'  # 向下调整


class ProtoId(object):
    InitConnect = 1001  # 初始化连接
    GlobalState = 1002  # 获取全局状态
    PushNotify = 1003  # 通知推送
    PushHeartBeat = 1004  # 通知推送

    Trd_GetAccList = 2001  # 获取业务账户列表
    Trd_UnlockTrade = 2005  # 解锁或锁定交易
    Trd_SubAccPush = 2008  # 订阅业务账户的交易推送数据

    Trd_GetFunds = 2101  # 获取账户资金
    Trd_GetPositionList = 2102  # 获取账户持仓

    Trd_GetOrderList = 2201  # 获取订单列表
    Trd_PlaceOrder = 2202  # 下单
    Trd_ModifyOrder = 2205  # 修改订单
    Trd_UpdateOrder = 2208  # 订单状态变动通知(推送)

    Trd_GetOrderFillList = 2211  # 获取成交列表
    Trd_UpdateOrderFill = 2218  # 成交通知(推送)

    Trd_GetHistoryOrderList = 2221  # 获取历史订单列表
    Trd_GetHistoryOrderFillList = 2222  # 获取历史成交列表

    # 订阅数据
    Qot_Sub = 3001  # 订阅或者反订阅
    Qot_RegQotPush = 3002  # 注册推送
    Qot_ReqSubInfo = 3003  # 获取订阅信息
    Qot_ReqStockBasic = 3004  # 获取股票基本行情
    Qot_PushStockBasic = 3005  # 推送股票基本行情
    Qot_ReqKL = 3006  # 获取K线
    Qot_PushKL = 3007  # 推送K线
    Qot_ReqRT = 3008  # 获取分时
    Qot_PushRT = 3009  # 推送分时
    Qot_ReqTicker = 3010  # 获取逐笔
    Qot_PushTicker = 3011  # 推送逐笔
    Qot_ReqOrderBook = 3012  # 获取买卖盘
    Qot_PushOrderBook = 3013  # 推送买卖盘
    Qot_ReqBroker = 3014  # 获取经纪队列
    Qot_PushBroker = 3015  # 推送经纪队列

    # 历史数据
    Qot_ReqHistoryKL = 3100  # 获取历史K线
    Qot_ReqHistoryKLPoints = 3101  # 获取多只股票历史单点K线
    Qot_ReqRehab = 3102  # 获取复权信息

    # 其他行情数据
    Qot_ReqTradeDate = 3200  # 获取市场交易日
    Qot_ReqSuspend = 3201  # 获取股票停牌信息
    Qot_ReqStockList = 3202  # 获取股票列表
    Qot_ReqStockSnapshot = 3203  # 获取股票快照
    Qot_ReqPlateSet = 3204  # 获取板块集合下的板块
    Qot_ReqPlateStock = 3205  # 获取板块下的股票


class TRADE(object):
    REV_MKT_MAP = {MKT_MAP[x]: x for x in MKT_MAP}
    REV_SEC_TYPE_MAP = {SEC_TYPE_MAP[x]: x for x in SEC_TYPE_MAP}
    REV_SUBTYPE_MAP = {SUBTYPE_MAP[x]: x for x in SUBTYPE_MAP}
    REV_KTYPE_MAP = {KTYPE_MAP[x]: x for x in KTYPE_MAP}
    REV_AUTYPE_MAP = {AUTYPE_MAP[x]: x for x in AUTYPE_MAP}
    REV_TICKER_DIRECTION = {TICKER_DIRECTION[x]: x for x in TICKER_DIRECTION}
    REV_ORDER_STATUS = {ORDER_STATUS[x]: x for x in ORDER_STATUS}
    REV_ENVTYPE_MAP = {ENVTYPE_MAP[x]: x for x in ENVTYPE_MAP}
    REV_ENVTYPE_STR_MAP = {str(ENVTYPE_MAP[x]): x for x in ENVTYPE_MAP}

    # 港股支持模拟和真实环境
    @staticmethod
    def check_envtype_hk(envtype):
        return str(envtype) in TRADE.REV_ENVTYPE_STR_MAP

    # 美股目前不支持模拟环境
    @staticmethod
    def check_envtype_us(envtype):
        return str(envtype) == u'0'


# noinspection PyPep8Naming
class QUOTE(object):
    REV_MKT_MAP = {MKT_MAP[x]: x for x in MKT_MAP}
    REV_WRT_TYPE_MAP = {WRT_TYPE_MAP[x]: x for x in WRT_TYPE_MAP}
    REV_PLATE_CLASS_MAP = {PLATE_CLASS_MAP[x]: x for x in PLATE_CLASS_MAP}
    REV_SEC_TYPE_MAP = {SEC_TYPE_MAP[x]: x for x in SEC_TYPE_MAP}
    REV_SUBTYPE_MAP = {SUBTYPE_MAP[x]: x for x in SUBTYPE_MAP}
    REV_KTYPE_MAP = {KTYPE_MAP[x]: x for x in KTYPE_MAP}
    REV_AUTYPE_MAP = {AUTYPE_MAP[x]: x for x in AUTYPE_MAP}
    REV_TICKER_DIRECTION = {TICKER_DIRECTION[x]: x for x in TICKER_DIRECTION}


# sys notify info
class SysNotifyType(object):
    NONE = 0
    GTW_EVENT = 1


class GtwEventType(object):
    NONE = ""
    LocalCfgLoadFailed = "LocalCfgLoadFailed"
    APISvrRunFailed = "APISvrRunFailed"
    ForceUpdate = "ForceUpdate"
    LoginFailed = "LoginFailed"
    UnAgreeDisclaimer = "UnAgreeDisclaimer"
    NetCfgMissing = "NetCfgMissing"
    KickedOut = "KickedOut"
    LoginPwdChanged = "LoginPwdChanged"
    TradePwdChanged = "TradePwdChanged"
    BanLogin = "BanLogin"
    NeedPicVerifyCode = "NeedPicVerifyCode"
    NeedPhoneVerifyCode = "NeedPhoneVerifyCode"
    NessaryDataMissing = "NessaryDataMissing"

GTW_EVENT_MAP = {
    GtwEventType.NONE: 0,
    GtwEventType.LocalCfgLoadFailed: 1,
    GtwEventType.APISvrRunFailed: 2,
    GtwEventType.ForceUpdate: 3,
    GtwEventType.LoginFailed: 4,
    GtwEventType.UnAgreeDisclaimer: 5,
    GtwEventType.NetCfgMissing: 6,
    GtwEventType.KickedOut: 7,
    GtwEventType.LoginPwdChanged: 8,
    GtwEventType.TradePwdChanged: 9,
    GtwEventType.BanLogin: 10,
    GtwEventType.NeedPicVerifyCode: 11,
    GtwEventType.NeedPhoneVerifyCode: 12,
    GtwEventType.NessaryDataMissing: 13,
}

class SysNoitfy(object):
    REV_GTW_EVENT_MAP = {GTW_EVENT_MAP[x]: x for x in GTW_EVENT_MAP}