========
行情API
========


一分钟上手
============

如下范例，创建api行情对象，调用get_market_snapshot获取港股腾讯00700的报价快照数据,最后关闭对象

.. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_market_snapshot('HK.00700'))
    quote_ctx.close()
    
----------------------------


接口类对象
==========

OpenQuoteContext - 行情上下文对象类
-------------------------------------------


close
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: close

关闭上下文对象。

.. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    quote_ctx.close()
    
    
start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: start

启动异步接收推送数据


stop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: stop

停止异步接收推送数据


set_handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: set_handler(self, handler)

 设置异步回调处理对象

 :param handler: 回调处理对象，必须是以下类的子类实例

            ===============================    =========================
             类名                                 说明
            ===============================    =========================
            StockQuoteHandlerBase               报价处理基类
            OrderBookHandlerBase                摆盘处理基类
            CurKlineHandlerBase                 实时k线处理基类
            TickerHandlerBase                   逐笔处理基类
            RTDataHandlerBase                   分时数据处理基类
            BrokerHandlerBase                   经济队列处理基类
            ===============================    =========================
 :return ret: RET_OK: 设置成功

        其它: 设置失败

get_trading_days
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_trading_days(self, market, start_date=None, end_date=None)

 获取交易日

 :param market: 市场类型，futuquant.common.constsnt.Market
 :param start_date: 起始日期
 :param end_date: 结束日期
 :return: 成功时返回(RET_OK, data)，data是字符串数组；失败时返回(RET_ERROR, data)，其中data是错误描述字符串
        
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_trading_days(market=Market.HK))
    quote_ctx.close()

get_stock_basicinfo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_stock_basicinfo(self, market, stock_type=SecurityType.STOCK, code_list=None)

 获取指定市场中特定类型的股票基本信息
 
 :param market: 市场类型，futuquant.common.constsnt.Market
 :param stock_type: 股票类型， futuquant.common.constsnt.SecurityType
 :param code_list: 如果不为None，应该是股票code的iterable类型，将只返回指定的股票信息
 :return: (ret_code, content)

        ret_code 等于RET_OK时， content为Pandas.DataFrame数据, 否则为错误原因字符串, 数据列格式如下
        
        =================   ===========   ==============================================================================
        参数                  类型                        说明
        =================   ===========   ==============================================================================
        code                str            股票代码
        name                str            名字
        lot_size            int            每手数量
        stock_type          str            股票类型，参见SecurityType
        stock_child_type    str            涡轮子类型，参见WrtType
        stock_owner         str            正股代码
        listing_date        str            上市时间
        stock_id            int            股票id
        =================   ===========   ==============================================================================

 :example:

 .. code-block:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.WARRANT))
    quote_ctx.close()
    
    
get_multiple_history_kline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_multiple_history_kline(self, codelist, start=None, end=None, ktype=KLType.K_DAY, autype=AuType.QFQ)

 获取多只股票的历史k线数据

 :param codelist: 股票代码列表，list或str。例如：['HK.00700', 'HK.00001']，'HK.00700,SZ.399001'
 :param start: 起始时间
 :param end: 结束时间
 :param ktype: k线类型，参见KLType
 :param autype: 复权类型，参见AuType
 :return: 成功时返回(RET_OK, [data])，data是DataFrame数据, 数据列格式如下

    =================   ===========   ==============================================================================
    参数                  类型                        说明
    =================   ===========   ==============================================================================
    code                str            股票代码
    time_key            str            k线时间
    open                float          开盘价
    close               float          收盘价
    high                float          最高价
    low                 float          最低价
    pe_ratio            float          市盈率
    turnover_rate       float          换手率
    volume              int            成交量
    turnover            float          成交额
    change_rate         float          涨跌幅
    last_close          float          昨收价
    =================   ===========   ==============================================================================

	失败时返回(RET_ERROR, data)，其中data是错误描述字符串
	
 :example:

 .. code-block:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_multiple_history_kline(['HK.00700'], '2017-06-20', '2017-06-25', KL_FIELD.ALL, KLType.K_DAY, AuType.QFQ))
    quote_ctx.close()


get_history_kline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_history_kline

 得到本地历史k线，需先参照帮助文档下载k线

 :param code: 股票代码
 :param start: 开始时间，例如2017-06-20
 :param end:  结束时间
 :param ktype: k线类型， 参见 KLType 定义
 :param autype: 复权类型, 参见 AuType 定义
 :param fields: 需返回的字段列表，参见 KL_FIELD 定义 KL_FIELD.ALL  KL_FIELD.OPEN ....
 :return: (ret, data)

        ret == RET_OK 返回pd Dataframe数据, 数据列格式如下

        ret != RET_OK 返回错误字符串

    =================   ===========   ==============================================================================
    参数                  类型                        说明
    =================   ===========   ==============================================================================
    code                str            股票代码
    time_key            str            k线时间
    open                float          开盘价
    close               float          收盘价
    high                float          最高价
    low                 float          最低价
    pe_ratio            float          市盈率
    turnover_rate       float          换手率
    volume              int            成交量
    turnover            float          成交额
    change_rate         float          涨跌幅
    last_close          float          昨收价
    =================   ===========   ==============================================================================

	
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_history_kline('HK.00700', start='2017-06-20', end='2017-06-22'))
    quote_ctx.close()


get_autype_list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_autype_list(self, code_list)

 获取给定股票列表的复权因子

 :param code_list: 股票列表，例如['HK.00700']
 :return: (ret, data)

        ret == RET_OK 返回pd dataframe数据，data.DataFrame数据, 数据列格式如下

        ret != RET_OK 返回错误字符串

        =====================   ===========   =================================================================
        参数                      类型                        说明
        =====================   ===========   =================================================================
        code                    str            股票代码
        ex_div_date             str            除权除息日
        split_ratio             float          拆合股比例； double，例如，对于5股合1股为1/5，对于1股拆5股为5/1
        per_cash_div            float          每股派现
        per_share_div_ratio     float          每股送股比例
        per_share_trans_ratio   float          每股转增股比例
        allotment_ratio         float          每股配股比例
        allotment_price         float          配股价
        stk_spo_ratio           float          增发比例
        stk_spo_price           float          增发价格
        forward_adj_factorA     float          前复权因子A
        forward_adj_factorB     float          前复权因子B
        backward_adj_factorA    float          后复权因子A
        backward_adj_factorB    float          后复权因子B
        =====================   ===========   =================================================================
		
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_autype_list(["HK.00700"]))
    quote_ctx.close()

get_market_snapshot
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_market_snapshot(self, code_list)

获取市场快照

 :param code_list: 股票列表，限制最多200只股票
 :return: (ret, data)

        ret == RET_OK 返回pd dataframe数据，data.DataFrame数据, 数据列格式如下

        ret != RET_OK 返回错误字符串

        =======================   =============   ==============================================================
        参数                       类型                        说明
        =======================   =============   ==============================================================
        code                       str            股票代码
        update_time                str            更新时间(yyyy-MM-dd HH:mm:ss)
        last_price                 float          最新价格
        open_price                 float          今日开盘价
        high_price                 float          最高价格
        low_price                  float          最低价格
        prev_close_price           float          昨收盘价格
        volume                     int            成交数量
        turnover                   float          成交金额
        turnover_rate              float          换手率
        suspension                 bool           是否停牌(True表示停牌)
        listing_date               str            上市日期 (yyyy-MM-dd)
        circular_market_val        float          流通市值
        total_market_val           float          总市值
        wrt_valid                  bool           是否是窝轮
        wrt_conversion_ratio       float          换股比率
        wrt_type                   str            窝轮类型，参见WrtType
        wrt_strike_price           float          行使价格
        wrt_maturity_date          str            格式化窝轮到期时间
        wrt_end_trade              str            格式化窝轮最后交易时间
        wrt_code                   str            窝轮对应的正股
        wrt_recovery_price         float          窝轮回收价
        wrt_street_vol             float          窝轮街货量
        wrt_issue_vol              float          窝轮发行量
        wrt_street_ratio           float          窝轮街货占比
        wrt_delta                  float          窝轮对冲值
        wrt_implied_volatility     float          窝轮引伸波幅
        wrt_premium                float          窝轮溢价
        lot_size                   int            每手股数
        issued_shares              int            发行股本
        net_asset                  int            资产净值
        net_profit                 int            净利润
        earning_per_share          float          每股盈利
        outstanding_shares         int            流通股本
        net_asset_per_share        float          每股净资产
        ey_ratio                   float          收益率
        pe_ratio                   float          市盈率
        pb_ratio                   float          市净率
        price_spread               float          当前摆盘价差亦即摆盘数据的买档或卖档的相邻档位的报价差
        =======================   =============   ==============================================================
        
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_market_snapshot('HK.00700'))
    quote_ctx.close()

get_rt_data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_rt_data(self, code)

 获取指定股票的分时数据

 :param code: 股票代码，例如，HK.00700，US.APPL
 :return (ret, data): ret == RET_OK 返回pd Dataframe数据, 数据列格式如下

        ret != RET_OK 返回错误字符串

        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                    str            股票代码
        time                    str            时间(yyyy-MM-dd HH:mm:ss)
        is_blank                bool           数据状态；正常数据为False，伪造数据为True
        opened_mins             int            零点到当前多少分钟
        cur_price               float          当前价格
        last_close              float          昨天收盘的价格
        avg_price               float          平均价格
        volume                  float          成交量
        turnover                float          成交金额
        =====================   ===========   ==============================================================

 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
	quote_ctx.subscribee(['HK.00700'], [SubType.RT_DATA])
    print(quote_ctx.get_rt_data('HK.00700'))
    quote_ctx.close()
	
get_plate_stock
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_plate_stock(self, plate_code)

 获取特定板块下的股票列表

 :param plate_code: 板块代码, string, 例如，”SH.BK0001”，”SH.BK0002”，先利用获取子版块列表函数获取子版块代码
 :return (ret, data): ret == RET_OK 返回pd dataframe数据，data.DataFrame数据, 数据列格式如下

        ret != RET_OK 返回错误字符串

        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                    str            股票代码
        lot_size                int            每手股数
        stock_name              str            股票名称
        stock_owner             str            所属正股的代码
        stock_child_type        str            股票子类型，参见WrtType
        stock_type              str            股票类型，参见SecurityType
        list_time               str            上市时间
        stock_id                int            股票id
        =====================   ===========   ==============================================================

 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_plate_stock('HK.BK1001'))
    quote_ctx.close()		
        
get_plate_list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_plate_list(self, market, plate_class)

 获取板块集合下的子板块列表

 :param market: 市场标识，注意这里不区分沪，深,输入沪或者深都会返回沪深市场的子板块（这个是和客户端保持一致的）参见Market
 :param plate_class: 板块分类，参见Plate
 :return (ret, data): ret == RET_OK 返回pd Dataframe数据，数据列格式如下

        ret != RET_OK 返回错误字符串

        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                    str            股票代码
        plate_name              str            板块名字
        plate_id                str            板块id
        =====================   ===========   ==============================================================

 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_plate_list(Market.HK, Plate.ALL))
    quote_ctx.close()
        
get_broker_queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_broker_queue(self, code)

 获取股票的经纪队列

 :param code: 股票代码
 :return: (ret, bid_frame_table, ask_frame_table)或(ret, err_message)

        ret == RET_OK 返回pd dataframe数据，数据列格式如下

        ret != RET_OK 返回错误字符串

        bid_frame_table 经纪买盘数据
        
        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                    str             股票代码
        bid_broker_id           int             经纪买盘id
        bid_broker_name         str             经纪买盘名称
        bid_broker_pos          int             经纪档位
        =====================   ===========   ==============================================================

        ask_frame_table 经纪卖盘数据
        
        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                    str             股票代码
        ask_broker_id           int             经纪卖盘id
        ask_broker_name         str             经纪卖盘名称
        ask_broker_pos          int             经纪档位
        =====================   ===========   ==============================================================

 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
	quote_ctx.subscribee(['HK.00700'], [SubType.BROKER])
    print(quote_ctx.get_broker_queue('HK.00700'))
    quote_ctx.close()
		
subscribe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: subscribe(self, code_list, subtype_list)

 订阅注册需要的实时信息，指定股票和订阅的数据类型即可，港股订阅需要Lv2行情。
 
 注意：len(code_list) * 订阅的K线类型的数量 <= 100

 :param code_list: 需要订阅的股票代码列表
 :param subtype_list: 需要订阅的数据类型列表，参见SubType
 :return: (ret, err_message)

        ret == RET_OK err_message为None
        
        ret != RET_OK err_message为错误描述字符串
        
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.subscribe(['HK.00700'], [SubType.QUOTE]))
    quote_ctx.close()
		
		
unsubscribe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: unsubscribe(self, code_list, subtype_list)

 取消订阅
 
 :param code_list: 取消订阅的股票代码列表
 :param subtype_list: 取消订阅的类型，参见SubType
 :return: (ret, err_message)
        
        ret == RET_OK err_message为None
        
        ret != RET_OK err_message为错误描述字符串
     
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.unsubscribe(['HK.00700'], [SubType.QUOTE]))
    quote_ctx.close()	 
        
query_subscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: query_subscription(self, is_all_conn=True)

查询已订阅的实时信息

:param is_all_conn: 是否返回所有连接的订阅状态,不传或者传False只返回当前连接数据
:return: (ret, data)  
        
        ret != RET_OK 返回错误字符串
        
        ret == RET_OK 返回 定阅信息的字典数据 ，格式如下:
        
.. code:: python

        {
            'total_used': 4,    # 所有连接已使用的定阅额度
            'own_used': 0,       # 当前连接已使用的定阅额度
            'remain': 496,       #  剩余的定阅额度
            'sub_list':          #  每种定阅类型对应的股票列表
            {
                'BROKER': ['HK.00700', 'HK.02318'],
                'RT_DATA': ['HK.00700', 'HK.02318']
            }
        }



:example:


 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.query_subscription())
    quote_ctx.close()
        
		
get_global_state
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_global_state(self)

 获取全局状态

 :return: (ret, data)

		ret == RET_OK data为包含全局状态的字典，含义如下

		ret != RET_OK data为错误描述字符串

		=====================   ===========   ==============================================================
		key                      value类型                        说明
		=====================   ===========   ==============================================================
		market_sz               str            深圳市场状态，参见MarketState
		market_us               str            美国市场状态，参见MarketState
		market_sh               str            上海市场状态，参见MarketState
		market_hk               str            香港市场状态，参见MarketState
		market_hkfuture           str            香港期货市场状态，参见MarketState
		server_ver              str            FutuOpenD版本号
		trd_logined             str            '1'：已登录交易服务器，'0': 未登录交易服务器
		qot_logined             str            '1'：已登录行情服务器，'0': 未登录行情服务器
		timestamp               str            当前格林威治时间戳
		=====================   ===========   ==============================================================
 
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_global_state())
    quote_ctx.close()

get_stock_quote
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_stock_quote(self, code_list)

 获取订阅股票报价的实时数据，有订阅要求限制

 :param code_list: 股票代码列表，必须确保code_list中的股票均订阅成功后才能够执行
 :return: (ret, data)

        ret == RET_OK 返回pd dataframe数据，数据列格式如下

        ret != RET_OK 返回错误字符串

        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                    str            股票代码
        data_date               str            日期
        data_time               str            时间
        last_price              float          最新价格
        open_price              float          今日开盘价
        high_price              float          最高价格
        low_price               float          最低价格
        prev_close_price        float          昨收盘价格
        volume                  int            成交数量
        turnover                float          成交金额
        turnover_rate           float          换手率
        amplitude               int            振幅
        suspension              bool           是否停牌(True表示停牌)
        listing_date            str            上市日期 (yyyy-MM-dd)
        price_spread            float          当前价差，亦即摆盘数据的买档或卖档的相邻档位的报价差
		dark_status             str            暗盘交易状态，见DarkStatus
        =====================   ===========   ==============================================================
		
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_stock_quote(['HK.00700']))
    quote_ctx.close()
        
get_rt_ticker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_rt_ticker(self, code, num=500)

 获取指定股票的实时逐笔。取最近num个逐笔

 :param code: 股票代码
 :param num: 最近ticker个数，最多可获取1000个
 :return: (ret, data)

        ret == RET_OK 返回pd dataframe数据，数据列格式如下

        ret != RET_OK 返回错误字符串

        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                     str            股票代码
        sequence                 int            逐笔序号
        time                     str            成交时间
        price                    float          成交价格
        volume                   int            成交数量（股数）
        turnover                 float          成交金额
        ticker_direction         str            逐笔方向
		type                     str            逐笔类型，参见TickerType
        =====================   ===========   ==============================================================

 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
	quote_ctx.subscribee(['HK.00700'], [SubType.TICKER])
    print(quote_ctx.get_rt_ticker('HK.00700', 10))
    quote_ctx.close()

get_cur_kline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_cur_kline(self, code, num, ktype=SubType.K_DAY, autype=AuType.QFQ)

 实时获取指定股票最近num个K线数据

 :param code: 股票代码
 :param num:  k线数据个数，最多1000根
 :param ktype: k线类型，参见KLType
 :param autype: 复权类型，参见AuType
 :return: (ret, data)

        ret == RET_OK 返回pd dataframe数据，数据列格式如下

        ret != RET_OK 返回错误字符串

        =====================   ===========   ==============================================================
        参数                      类型                        说明
        =====================   ===========   ==============================================================
        code                     str            股票代码
        time_key                 str            时间
        open                     float          开盘价
        close                    float          收盘价
        high                     float          最高价
        low                      float          最低价
        volume                   int            成交量
        turnover                 float          成交额
        pe_ratio                 float          市盈率
        turnover_rate            float          换手率
        last_close               float          昨收价
        =====================   ===========   ==============================================================
		
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
	quote_ctx.subscribee(['HK.00700'], [SubType.K_DAY])
    print(quote_ctx.get_cur_kline('HK.00700', 10, SubType.K_DAY, AuType.QFQ))
    quote_ctx.close()
        
get_order_book
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_order_book(self, code)

 获取实时摆盘数据

 :param code: 股票代码
 :return: (ret, data)

        ret == RET_OK 返回字典，数据格式如下

        ret != RET_OK 返回错误字符串

 .. code:: python

        {
            'code': 股票代码
            'Ask':[ (ask_price1, ask_volume1，order_num), (ask_price2, ask_volume2, order_num),…]
            'Bid': [ (bid_price1, bid_volume1, order_num), (bid_price2, bid_volume2, order_num),…]
        }

        'Ask'：卖盘， 'Bid'买盘。每个元组的含义是(委托价格，委托数量，委托订单数)
        
:example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
	quote_ctx.subscribee(['HK.00700'], [SubType.ORDER_BOOK])
    print(quote_ctx.get_order_book('HK.00700'))
    quote_ctx.close()


        
get_multi_points_history_kline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_multi_points_history_kline(self, code_list, dates, fields, ktype=KLType.K_DAY, autype=AuType.QFQ, no_data_mode=KLNoDataMode.FORWARD)

 获取多支股票多个时间点的指定数据列

 :param code_list: 单个或多个股票 'HK.00700'  or  ['HK.00700', 'HK.00001']
 :param dates: 单个或多个日期 '2017-01-01' or ['2017-01-01', '2017-01-02']，最多5个时间点
 :param fields: 单个或多个数据列 KL_FIELD.ALL or [KL_FIELD.DATE_TIME, KL_FIELD.OPEN]
 :param ktype: K线类型
 :param autype: 复权类型
 :param no_data_mode: 指定时间为非交易日时，对应的k线数据取值模式，参见KLNoDataMode
 :return: (ret, data)

        ret == RET_OK 返回pd dataframe数据，固定表头包括'code'(代码) 'time_point'(指定的日期) 'data_status' (KLDataStatus)。数据列格式如下

        ret != RET_OK 返回错误字符串

    =================   ===========   ==============================================================================
    参数                  类型                        说明
    =================   ===========   ==============================================================================
    code                str            股票代码
    time_point          str            请求的时间
    data_status         str            数据点是否有效，参见KLDataStatus
    time_key            str            k线时间
    open                float          开盘价
    close               float          收盘价
    high                float          最高价
    low                 float          最低价
    pe_ratio            float          市盈率
    turnover_rate       float          换手率
    volume              int            成交量
    turnover            float          成交额
    change_rate         float          涨跌幅
    last_close          float          昨收价
    =================   ===========   ==============================================================================
    
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_multi_points_history_kline(['HK.00700'], '2017-06-20', '2017-06-25', KL_FIELD.ALL, KLType.K_DAY, AuType.QFQ))
    quote_ctx.close()	
	
	
	
get_referencestock_list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_referencestock_list(self, code, reference_type)


 获取证券的关联数据
 
 :param code: 证券id，str，例如HK.00700
 :param reference_type: 要获得的相关数据，参见SecurityReferenceType。例如WARRANT，表示获取正股相关的涡轮
 :return: (ret, data)

		ret == RET_OK 返回pd dataframe数据，数据列格式如下

		ret != RET_OK 返回错误字符串
		
		=================   ===========   ==============================================================================
		参数                  类型                        说明
		=================   ===========   ==============================================================================
		code                str            证券代码
		lot_size            int            每手数量
		stock_type          str            证券类型，参见SecurityType
		stock_name          str            证券名字
		list_time           str            上市时间
		wrt_valid           bool           是否是涡轮，如果为True，下面wrt开头的字段有效
		wrt_type            str            涡轮类型，参见WrtType
		wrt_code            str            所属正股
		=================   ===========   ==============================================================================
		
 :example:

 .. code:: python

    from futuquant import *
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.get_referencestock_list('HK.00700', SecurityReferenceType.WARRANT))
    quote_ctx.close()	

---------------------------------------------------------------------    


StockQuoteHandlerBase - 实时报价回调处理类
-------------------------------------------

异步处理推送的订阅股票的报价。

.. code:: python
    
	import time
	from futuquant import *
	
	class StockQuoteTest(StockQuoteHandlerBase):
		def on_recv_rsp(self, rsp_str):
			ret_code, data = super(StockQuoteTest,self).on_recv_rsp(rsp_str)
			if ret_code != RET_OK:
				print("StockQuoteTest: error, msg: %s" % data)
				return RET_ERROR, data

			print("StockQuoteTest ", data) # StockQuoteTest自己的处理逻辑

			return RET_OK, data
			
	quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
	handler = StockQuoteTest()
	quote_ctx.set_handler(handler)
	time.sleep(15)  
	quote_ctx.close()	
                
-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)

 在收到实时报价推送后会回调到该函数，使用者需要在派生类中覆盖此方法

 注意该回调是在独立子线程中

 :param rsp_pb: 派生类中不需要直接处理该参数
 :return: 参见get_stock_quote的返回值
    
----------------------------

OrderBookHandlerBase - 实时摆盘回调处理类
-------------------------------------------

异步处理推送的实时摆盘。

.. code:: python
    
	import time
	from futuquant import *
	
	class OrderBookTest(OrderBookHandlerBase):
		def on_recv_rsp(self, rsp_str):
			ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_str)
			if ret_code != RET_OK:
				print("OrderBookTest: error, msg: %s" % data)
				return RET_ERROR, data

			print("OrderBookTest ", data) # OrderBookTest自己的处理逻辑

			return RET_OK, data
			
	quote_ctx = OpenQuoteContex(host='127.0.0.1', port=11111)
	handler = OrderBookTest()
	quote_ctx.set_handler(handler)
	time.sleep(15)  
	quote_ctx.close()
            
-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)


 在收到实摆盘数据推送后会回调到该函数，使用者需要在派生类中覆盖此方法

 注意该回调是在独立子线程中

 :param rsp_pb: 派生类中不需要直接处理该参数
 :return: 参见get_order_book的返回值
    
----------------------------

CurKlineHandlerBase - 实时k线推送回调处理类
-------------------------------------------

异步处理推送的k线数据。

.. code:: python

	import time
	from futuquant import *

	class CurKlineTest(CurKlineHandlerBase):
		def on_recv_rsp(self, rsp_str):
			ret_code, data = super(CurKlineTest,self).on_recv_rsp(rsp_str)
			if ret_code != RET_OK:
				print("CurKlineTest: error, msg: %s" % data)
				return RET_ERROR, data

			print("CurKlineTest ", data) # CurKlineTest自己的处理逻辑

			return RET_OK, data

	quote_ctx = OpenQuoteContex(host='127.0.0.1', port=11111)
	handler = CurKlineTest()
	quote_ctx.set_handler(handler)
	time.sleep(15)  
	quote_ctx.close()			

-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)


 在收到实时k线数据推送后会回调到该函数，使用者需要在派生类中覆盖此方法

 注意该回调是在独立子线程中

 :param rsp_pb: 派生类中不需要直接处理该参数
 :return: 参见get_cur_kline的返回值
    
----------------------------

TickerHandlerBase - 实时逐笔推送回调处理类
-------------------------------------------

异步处理推送的逐笔数据。

.. code:: python
    
	import time
	from futuquant import *
	
	class TickerTest(TickerHandlerBase):
		def on_recv_rsp(self, rsp_str):
			ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_str)
			if ret_code != RET_OK:
				print("CurKlineTest: error, msg: %s" % data)
				return RET_ERROR, data

			print("TickerTest ", data) # TickerTest自己的处理逻辑

			return RET_OK, data
                
	quote_ctx = OpenQuoteContex(host='127.0.0.1', port=11111)
	handler = TickerTest()
	quote_ctx.set_handler(handler)
	time.sleep(15)  
	quote_ctx.close()

-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)


 在收到实时逐笔数据推送后会回调到该函数，使用者需要在派生类中覆盖此方法

 注意该回调是在独立子线程中

 :param rsp_pb: 派生类中不需要直接处理该参数
 :return: 参见get_rt_ticker的返回值

----------------------------

RTDataHandlerBase - 实时分时推送回调处理类
-------------------------------------------

异步处理推送的分时数据。

.. code:: python
    
	import time
	from futuquant import *
	
	class RTDataTest(RTDataHandlerBase):
		def on_recv_rsp(self, rsp_str):
			ret_code, data = super(RTDataTest,self).on_recv_rsp(rsp_str)
			if ret_code != RET_OK:
				print("RTDataTest: error, msg: %s" % data)
				return RET_ERROR, data

			print("RTDataTest ", data) # RTDataTest自己的处理逻辑

			return RET_OK, data
                
	quote_ctx = OpenQuoteContex(host='127.0.0.1', port=11111)
	handler = RTDataTest()
	quote_ctx.set_handler(handler)
	time.sleep(15)  
	quote_ctx.close()
	
-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)


 在收到实时逐笔数据推送后会回调到该函数，使用者需要在派生类中覆盖此方法

 注意该回调是在独立子线程中

 :param rsp_pb: 派生类中不需要直接处理该参数
 :return: 参见get_rt_data的返回值

----------------------------

BrokerHandlerBase - 实时经纪推送回调处理类
-------------------------------------------

异步处理推送的分时数据。

异步处理推送的经纪数据。

.. code:: python
    
	import time
	from futuquant import *
	
	class BrokerTest(BrokerHandlerBase):
		def on_recv_rsp(self, rsp_str):
			ret_code, data = super(BrokerTest,self).on_recv_rsp(rsp_str)
			if ret_code != RET_OK:
				print("BrokerTest: error, msg: %s" % data)
				return RET_ERROR, data

			print("BrokerTest ", data) # BrokerTest自己的处理逻辑

			return RET_OK, data
                
	quote_ctx = OpenQuoteContex(host='127.0.0.1', port=11111)
	handler = BrokerTest()
	quote_ctx.set_handler(handler)
	time.sleep(15)  
	quote_ctx.close()
	
-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)


 在收到实时经纪数据推送后会回调到该函数，使用者需要在派生类中覆盖此方法

 注意该回调是在独立子线程中

 :param rsp_pb: 派生类中不需要直接处理该参数
 :return: 参见get_broker_queue的返回值

----------------------------    


接口入参限制
============ 

 ===============================        =========================
 接口名称                               入参限制
 ===============================        =========================
 get_market_snapshot                    传入股票最多200个
 get_rt_ticker				            可获取逐笔最多最近1000个
 get_cur_kline				            可获取K线最多最近1000根
 get_multi_points_history_kline         时间点最多5个
 ===============================        =========================

----------------------------

接口限频
========

低频数据接口
------------

低频数据接口是指不需要定阅就可以请求数据的接口， api的请求到达网关客户端后， 会转发请求到futu后台服务器，为控制流量，会对请求频率加以控制，
目前的频率限制是以连续30秒内，限制请求次数，具体那些接口有限制以及限制次数如下:

 =====================        =====================
 接口名称                     连续30秒内次数限制
 =====================        =====================
 get_market_snapshot          10
 get_plate_list               10
 get_plate_stock              10
 =====================        =====================

---------------------------------------------------------------------

高频数据接口
------------

为控制定阅产生推送数据流量，股票定阅总量有额度控制，规则如下:

1.使用高频数据接口前，需要订阅（调用subscribe）.订阅有额度限制：

 用户额度 >= 订阅K线股票数 * K线权重 + 订阅逐笔股票数 * 逐笔权重 + 订阅报价股票数 * 报价权重 + 订阅摆盘股票数 * 摆盘权重
 
2.订阅不同的类型，会消耗不同的额度，当总额度超过上限后，目前用户总额度上限为500。

3.订阅至少一分钟才可以反订阅

 =====================    ===============================
 订阅数据                 额度权重（所占订阅单位）
 =====================    ===============================
 K线						2
 分时						2
 逐笔						5（牛熊证为1）
 报价						1
 摆盘						5（牛熊证为1）
 经纪队列					5（牛熊证为1）
 =====================    ===============================




