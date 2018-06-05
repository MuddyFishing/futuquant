# encoding: UTF-8

'''
    策略运行脚本
'''
from futuquant.examples.TinyQuant.TinyQuantFrame import *
from TinyStrateSample import *


if __name__ == '__main__':
    my_strate = TinyStrateSample()
    frame = TinyQuantFrame(my_strate)
    frame.run()

