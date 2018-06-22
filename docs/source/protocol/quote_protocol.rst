行情协议
==========
	这里对FutuOpenD开放的行情协议接口作出归档说明。

.. note::

    *   为避免增删导致的版本兼容问题，所有enum枚举类型只用于值的定义，在protobuf结构体中声明类型时使用int32类型
    *   所有类型定义使用protobuf格式声明，不同语言对接时请自行通过相关工具转换成对应的头文件
    *   *.proto表示协议文件名, `FutuQuant/common/pb <https://github.com/FutunnOpen/futuquant/tree/master/futuquant/common/pb>`_ 开源项目中可获取所有文件

--------------

Common.proto
-------------

RetType - 协议返回值
~~~~~~~~~~~~~~~~~~~~~~~~

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


