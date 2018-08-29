
## 文件说明：
+ runBacktesting.py: 源于vnpy库下的examples/CtaBacktesting/runBacktesting.py, 修改了股票code及时间等基本参数
+ strategyKingKeltnerTest.py 源于vnpy库下的vnpy/trader/app/ctaStrategy/strategy/strategyKingKeltner.py
+ runBacktesting.bat: windows下的脚本执行文件，可双击运行。主要逻辑是设置脚本所在目录为当前工作目录及运行runBacktesting.py 
+ export_csv_k1min_00700.py： 辅助脚本， 从futu api中导出vnpy需要的csv 数据
+ HK.00700_1min.csv：已经导出的部分HK.00700的分k数据文件
+ loadCsv.py: 源于vnpy库下的examples/CtaBacktesting/loadCsv.py 将csv数据导入到本地mongo数据库中, 用于回测数据需要


## 使用说明:
+ futuquant已兼容python2.7, vnpy最低版本要求v1.9, 因cpickle库的兼容问题， 只能在python2.x下运行该范例
+ 需要用pip 安装的其它库包括 : vnpy, pymongo, future, ta-lib
+ 体验步骤:
	+ 执行export_csv_k1min_00700.py生成csv文件, 如果不需要最新数据，可跳过
	+ 执行loadCsv.py 将csv文件数据导入到vnpy的db中
	+ 执行 runBacktesting.bat(windows)或 设置当前目录为工作目录，再执行runBacktesting.py 
 



