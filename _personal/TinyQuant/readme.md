# TinyQuant
#### 项目简介：
+ 基于futu api接口，使用python封装的一个轻量级的实盘量化交易框架
+ 框架接口借鉴了业界常见形式， 力求已有策略代码能更简单的迁移
+ 目前项目还在内测阶段，建议先做港股模拟实盘，如有问题，请在api QQ群:108534288 或git issue上反馈

#### 适用人群:
+ 有意向做中低频的港美股量化交易
+ 已有很好的回测策略，需要实盘运行
+ 对futu api有一定的了解，但是没时间封装新框架或对接已有框架
+ 有基础的python开发能力, 能够读懂范例代码逻辑

#### 运行须知:
+ 需要先安装vnpy / ta-lib
+ 该框架二次封装了futu api 常用的行情交易接口，有关futu api的使用请参见 https://futunnopen.github.io/futuquant/intro/intro.html
+ 支持港/美股实盘策略运行，港股可以下模拟单
+ 不支持数据回测
+ 策略实现请参考 TinyStrateSample.py / TinyStrateSouthETF.py
+ 启动策略参考 Run_TinyStrateSample.py / Run_TinyStrateSouthETF.py
