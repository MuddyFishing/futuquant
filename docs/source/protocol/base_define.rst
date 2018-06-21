基础定义
==========
	这里对FutuOpenD开放协议接口中用到基本数据结构作出归档说明, 所有类型都是通过Protobuf文本定义，请通过protobuf自带工具转成对应语言的接口类对象

--------------


Common.proto
-------------

RetType - 协议返回值
~~~~~~~~~

.. code-block:: protobuf

	//返回结果
	enum RetType
	{
		RetType_Succeed = 0; //成功
		RetType_Failed = -1; //失败
		RetType_TimeOut = -100; //超时
		RetType_Unknown = -400; //未知结果
	}

.. note::

    *   RetType 定义协议请求返回值
    *   请求失败情况，除网络超时外，其它具体原因参见各协议定义的retMsg字段
 
-------------------------------------

PacketID
~~~~~~~~~~~

.. code-block:: protobuf

	//包的唯一标识，用于回放攻击的识别和保护
	message PacketID
	{
		required uint64 connID = 1; //当前TCP连接的连接ID，一条连接的唯一标识，InitConnect协议会返回
		required uint32 serialNo = 2; //包头中的包自增序列号
	}

.. note::

    *   PacketID 用于唯一标识一次请求
    *   serailNO 由请求方自定义填入包头，为防回放攻击要求自增，否则新的请求将被忽略
 
-------------------------------------


Qot_Common.proto
--------------------------

QotMarket - 行情市场
~~~~~~~~~~

 .. code-block:: protobuf

	enum QotMarket
	{
		QotMarket_Unknown = 0; //未知市场
		QotMarket_HK_Security = 1; //港股
		QotMarket_HK_Future = 2; //港期货(目前是恒指的当月、下月期货行情)
		QotMarket_US_Security = 11; //美股
		QotMarket_US_Option = 12; //美期权,暂时不支持期权
		QotMarket_CNSH_Security = 21; //沪股
		QotMarket_CNSZ_Security = 22; //深股
	}

 .. note::

    *   QotMarket定义一支证券所属的行情市场分类
    *   QotMarket_HK_Future 港股期货，目前仅支持 999010(恒指当月期货)、999011(恒指下月期货)
    *   QotMarket_US_Option 美股期权，牛牛客户端可以查看行情，API 后续支持
	
----------------------------------------------

SecurityType - 证券类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	enum SecurityType
	{
		SecurityType_Unknown = 0; //未知
		SecurityType_Bond = 1; //债券
		SecurityType_Bwrt = 2; //一揽子权证
		SecurityType_Eqty = 3; //正股
		SecurityType_Trust = 4; //信托,基金
		SecurityType_Warrant = 5; //涡轮
		SecurityType_Index = 6; //指数
		SecurityType_Plate = 7; //板块
		SecurityType_Drvt = 8; //期权
		SecurityType_PlateSet = 9; //板块集
	}
	
-----------------------------------------------
	
	
PlateSetType - 板块集合类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	enum PlateSetType
	{
		PlateSetType_All = 0; //所有板块
		PlateSetType_Industry = 1; //行业板块
		PlateSetType_Region = 2; //地域板块,港美股市场的地域分类数据暂为空
		PlateSetType_Concept = 3; //概念板块
	}

 .. note::

    *   Qot_GetPlateSet 请求参数类型
	
-----------------------------------------------
 
WarrantType - 窝轮子类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	enum WarrantType
	{
		WarrantType_Unknown = 0; //未知
		WarrantType_Buy = 1; //认购
		WarrantType_Sell = 2; //认沽
		WarrantType_Bull = 3; //牛
		WarrantType_Bear = 4; //熊
	};

 
-----------------------------------------------

QotMarketState - 行情市场状态
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	enum QotMarketState
	{
		QotMarketState_None = 0; 									// 无交易,美股未开盘
		QotMarketState_Auction = 1; 							// 竞价 
		QotMarketState_WaitingOpen = 2; 					// 早盘前等待开盘
		QotMarketState_Morning = 3; 							// 早盘 
		QotMarketState_Rest = 4; 									// 午间休市 
		QotMarketState_Afternoon = 5; 						// 午盘 
		QotMarketState_Closed = 6; 								// 收盘
		QotMarketState_PreMarketBegin = 8; 				// 盘前
		QotMarketState_PreMarketEnd = 9; 					// 盘前结束 
		QotMarketState_AfterHoursBegin = 10; 			// 盘后
		QotMarketState_AfterHoursEnd = 11; 				// 盘后结束 
		QotMarketState_NightOpen = 13; 						// 夜市开盘 
		QotMarketState_NightEnd = 14; 						// 夜市收盘 
		QotMarketState_FutureDayOpen = 15; 				// 期指日市开盘 
		QotMarketState_FutureDayBreak = 16; 			// 期指日市休市 
		QotMarketState_FutureDayClose = 17; 			// 期指日市收盘 
		QotMarketState_FutureDayWaitForOpen = 18; // 期指日市等待开盘 
		QotMarketState_HkCas = 19; 								// 盘后竞价,港股市场增加CAS机制对应的市场状态
	}

-----------------------------------------------

RehabType - K线复权类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	enum RehabType
	{
		RehabType_None = 0; //不复权
		RehabType_Forward = 1; //前复权
		RehabType_Backward = 2; //后复权
	}
	
-----------------------------------------------

KLType - K线类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	 //枚举值兼容旧协议定义
	 //新类型季K,年K,3分K暂时没有支持历史K线
	enum KLType
	{
		KLType_1Min = 1; //1分K
		KLType_Day = 2; //日K
		KLType_Week = 3; //周K
		KLType_Month = 4; //月K	
		KLType_Year = 5; //年K
		KLType_5Min = 6; //5分K
		KLType_15Min = 7; //15分K
		KLType_30Min = 8; //30分K
		KLType_60Min = 9; //60分K		
		KLType_3Min = 10; //3分K
		KLType_Quarter = 11; //季K
	}
	
-----------------------------------------------

KLFields - K线数据字段
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	enum KLFields
	{
		KLFields_High = 1; //最高价
		KLFields_Open = 2; //开盘价
		KLFields_Low = 4; //最低价
		KLFields_Close = 8; //收盘价
		KLFields_LastClose = 16; //昨收价
		KLFields_Volume = 32; //成交量
		KLFields_Turnover = 64; //成交额
		KLFields_TurnoverRate = 128; //换手率
		KLFields_PE = 256; //市盈率
		KLFields_ChangeRate = 512; //涨跌幅
	}
		
-----------------------------------------------

SubType - 行情定阅类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	 //订阅类型
	 //枚举值兼容旧协议定义
	enum SubType
	{
		SubType_None = 0;
		SubType_Basic = 1; //基础报价
		SubType_OrderBook = 2; //摆盘
		SubType_Ticker = 4; //逐笔
		SubType_RT = 5; //分时
		SubType_KL_Day = 6; //日K
		SubType_KL_5Min = 7; //5分K
		SubType_KL_15Min = 8; //15分K
		SubType_KL_30Min = 9; //30分K
		SubType_KL_60Min = 10; //60分K
		SubType_KL_1Min = 11; //1分K
		SubType_KL_Week = 12; //周K
		SubType_KL_Month = 13; //月K
		SubType_Broker = 14; //经纪队列
		SubType_KL_Qurater = 15; //季K
		SubType_KL_Year = 16; //年K
		SubType_KL_3Min = 17; //3分K
	}
	
-----------------------------------------------

TickerDirection - 逐笔方向
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	 //订阅类型
	 //枚举值兼容旧协议定义
	 enum TickerDirection
	{
		TickerDirection_Bid = 1; //外盘
		TickerDirection_Ask = 2; //内盘
		TickerDirection_Neutral = 3; //中性盘
	}
		
-----------------------------------------------

Security - 证券标识
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message Security
	{
		required int32 market = 1; //QotMarket,股票市场
		required string code = 2; //股票代码
	}

-----------------------------------------------

KLine - K线数据点
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message KLine
	{
		required string time = 1; //时间戳字符串
		required bool isBlank = 2; //是否是空内容的点,若为ture则只有时间信息
		optional double highPrice = 3; //最高价,9位小数精度
		optional double openPrice = 4; //开盘价,9位小数精度
		optional double lowPrice = 5; //最低价,9位小数精度
		optional double closePrice = 6; //收盘价,9位小数精度
		optional double lastClosePrice = 7; //昨收价,9位小数精度
		optional int64 volume = 8; //成交量
		optional double turnover = 9; //成交额,3位小数精度
		optional double turnoverRate = 10; //换手率,3位小数精度
		optional double pe = 11; //市盈率,3位小数精度
		optional double changeRate = 12; //涨跌幅,3位小数精度
	}
		
-----------------------------------------------

BasicQot - 基础报价
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message BasicQot
	{
		required Security security = 1; //股票
		required bool isSuspended = 2; //是否停牌
		required string listTime = 3; //上市日期字符串
		required double priceSpread = 4; //价差
		required string updateTime = 5; //更新时间字符串
		required double highPrice = 6; //最高价,9位小数精度
		required double openPrice = 7; //开盘价,9位小数精度
		required double lowPrice = 8; //最低价,9位小数精度
		required double curPrice = 9; //最新价,9位小数精度
		required double lastClosePrice = 10; //昨收价,9位小数精度
		required int64 volume = 11; //成交量
		required double turnover = 12; //成交额,3位小数精度
		required double turnoverRate = 13; //换手率,3位小数精度
		required double amplitude = 14; //振幅,3位小数精度
	}
		
-----------------------------------------------

TimeShare - 分时数据点
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message TimeShare
	{
		required string time = 1; //时间字符串
		required int32 minute = 2; //距离0点过了多少分钟
		required bool isBlank = 3; //是否是空内容的点,若为ture则只有时间信息
		optional double price = 4; //当前价,9位小数精度
		optional double lastClosePrice = 5; //昨收价,9位小数精度
		optional double avgPrice = 6; //均价,9位小数精度
		optional int64 volume = 7; //成交量
		optional double turnover = 8; //成交额,3位小数精度
	}
		
 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------

SecurityStaticBasic - 证券基本静态信息
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message SecurityStaticBasic
	{
		required Qot_Common.Security security = 1; //股票
		required int64 id = 2; //股票ID
		required int32 lotSize = 3; //每手数量
		required int32 secType = 4; //Qot_Common.SecurityType,股票类型
		required string name = 5; //股票名字
		required string listTime = 6; //上市时间字符串
	}
		
 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------

WarrantStaticExData - 窝轮静态信息
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message WarrantStaticExData
	{
		required int32 type = 1; //Qot_Common.WarrantType,涡轮类型
		required Qot_Common.Security owner = 2; //所属正股
	}
			
 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------

SecurityStaticInfo - 证券静态信息
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message SecurityStaticInfo
	{
		required SecurityStaticBasic basic = 1; //基本股票静态信息
		optional WarrantStaticExData warrantExData = 2; //窝轮额外股票静态信息
	}

 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------

Broker - 买卖经纪摆盘
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message Broker
	{
		required int64 id = 1; //经纪ID
		required string name = 2; //经纪名称
		required int32 pos = 3; //经纪档位
	}

 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------


Ticker - 逐笔成交
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message Ticker
	{
		required string time = 1; //时间字符串
		required int64 sequence = 2; // 唯一标识
		required int32 dir = 3; //TickerDirection, 买卖方向
		required double price = 4; //价格
		required int64 volume = 5; //成交量
		required double turnover = 6; //成交额
	}

 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------


OrderBook - 买卖十档摆盘
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message OrderBook
	{
		required double price = 1; //委托价格
		required int64 volume = 2; //委托数量
		required int32 orederCount = 3; //委托订单个数
	}

 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------

SubInfo - 单个定阅类型信息
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message SubInfo
	{
		required int32 subType = 1; //Qot_Common.SubType,订阅类型
		repeated Qot_Common.Security securityList = 2; //订阅该类型行情的股票
	}

 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------

ConnSubInfo - 单条连接定阅信息
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 .. code-block:: protobuf

	message ConnSubInfo
	{
		repeated SubInfo subInfoList = 1; //该连接订阅信息
		required int32 usedQuota = 2; //该连接已经使用的订阅额度
		required bool isOwnConnData = 3; //用于区分是否是自己连接的数据
	}

 .. note::

    *   1
    *   2
    *   3
	
-----------------------------------------------






