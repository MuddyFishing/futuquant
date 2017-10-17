# FutuQuant - 富途量化投资平台 (Futu Quant Trading API)

### 简介

[​**FutuQuant**](https://futunnopen.github.io/futuquant/intro/intro.html)开源项目可以满足使用[**富途牛牛**](http://www.futunn.com/)软件进行量化投资的需求, 提供包括Python接口、Json接口的行情及交易的API。 

- [官方在线文档](https://futunnopen.github.io/futuquant/intro/intro.html)

-------------------

### 安装
```
pip install futuquant
```

###### 注: 本API同时兼容Python2和Python3, 推荐安装anaconda环境，方便快捷。

---

### 快速上手
```
# 导入futuquant api
import futuquant as ft

# 实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host="127.0.0.1", port=11111)

# 上下文控制
quote_ctx.start()              # 开启异步数据接收
quote_ctx.stop()               # 停止异步数据接收
quote_ctx.set_handler(handler) # 设置用于异步处理数据的回调对象

# 低频数据接口 
quote_ctx.get_trading_days(market, start_date=None, end_date=None)    # 获取交易日
quote_ctx.get_stock_basicinfo(market, stock_type='STOCK')             # 获取股票信息
quote_ctx.get_history_kline(code, start=None, end=None, ktype='K_DAY', autype='qfq')  # 获取历史K线
quote_ctx.get_autype_list(code_list)                                  # 获取复权因子
quote_ctx.get_market_snapshot(code_list)                              # 获取市场快照
quote_ctx.get_plate_list(market, plate_class)                         # 获取板块集合下的子板块列表
quote_ctx.get_plate_stock(market, stock_code)                         # 获取板块下的股票列表

# 高频数据接口
quote_ctx.get_stock_quote(code_list) # 获取报价
quote_ctx.get_rt_ticker(code, num)   # 获取逐笔
quote_ctx.get_cur_kline(code, num, ktype=' K_DAY', autype='qfq') # 获取当前K线
quote_ctx.get_order_book(code)       # 获取摆盘
quote_ctx.get_rt_data(code)          # 获取分时数据
quote_ctx.get_broker_queue(code)     # 获取经纪队列


# 实例化港股交易上下文对象
trade_hk_ctx = ft.OpenHKTradeContext(host="127.0.0.1", port=11111)

# 实例化美股交易上下文对象
trade_us_ctx = ft.OpenUSTradeContext(host="127.0.0.1", port=11111)

# 交易接口列表
ret_code, ret_data = trade_hk_ctx.unlock_trade(password='123456')                # 解锁接口
ret_code, ret_data = trade_hk_ctx.place_order(price, qty, strcode, orderside, ordertype=0, envtype=0) # 下单接口
ret_code, ret_data = trade_hk_ctx.set_order_status(status, orderid=0, envtype=0) # 设置订单状态
ret_code, ret_data = trade_hk_ctx.change_order(price, qty, orderid=0, envtype=0) # 修改订单
ret_code, ret_data = trade_hk_ctx.accinfo_query(envtype=0)                       # 查询账户信息
ret_code, ret_data = trade_hk_ctx.order_list_query(statusfilter="", envtype=0)   # 查询订单列表
ret_code, ret_data = trade_hk_ctx.position_list_query(envtype=0)                 # 查询持仓列表
ret_code, ret_data = trade_hk_ctx.deal_list_query(envtype=0)                     # 查询成交列表
```

---

### 示例策略

- 示例策略文件位于目录: (futuquant包安装目录)/futuquant/examples 下，用户可参考实例策略来学习API的使用。
- 另外，可参考API相对应的[视频课程](https://live.futunn.com/course/1056)学习API的使用。

---

### 组织结构

![image](https://github.com/FutunnOpen/futuquant/raw/master/docs/source/_static/Structure.png)

​	最新版本在master分支。之前各版本在其他分支上。

---

### API与富途牛牛客户端架构

![image](https://github.com/FutunnOpen/futuquant/raw/master/docs/source/_static/API.png)

***

### 使用须知

- 限定使用有API后缀的安装包。不要去掉勾选“安装量化交易插件API”选项。
- 无需拷贝对应的dll插件。
- 安装成功后直接使用接口进行行情获取或者交易操作。

---

### 历史数据及除权除息下载问题
###### [历史K线下载指引](https://github.com/FutunnOpen/futuquant/blob/master/docs/document/Hist_KLine_Download_Intro.md)

- 在富途牛牛安装目录的plugin文件夹内有历史数据下载配置文件(ftplugin.ini)，请先详细阅读再进行操作。
- 如果不想下载新数据、可以将开始时间和暂停下载时间设置为相同时间。
- 如果选择下载的数据越大，下载所需时间越长。如果中途退出，下次开启时将重新下载。请勿在下载过程中关闭牛牛客户端。

***

### 客户端下载及交流方式

* 富途开放API群(108534288)    群文件 >富途牛牛客户端(API接口专用版本)

  ![image](https://github.com/FutunnOpen/futuquant/raw/master/docs/source/_static/Download.png)

* <https://github.com/FutunnOpen/futuquant/issues>


***

### 使用说明

* 有任何问题可以到 issues  处提出，我们会及时进行解答。
* 使用新版本时请先仔细阅读接口文档，大部分问题都可以在接口文档中找到你想要的答案。
* 欢迎大家提出建议、也可以提出各种需求，我们一定会尽量满足大家的需求。

---
