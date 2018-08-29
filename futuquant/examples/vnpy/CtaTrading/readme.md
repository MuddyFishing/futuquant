
## 文件说明：
+ futu_connect.json： vnpy对接futu api的配置文件，vnpy会优先读取当前目前下的配置文件，也可将该文件copy至 vnpy库下的vnpy/trader/gateway/futuGateway目录
+ CTA_setting.json： vnpy策略配置文件，源于vnpy库下VnTrader/CTA_setting.json, vnpy在逻辑处理上会优先读取当前工作目录下的同名配置文件，
+ runCtaTrading.py: 源于vnpy库下的examples/CtaTrading/runCtaTrading.py, 修改了部分代码， 只加载futu模块
+ strategyKingKeltnerTest.py 源于vnpy库下的vnpy/trader/app/ctaStrategy/strategy/strategyKingKeltner.py
+ runCtaTrading.bat: windows下的脚本执行文件，可双击运行。主要逻辑是设置脚本所在目录为当前工作目录及运行runCtaTrading.py

## 使用说明:
+ futuquant已兼容python2.7, vnpy最低版本要求v1.9, 建议在python2.7下运行该范例
+ 需要用pip 安装的其它库包括 : vnpy, pymongo, future, ta-lib
+ 体验步骤:
	+ 执行 runCtaTrading.bat(windows)或 设置当前目录为工作目录，再执行runCtaTrading.py
 



