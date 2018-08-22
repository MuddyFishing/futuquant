
## 文件说明：
+ run.py: 来源于vnpy库下的examples/vnTrader/run.py, 为方便体验， 去掉了与futu api无关的模块加载 
+ futu_connect.json： vnpy对接futu api的配置文件，vnpy会优先读取当前目前下的配置文件，也可将该文件copy至 vnpy库下的vnpy/trader/gateway/futuGateway目录 
+ run.bat: windows下的脚本执行文件。主要逻辑是设置脚本所在目录为当前工作目录及运行run.py 

## 使用说明:
+ futuquant已兼容python2.7, vnpy最低版本要求v1.9, 建议在python2.7下运行该范例
+ 需要用pip 安装的其它库包括 : vnpy, pymongo, future, ta-lib
+ 体验步骤:
	+ 双击run.bat(windows)或 设置当前目录为工作目录，再执行run.py
	+ 打开界面后， 操作菜单"系统" ->"连接富途证券", 观察命令行窗口输出， 是否正常运行
	+ 默认配置是港股仿真交易环境 ，可放心体验下单操作,  如”合约代码“ 填入 "HK.00700"后敲回车, “成交量” 填入100, 点击”发单“按钮, 观察成交和订单窗口信息展现  
 



