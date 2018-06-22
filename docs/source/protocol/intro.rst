协议接口指南
====
`FutuQuant <https://github.com/FutunnOpen/futuquant/>`_ 开源项目是基于FutuOpenD开放协议实现的Futu API的交易和行情接口，为了实现更高效和灵活的接口，您也可以使用其它语言直接对接原始协议。

--------------

FutuOpenD

	.. _FutuOpenD: ../setup/FutuOpenDGuide.html#id5
	
	
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

 ==============   =============================================================================================================================================================    ==================================================================
 协议ID           Protobuf文件                                                                                                                                                     说明
 ==============   =============================================================================================================================================================    ==================================================================
 1001        	  `InitConnect.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/InitConnect.proto>`_                                                  初始化连接
 1002             `GetGlobalState.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/GetGlobalState.proto>`_                                            获取全局状态 
 1003             `Notify.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Notify.proto>`_                                                            系统通知推送
 1004			  `KeepAlive.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/KeepAlive.proto>`_  	    	                                        保活心跳
 2001             `Trd_GetAccList.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_GetAccList.proto>`_                                            获取业务账户列表
 2005             `Trd_UnlockTrade.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_UnlockTrade.proto>`_                                          解锁或锁定交易
 2008             `Trd_SubAccPush.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_SubAccPush.proto>`_                                            订阅业务账户的交易推送数据
 2101             `Trd_GetFunds.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_GetFunds.proto>`_                                                获取账户资金
 2102             `Trd_GetPositionList.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_GetPositionList.proto>`_                                  获取账户持仓
 2201             `Trd_GetOrderList.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_GetOrderList.proto>`_                                        获取订单列表
 2202             `Trd_PlaceOrder.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_PlaceOrder.proto>`_                                            下单
 2205             `Trd_ModifyOrder.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_ModifyOrder.proto>`_                                          修改订单
 2208             `Trd_UpdateOrder.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_UpdateOrder.proto>`_                                          推送订单状态变动通知
 2211             `Trd_GetOrderFillList.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_GetOrderFillList.proto>`_                                获取成交列表
 2222             `Trd_UpdateOrderFill.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_UpdateOrderFill.proto>`_                                  推送成交通知
 2221             `Trd_GetHistoryOrderList.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_GetHistoryOrderList.proto>`_                          获取历史订单列表
 2222             `Trd_GetHistoryOrderFillList.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Trd_GetHistoryOrderFillList.proto>`_                  获取历史成交列表
 3001             `Qot_Sub.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_Sub.proto>`_                                                          订阅或者反订阅
 3002             `Qot_RegQotPush.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_RegQotPush.proto>`_                                            注册推送
 3003             `Qot_GetSubInfo.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetSubInfo.proto>`_                                            获取订阅信息
 3004             `Qot_GetBasicQot.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetBasicQot.proto>`_                                          获取股票基本行情
 3005             `Qot_UpdateBasicQot.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_UpdateBasicQot.proto>`_                                    推送股票基本行情
 3006             `Qot_GetKL.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetKL.proto>`_                                                      获取K线
 3007             `Qot_UpdateKL.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_UpdateKL.proto>`_                                                推送K线
 3008             `Qot_GetRT.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetRT.proto>`_                                                      获取分时
 3009             `Qot_UpdateRT.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_UpdateRT.proto>`_                                                推送分时
 3010             `Qot_GetTicker.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetTicker.proto>`_                                              获取逐笔
 3011             `Qot_UpdateTicker.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_UpdateTicker.proto>`_                                        推送逐笔
 3012             `Qot_GetOrderBook.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetOrderBook.proto>`_                                        获取买卖盘
 3013             `Qot_UpdateOrderBook.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_UpdateOrderBook.proto>`_                                  推送买卖盘
 3014             `Qot_GetBroker.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetBroker.proto>`_                                              获取经纪队列
 3015             `Qot_UpdateBroker.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_UpdateBroker.proto>`_                                        推送经纪队列
 3100             `Qot_GetHistoryKL.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetHistoryKL.proto>`_                                        获取单只股票一段历史K线
 3101             `Qot_GetHistoryKLPoints.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetHistoryKLPoints.proto>`_                            获取多只股票多点历史K线
 3102             `Qot_GetRehab.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetRehab.proto>`_                                                获取复权信息
 3200             `Qot_GetTradeDate.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetTradeDate.proto>`_                                        获取市场交易日
 3201             `Qot_GetSuspend.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetSuspend.proto>`_                                            获取股票停牌信息（暂时数据不全）
 3202             `Qot_GetStaticInfo.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetStaticInfo.proto>`_                                      获取股票静态信息
 3203             `Qot_GetSecuritySnapshot.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetSecuritySnapshot.proto>`_                          获取股票快照
 3204             `Qot_GetPlateSet.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetPlateSet.proto>`_                                          获取板块集合下的板块
 3205             `Qot_GetPlateSecurity.proto <https://github.com/FutunnOpen/futuquant/blob/master/futuquant/common/pb/Qot_GetPlateSecurity.proto>`_                                获取板块下的股票
 ==============   =============================================================================================================================================================    ==================================================================

 
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

	*  包体格式类型设置参见 FutuOpenD_ 配置说明
	*  枚举值字段定义使用有符号整形，注释指明对应枚举，枚举一般定义于Common.proto，Qot_Common.proto，Trd_Common.proto文件中
	*  原始协议文件格式是以Protobuf格式定义，若需要json格式传输，建议使用protobuf3人接口直接转换成json
	
---------------------------------------------------

加密通信流程
~~~~~~~~~~~~~~~

  * 通过RSA密钥加密1001协议获得随机密钥，后续使用随机密钥进行AES加密通信。

.. image:: ../_static/encrypt.png

.. note::
	* RSA密钥配置参考 `FutuOpenD配置 <https://futunnopen.github.io/futuquant/setup/FutuOpenDGuide.html#id5>`_ rsa_private_key配置项
	
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










		





	
	
	

