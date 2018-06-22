协议接口指南
====
`FutuQuant <https://github.com/FutunnOpen/futuquant/>`_ 开源项目是基于FutuOpenD开放协议实现的Futu API的交易和行情接口，为了实现更高效和灵活的接口，您也可以使用其它语言直接对接原始协议。

--------------

  .. _InitConnect.proto: base_define.html#id2
  .. _GetGlobalState.proto:  base_define.html#id3
  .. _Notify.proto:  base_define.html#id4
  .. _KeepAlive.proto:  base_define.html#id5
  
  .. _Trd_GetAccList.proto:  trade_protocol.html#trd-getacclist-proto-2001
  .. _Trd_UnlockTrade.proto:  trade_protocol.html#trd-unlocktrade-proto-2005
  .. _Trd_SubAccPush.proto:  trade_protocol.html#trd-subaccpush-proto-2008
  .. _Trd_GetFunds.proto:  trade_protocol.html#trd-getfunds-proto-2101
  .. _Trd_GetPositionList.proto:  trade_protocol.html#trd-getpositionlist-proto-2102
  
  .. _Trd_GetOrderList.proto:  trade_protocol.html#trd-getorderlist-proto-2201
  .. _Trd_PlaceOrder.proto:  trade_protocol.html#trd-placeorder-proto-2202
  .. _Trd_ModifyOrder.proto:  trade_protocol.html#trd-modifyorder-proto-2205
  .. _Trd_UpdateOrder.proto:  trade_protocol.html#trd-updateorder-proto-2208
  
  .. _Trd_GetOrderFillList.proto:  trade_protocol.html#trd-getorderfilllist-proto-2211
  .. _Trd_UpdateOrderFill.proto:  trade_protocol.html#trd-updateorderfill-proto-2218
  
  .. _Trd_GetHistoryOrderList.proto:  trade_protocol.html#trd-gethistoryorderlist-proto-2221
  .. _Trd_GetHistoryOrderFillList.proto:  trade_protocol.html#trd-gethistoryorderfilllist-proto-2221
  
  .. _Qot_Sub.proto:  quote_protocol.html#id4
  .. _Qot_RegQotPush.proto:  quote_protocol.html#id5
  .. _Qot_GetSubInfo.proto:  quote_protocol.html#id6
  .. _Qot_GetBasicQot.proto:  quote_protocol.html#id7
  .. _Qot_UpdateBasicQot.proto:  quote_protocol.html#id8
  
  .. _Qot_GetKL.proto:  quote_protocol.html#qot-getkl-proto-k
  .. _Qot_UpdateKL.proto:  quote_protocol.html#qot-updatekl-proto-k
  .. _Qot_GetRT.proto:  quote_protocol.html#id9
  .. _Qot_UpdateRT.proto:  quote_protocol.html#id10
  .. _Qot_GetTicker.proto:  quote_protocol.html#id11
  
  .. _Qot_UpdateTicker.proto:  quote_protocol.html#id12
  .. _Qot_GetOrderBook.proto:  quote_protocol.html#id13
  .. _Qot_UpdateOrderBook.proto:  quote_protocol.html#id14
  .. _Qot_GetBroker.proto:  quote_protocol.html#id15
  .. _Qot_UpdateBroker.proto:  quote_protocol.html#id16
  
  
  .. _Qot_GetHistoryKL.proto:  quote_protocol.html#qot-gethistorykl-proto-k
  .. _Qot_GetHistoryKLPoints.proto:  quote_protocol.html#qot-gethistoryklpoints-proto-k
  .. _Qot_GetRehab.proto:  quote_protocol.html#id19
  .. _Qot_GetTradeDate.proto:  quote_protocol.html#id20
  .. _Qot_GetSuspend.proto:  quote_protocol.html#id20
  
  .. _Qot_GetStaticInfo.proto:  quote_protocol.html#id21
  .. _Qot_GetSecuritySnapshot.proto:  quote_protocol.html#id22
  .. _Qot_GetPlateSet.proto:  quote_protocol.html#id23
  .. _Qot_GetPlateSecurity.proto:  quote_protocol.html#id24
  
	
特点
-------

+ 基于TCP传输协议实现，稳定高效。
+ 支持protobuf/json两种协议格式， 灵活接入。
+ 协议设计支持加密、数据校验及回放功击保护，安全可靠。


变更记录
----------

 ==============   ===========   ===================================================================
 时间             修改文件      说明
 ==============   ===========   ===================================================================
 2018/6/20        无            初稿
 
 ==============   ===========   ===================================================================
 
---------------------------------------------------
 
协议清单
----------

 ==============   ==================================     ==================================================================
 协议ID           Protobuf文件                           说明
 ==============   ==================================     ==================================================================
 1001        	  InitConnect.proto_                      初始化连接
 1002             GetGlobalState.proto_                   获取全局状态 
 1003             Notify.proto_                           系统通知推送
 1004             KeepAlive.proto_                        保活心跳
 2001             Trd_GetAccList.proto_                   获取业务账户列表
 2005             Trd_UnlockTrade.proto_                  解锁或锁定交易
 2008             Trd_SubAccPush.proto_                   订阅业务账户的交易推送数据
 2101             Trd_GetFunds.proto_                     获取账户资金
 2102             Trd_GetPositionList.proto_              获取账户持仓
 2201             Trd_GetOrderList.proto_                 获取订单列表
 2202             Trd_PlaceOrder.proto_                   下单
 2205             Trd_ModifyOrder.proto_                  修改订单
 2208             Trd_UpdateOrder.proto_                  推送订单状态变动通知
 2211             Trd_GetOrderFillList.proto_             获取成交列表
 2218             Trd_UpdateOrderFill.proto_              推送成交通知
 2221             Trd_GetHistoryOrderList.proto_          获取历史订单列表
 2222             Trd_GetHistoryOrderFillList.proto_      获取历史成交列表
 3001             Qot_Sub.proto_                          订阅或者反订阅
 3002             Qot_RegQotPush.proto_                   注册推送
 3003             Qot_GetSubInfo.proto_                   获取订阅信息
 3004             Qot_GetBasicQot.proto_                  获取股票基本行情
 3005             Qot_UpdateBasicQot.proto_               推送股票基本行情
 3006             Qot_GetKL.proto_                        获取K线
 3007             Qot_UpdateKL.proto_                     推送K线
 3008             Qot_GetRT.proto_                        获取分时
 3009             Qot_UpdateRT.proto_                     推送分时
 3010             Qot_GetTicker.proto_                    获取逐笔
 3011             Qot_UpdateTicker.proto_                 推送逐笔
 3012             Qot_GetOrderBook.proto_                 获取买卖盘
 3013             Qot_UpdateOrderBook.proto_              推送买卖盘
 3014             Qot_GetBroker.proto_                    获取经纪队列
 3015             Qot_UpdateBroker.proto_                 推送经纪队列
 3100             Qot_GetHistoryKL.proto_                 获取单只股票一段历史K线
 3101             Qot_GetHistoryKLPoints.proto_           获取多只股票多点历史K线
 3102             Qot_GetRehab.proto_                     获取复权信息
 3200             Qot_GetTradeDate.proto_                 获取市场交易日
 3201             Qot_GetSuspend.proto_                   获取股票停牌信息（暂时数据不全）
 3202             Qot_GetStaticInfo.proto_                获取股票静态信息
 3203             Qot_GetSecuritySnapshot.proto_          获取股票快照
 3204             Qot_GetPlateSet.proto_                  获取板块集合下的板块
 3205             Qot_GetPlateSecurity.proto_             获取板块下的股票 
 ==============   ==================================     ==================================================================


.. note::

    * 所有 Protobuf 文件可从 `FutuQuant <https://github.com/FutunnOpen/futuquant/tree/master/futuquant/common/pb>`_ Python开源项目下获取

---------------------------------------------------

协议请求流程 
-------------
	* 建立连接
	* 初始化连接
	* 请求数据或接收推送数据
	
.. image:: ../_static/proto.png

--------------

协议设计
---------
  协议数据包括协议头以及协议体，协议头固定字段，协议体根据具体协议决定。
  
协议头结构
~~~~~~~~~~~~~~~

.. code-block:: bash
    
	struct APIProtoHeader
	{
	    u8_t szHeaderFlag[2];
	    u32_t nProtoID;
	    u8_t nProtoFmtType;
	    u8_t nProtoVer;
	    u32_t nSerialNo;
	    u32_t nBodyLen;
	    u8_t arrBodySHA1[20];
	    u8_t arrReserved[8];
	};


==============   ==================================================================
字段             说明
==============   ==================================================================
szHeaderFlag     包头起始标志，固定为“FT”
nProtoID         协议ID
nProtoFmtType    协议格式类型，0为Protobuf格式，1为Json格式
nProtoVer        协议版本，用于迭代兼容
nSerialNo        包序列号，用于对应请求包和回包
nBodyLen         包体长度
arrBodySHA1      包体原数据(解密后)的SHA1哈希值
arrReserved      保留8字节扩展
==============   ==================================================================

.. note::

    *   u8_t表示8位无符号整数，u32_t表示32位无符号整数
    *   FutuOpenD内部处理使用Protobuf，因此协议格式建议使用Protobuf，减少Json转换开销
    *   nProtoFmtType字段指定了包体的数据类型，回包会回对应类型的数据；推送协议数据类型由FutuOpenD配置文件指定

---------------------------------------------------
	
协议体结构
~~~~~~~~~~~

**Protobuf协议请求包体结构**

.. code-block:: bash
    
	message C2S
	{
	    required int64 req = 1; 
	}

	message Request
	{
	    required C2S c2s = 1;
	}

**Protobuf协议回应包体结构**

.. code-block:: bash
	
	message S2C
	{
	    required int64 data = 1; 
	}

	message Response
	{
	    required int32 retType = 1 [default = -400]; //RetType,返回结果
	    optional string retMsg = 2;
	    optional int32 errCode = 3;
	    optional S2C s2c = 4;
	}

**Json协议请求包体结构**

.. code-block:: bash
	
	{
	    "Request":
	    {
	        "c2s": 
	        {
	            "req": 0
	        }
	    }
	}

**Json协议回应包体结构**

.. code-block:: bash
	
	{
	    "Response":
	    {
	        "retType" : 0
	        "retMsg" : ""
	        "errCode" : 0
	        "s2c": 
	        {
	            "data": 0
	        }
	    }
	}

---------

==============   ==================================================================
字段             说明
==============   ==================================================================
Request          请求包体结构
c2s              请求参数结构
req              请求参数，实际根据协议定义
Response         回应包体结构
retType          请求结果
retMsg           若请求失败，说明失败原因
errCode          若请求失败对应错误码
s2c              回应数据结构，部分协议不返回数据则无该字段
data             回应数据，实际根据协议定义
==============   ==================================================================
 
.. note::

	*  包体格式类型设置参见 `FutuOpenD配置 <https://futunnopen.github.io/futuquant/setup/FutuOpenDGuide.html#id5>`_ 约定的 “push_proto_type“ 配置项
	*  枚举值字段定义使用有符号整形，注释指明对应枚举，枚举一般定义于Common.proto，Qot_Common.proto，Trd_Common.proto文件中
	*  原始协议文件格式是以Protobuf格式定义，若需要json格式传输，建议使用protobuf3人接口直接转换成json
	
---------------------------------------------------

加密通信流程
~~~~~~~~~~~~~~~

  * 通过RSA密钥加密1001协议获得随机密钥，后续使用随机密钥进行AES加密通信。

.. image:: ../_static/encrypt.png

.. note::
	* RSA密钥配置参考 `FutuOpenD配置 <https://futunnopen.github.io/futuquant/setup/FutuOpenDGuide.html#id5>`_ 约定的 “rsa_private_key“ 配置项
	
---------------------------------------------------

AES加解密
~~~~~~~~~~~~~~~~~~~

**发送数据加密**

  * AES加密要求源数据长度必须是16的整数倍,  故需补‘\0'对齐后再加密，记录mod_len为源数据长度与16取模值

  * 因加密前有可能对源数据作修改， 故需在加密后的数据尾再增加一个16字节的填充数据块，其最后一个字节赋值mod_len, 其余字节赋值'\0'， 将加密数据和额外的填充数据块拼接作为最终要发送协议的body数据

  * 注意mod_len为小端字节序

**接收数据解密**

  * 协议body数据, 先将最后一个字节取出，记为mod_len， 然后将body截掉尾部16字节填充数据块后再解密（与加密填充额外数据块逻辑对应）

  * mod_len 为0时，上述解密后的数据即为协议返回的body数据, 否则需截掉尾部(16 - mod_len)长度的用于填充对齐的数据

  .. image:: ../_static/AES.png
  
---------------------------------------------------










		





	
	
	

