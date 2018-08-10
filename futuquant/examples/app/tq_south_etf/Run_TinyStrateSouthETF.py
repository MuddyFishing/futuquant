# encoding: UTF-8

'''
    运行须知:
    1. 需要先安装vnpy / ta-lib, 暂时仅能运行在python2.7环境,
    2. TinyQuantFrame封装了futu api 的调用，有关futu api的使用请参见 https://futunnopen.github.io/futuquant/intro/intro.html
    3. 支持港/美股实盘策略运行，港股可以下模拟单, 不支持数据回测
    4. 策略实现参考 TinyStrateSample.py文件
'''

from futuquant.examples.TinyQuant.TinyQuantFrame import *
from .TinyStrateSouthETF import *

if __name__ == '__main__':
    my_strate = TinyStrateSouthETF()
    frame = TinyQuantFrame(my_strate)
    frame.run()

