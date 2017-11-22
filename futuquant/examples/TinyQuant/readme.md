# TinyQuant
#### 项目简介：
+ 基于futu api接口， 使用python封装的一个轻量级的实盘量化交易框架
+ 框架接口参考了行业的常见接口设计模式， 力求代码更方便的迁移原有策略
+ 目前项目还在内测阶段，建议先做港股模拟实盘，如有问题，请在api QQ群 108534288 或 git issue上反馈

#### 适用人群:
+ 有意向做中低频的港美股量化交易
+ 已有很好的回测策略，需要实盘运行
+ 对futu api有一定的了解， 但是没时间封装新框架或对接已有框架
+ 有基础的python开发能力, 能够读懂TinyStrateSample接口逻辑

#### 运行须知:
+ 需要先安装vnpy / ta-lib, 暂时仅能运行在python2.7环境,
+ TinyQuantFrame封装了futu api 的调用，有关futu api的使用请参见 https://futunnopen.github.io/futuquant/intro/intro.html
+ 支持港/美股实盘策略运行，港股可以下模拟单, 不支持数据回测
+ 策略实现参考 TinyStrateSample.py
+ 启动策略运行参见 Run_TinyStrateSample.py
