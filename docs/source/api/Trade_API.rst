========
交易API
========

----------------------------

一分钟上手
============

如下范例，创建api交易对象，先调用unlock_trade对交易解锁，然后调用place_order下单，以700.0价格，买100股腾讯00700,最后关闭对象

.. code:: python

	from futuquant import *
	pwd_unlock = '123456'
	trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
	print(trd_ctx.unlock_trade(pwd_unlock))
	print(place_order(price=700.0, qyt=100, code="HK.00700", trd_side=TrdSide.SELL))
	quote_ctx.close()
	
----------------------------


接口类对象
==========

-------------------------------------------

TradeOrderHandlerBase - 订单状态变化回调处理基类
------------------------------------------------

-------------------------------------------

on_recv_rsp
~~~~~~~~~~~

on_recv_rsp(self, rsp_pb) - 订单状态变化回调处理函数

**描述:**：

这里增加文字

**参数:**


**返回值**:

(ret_code, content)

**示例代码:**

.. code:: python

  from futuquant import *
  trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
  ....
	trd_ctx.close()
	
----------------------------

TradeDealHandlerBase - 订单成交回调处理基类
-------------------------------------------

-------------------------------------------

on_recv_rsp
~~~~~~~~~~~~~~~

on_recv_rsp(self, rsp_pb) - 订单成交回调处理函数

**描述:**：

这里增加文字

**参数:**


**返回值**:

(ret_code, content)

**示例代码:**

.. code:: python
  
  from futuquant import *
  trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
  ....
	trd_ctx.close()
	
----------------------------

OpenHKTradeContext、OpenUSTradeContext - 交易请求对象类
-----------------------------------------------------------

get_acc_list - 获取交易业务账户列表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: get_acc_list(self)

 获取交易业务账户列表。要调用交易接口前，必须先获取此列表，后续交易接口根据不同市场传入不同的交易业务账户。
		
 :return(ret_code, ret_data): ret_code为RET_OK时，ret_data为DataFrame数据，否则为错误原因字符串，DataFrame数据如下：
 
 ==============   ===========   ===================================================================
 参数             类型          说明
 ==============   ===========   ===================================================================
 acc_id           int           交易业务账户
 trd_env          str           交易环境，TrdEnv.REAL(真实环境)或TrdEnv.SIMULATE(仿真环境)
 ==============   ===========   ===================================================================

 :example:
 
 .. code:: python
 
  from futuquant import *
  get_acc_list
	
----------------------------

unlock_trade - 解锁交易
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: unlock_trade(self, password, password_md5=None, is_unlock=True)

 解锁交易。要调用交易接口前，必须先拉业务账户列表，然后再解锁交易，才有权限调用交易接口。

 :param password: str，交易密码，如果password_md5不为空就使用传入的password_md5解锁，否则使用password转MD5得到password_md5再解锁
 :param password_md5: str，交易密码的MD5转16进制字符串(全小写)，解锁交易必须要填密码，锁定交易忽略
 :param is_unlock: bool，解锁或锁定，True解锁，False锁定
 :return(ret_code, ret_data): ret_code为RET_OK时，ret_data为None，否则为错误原因字符串

 :example:
 
 .. code:: python
 
  from futuquant import *
  unlock_trade
 
----------------------------
 
accinfo_query - 获取账户资金数据
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  py:function:: accinfo_query(self, trd_env=TrdEnv.REAL, acc_id=0)

 获取账户资金数据。获取账户的资产净值、证券市值、现金、购买力等资金数据。

 :param trd_env: str，交易环境，TrdEnv.REAL(真实环境)或TrdEnv.SIMULATE(仿真环境)
 :param acc_id: int，交易业务账户
 :return(ret_code, ret_data): ret_code为RET_OK时，ret_data为DataFrame数据，否则为错误原因字符串，DataFrame数据如下：

 =====================        ===========   ===================================================================
 参数                         类型          说明
 =====================        ===========   ===================================================================
 power                        float         购买力，即可使用用于买入的资金
 total_assets                 float         资产净值
 cash                         float         现金
 market_val                   float         证券市值
 frozen_cash                  float         冻结金额
 avl_withdrawal_cash          float         可提金额
 =====================        ===========   ===================================================================
 
 :example:
 
 .. code:: python
 
  from futuquant import *
  accinfo_query

----------------------------

position_list_query - 获取账户持仓列表
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  position_list_query(self, code='', pl_ratio_min=None, pl_ratio_max=None, trd_env=TrdEnv.REAL, acc_id=0)

 获取账户持仓列表。获取账户的证券持仓列表。

 :param code: str，代码过滤，只返回包含这些代码的数据，没传不过滤
 :param pl_ratio_min: float，过滤盈亏比例下限，高于此比例的会返回，如0.1，返回盈亏比例大于10%的持仓
 :param pl_ratio_max: float，过滤盈亏比例上限，低于此比例的会返回，如0.2，返回盈亏比例小于20%的持仓
 :param trd_env: str，交易环境，TrdEnv.REAL(真实环境)或TrdEnv.SIMULATE(仿真环境)
 :param acc_id: int，交易业务账户
 :return(ret_code, ret_data): ret_code为RET_OK时，ret_data为DataFrame数据，否则为错误原因字符串，DataFrame数据如下：

 =====================        ===========   ===================================================================
 参数                         类型          说明
 =====================        ===========   ===================================================================
 position_side                str           持仓方向，PositionSide.LONG(多仓)或PositionSide.SHORT(空仓)
 code                         str           代码
 stock_name                   str           名称
 qty                          float         持有数量，2位精度，期权单位是"张"，下同
 can_sell_qty                 float         可卖数量
 nominal_price                float         市价，3位精度(A股2位)
 cost_price                   float        	成本价，无精度限制
 cost_price_valid             bool          成本价是否有效，True有效，False无效
 market_val                   float         市值，3位精度(A股2位)
 pl_ratio                     float         盈亏比例，无精度限制
 pl_ratio_valid               bool          盈亏比例是否有效，True有效，False无效
 pl_val                       float         盈亏金额，3位精度(A股2位)
 pl_val_valid                 bool          盈亏金额是否有效，True有效，False无效
 today_pl_val                 float         今日盈亏金额，3位精度(A股2位)，下同
 today_buy_qty                float         今日买入总量
 today_buy_val                float         今日买入总额
 today_sell_qty               float         今日卖出总量
 today_sell_val               float         今日卖出总额
 =====================        ===========   ===================================================================
 
 :example:
 
 .. code:: python
 
  from futuquant import *
  position_list_query

----------------------------
  
---------------------------------------------------------------------
	
接口限频
========

---------------------------------------------------------------------

交易相关请求到达网关客户端后， 会转发请求到futu后台服务器，为控制流量，会对请求频率加以控制，
目前的控制频率为每30秒最多请求10次，相关接口如下:


+ **history_order_list_query**


---------------------------------------------------------------------






