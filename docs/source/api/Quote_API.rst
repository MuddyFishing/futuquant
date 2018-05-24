========
行情API
========

----------------------------

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

-------------------------------------------

StockQuoteHandlerBase - 实时报价回调处理类
-------------------------------------------

-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)


 行情上下文对象订阅实时报价，继承对象，在收到实时报价推送后会回调到该函数，注意该回调是在独立子线程中

 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :return: (ret_code, content) 
 
  ret_code 等于RET_OK时， content为Pandas.DataFrame数据, 否则为错误原因字符串, 数据列格式如下
 
  ==============   ===========   ==============================================================================
   参数              类型                        说明
  ==============   ===========   ==============================================================================
  open             float         开盘价
  close            float         收盘价
  high             float         最高价
  ==============   ===========   ==============================================================================

 :example:

 .. code:: python

  from futuquant import *
  quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
  quote_ctx.close()
	
	
----------------------------

OrderBookHandlerBase - 实时摆盘回调处理类
-------------------------------------------

-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

..  py:function:: on_recv_rsp(self, rsp_pb)

 行情上下文对象订阅实时报价，继承对象，在收到实时报价推送后会回调到该函数，注意该回调是在独立子线程中

 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :return: (ret_code, content) 
 
  ret_code 等于RET_OK时， content为Pandas.DataFrame数据, 否则为错误原因字符串, 数据列格式如下
 
  ==============   ===========   ==============================================================================
   参数              类型                        说明
  ==============   ===========   ==============================================================================
  open             float         开盘价
  close            float         收盘价
  high             float         最高价
  ==============   ===========   ==============================================================================

 :example:

 .. code:: python

  from futuquant import *
  quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
  quote_ctx.close()
		
----------------------------

OpenQuoteContext - 上下文对象类
-------------------------------------------

----------------------------

get_stock_basicinfo - 获取股票基列表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_stock_basicinfo(self, rsp_pb)

 行情上下文对象订阅实时报价，继承对象，在收到实时报价推送后会回调到该函数，注意该回调是在独立子线程中

 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :param rsp_pb: 数据对象 common.pb.Qot_UpdateBasicQot_pb2中的Response
 :return: (ret_code, content) 
 
  ret_code 等于RET_OK时， content为Pandas.DataFrame数据, 否则为错误原因字符串, 数据列格式如下
 
  ==============   ===========   ==============================================================================
   参数              类型                        说明
  ==============   ===========   ==============================================================================
  open             float         开盘价
  close            float         收盘价
  high             float         最高价
  ==============   ===========   ==============================================================================

 :example:

 .. code:: python

  from futuquant import *
  quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
  quote_ctx.close()
	
---------------------------------------------------------------------
	
接口限频
========

---------------------------------------------------------------------

低频数据接口
------------

低频数据接口是指不需要定阅就可以请求数据的接口， api的请求到达网关客户端后， 会转发请求到futu后台服务器，为控制流量，会对请求频率加以控制，
目前的控制频率为每30秒最多请求10次，相关接口如下:

+ **get_market_snapshot**

+ **get_market_snapshot**


---------------------------------------------------------------------

高频数据接口
------------

高频数据接口是定阅股票后，应用端可以无时限的查询最新数据， api请求到达网关客户端后，会将已经缓存的最新数据返回给应用层，相关接口下：

+ **get_stock_quote**

+ **get_cur_kline**


为控制定阅产生推送数据流量，股票定阅总量有额度控制，规则如下（待补充） 。。。。



