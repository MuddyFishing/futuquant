协议接口指南
====
`FutuQuant <https://github.com/FutunnOpen/futuquant/>`_ 开源项目是基于FutuOpenD开放协议实现的Futu API的交易和行情接口，为了实现更高效和灵活的接口，您也可以使用其它语言直接对接原始协议。

--------------


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

 ==============   ==================================    ==================================================================
 协议ID           Protobuf文件                          说明
 ==============   ==================================    ==================================================================
 1001        	  InitConnect.proto                     初始化连接
 1002             GetGlobalState.proto                  获取全局状态 
 1003             Notify.proto                          系统通知推送
 1004			  KeepAlive.proto		    	        保活心跳
 2001             Trd_GetAccList.proto                  获取业务账户列表
 2005             Trd_UnlockTrade.proto                 解锁或锁定交易
 2008             Trd_SubAccPush.proto                  订阅业务账户的交易推送数据
 2101             Trd_GetFunds.proto                    获取账户资金
 2102             Trd_GetPositionList.proto             获取账户持仓
 2201             Trd_GetOrderList.proto                获取订单列表
 2202             Trd_PlaceOrder.proto                  下单
 2205             Trd_ModifyOrder.proto                 修改订单
 2208             Trd_UpdateOrder.proto                 推送订单状态变动通知
 2211             Trd_GetOrderFillList.proto            获取成交列表
 2222             Trd_UpdateOrderFill.proto             推送成交通知
 2221             Trd_GetHistoryOrderList.proto         获取历史订单列表
 2222             Trd_GetHistoryOrderFillList.proto     获取历史成交列表
 3001             Qot_Sub.proto                         订阅或者反订阅
 3002             Qot_RegQotPush.proto                  注册推送
 3003             Qot_GetSubInfo.proto                  获取订阅信息
 3004             Qot_GetBasicQot.proto                 获取股票基本行情
 3005             Qot_UpdateBasicQot.proto              推送股票基本行情
 3006             Qot_GetKL.proto                       获取K线
 3007             Qot_UpdateKL.proto                    推送K线
 3008             Qot_GetRT.proto                       获取分时
 3009             Qot_UpdateRT.proto                    推送分时
 3010             Qot_GetTicker.proto                   获取逐笔
 3011             Qot_UpdateTicker.proto                推送逐笔
 3012             Qot_GetOrderBook.proto                获取买卖盘
 3013             Qot_UpdateOrderBook.proto             推送买卖盘
 3014             Qot_GetBroker.proto                   获取经纪队列
 3015             Qot_UpdateBroker.proto                推送经纪队列
 3100             Qot_GetHistoryKL.proto                获取单只股票一段历史K线
 3101             Qot_GetHistoryKLPoints.proto          获取多只股票多点历史K线
 3102             Qot_GetRehab.proto                    获取复权信息
 3200             Qot_GetTradeDate.proto                获取市场交易日
 3201             Qot_GetSuspend.proto                  获取股票停牌信息（暂时数据不全）
 3202             Qot_GetStaticInfo.proto               获取股票静态信息
 3203             Qot_GetSecuritySnapshot.proto         获取股票快照
 3204             Qot_GetPlateSet.proto                 获取板块集合下的板块
 3205             Qot_GetPlateSecurity.proto            获取板块下的股票
 ==============   ==================================    ==================================================================
 
.. note::

    * 所有 Protobuf 文件可从 `FutuQuant <https://github.com/FutunnOpen/futuquant/tree/master/futuquant/common/pb>`_ Python开源项目下获取

---------------------------------------------------

协议请求流程 
-------------

图表： 建立连接 -》 初始化连接 -》 请求操作 -》 返回   +  数据推送 


--------------

协议设计
---------
  协议数据包括协议头以及协议体，协议头固定字段，协议体根据具体协议决定。
  
协议头结构
~~~~~
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

---------

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

Protobuf协议请求包体结构

.. code-block:: bash
    
	message C2S
	{
	    required int64 req = 1; 
	}

	message Request
	{
	    required C2S c2s = 1;
	}

Protobuf协议回应包体结构

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

Json协议请求包体结构

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

Json协议回应包体结构

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

    *  枚举值字段定义使用有符号整形，注释指明对应枚举，枚举一般定义于Common.proto，Qot_Common.proto，Trd_Common.proto文件中
	
---------------------------------------------------
	
RSA私钥文件
~~~~~~~~~~~~~~

.. code-block:: bash

		-----BEGIN RSA PRIVATE KEY-----
	MIICXAIBAAKBgQCx3W78hx5dQxg47hGMEj02JAJYP+HdKGWD8QilzeK4eL6QJ9QP
	+uVYGA5Jp0Ed2AaV+zQrT/BCe6z5j/Qd5B0eY2cFlgk+/hbAt7A4wcSAbby8nONw
	0fZTglU78FhLUih84Int5HO0Fr3WLUDvpE+TgS3l/2u5ym6H6fvsdrdNCwIDAQAB
	AoGAHep/s2vKmKcjWNf6DZQ3xXZzCoLcK4WS5YlSCglCHAL7EmYQjguGLbYGGS9P
	jYR7Pxi8YpiUcao5otQqnCh1GRFouU397D3h+bf/bQXINZcv3sxKFrXm9MNVaBJD
	W4BcC3HGfnlaIVTKU+qGkeA1BydP5AQyxsGOq00IUeGK4uECQQD/5xHLDwhwYFyc
	MK4xMnlrvne8TSlPBciWfrxQ7V/X0eP/HQ20VkVxc0tFD91aLrCap6OYcNV9jwJN
	wTQLt5wbAkEAse7C75LKW0+cMcROvAR3qLV2LbGjLW+cH6WmEP9CEGxi0aJg4Gs3
	oSRYfaC/RLI87sSb0DC5+mTswXduLGpB0QJAJk0ec6cHW1KA6fu7Rq/ITqEOaMef
	xC0YbbYAV5h/vNy0ZE2j7HbxI97eyDJsrf/I/QzURo+01HsgHCUrtglAOwJBAKiW
	cA7sh1zS5kxlErCkjvfDz1BmIhT3zfZSTjGGmYLUHyE/eAjKra+5rzqA5xjgxEj6
	8iLlOCFeJND+Jt5gYzECQH+HtFilF1SxGS4AHrJomHaMhk/IazjtUnLuFM/DuZ/h
	sxTqXpBBCtTqcAotMlx4ZJQYL3f2PmI2Q/o0NUMt40w=
	-----END RSA PRIVATE KEY-----
	
.. note::

  *  RSA 密钥的填充方式为 PKCS1, 位数1024
  *  密钥文件可通过第三方web平台自动生成， 请在baidu或google上搜索"RSA 在线生成"
	
---------------------------------------------------
	
加密操作流程
~~~~~~~~~~~~~~~

.. image:: ../_static/encrypt.png
				
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

---------------------------------------------------










		





	
	
	

