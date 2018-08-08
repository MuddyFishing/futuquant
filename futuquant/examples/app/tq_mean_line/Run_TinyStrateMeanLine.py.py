# encoding: UTF-8

'''
    策略运行脚本
'''
from futuquant.examples.TinyQuant.TinyQuantFrame import *
from TinyStrateMeanLine import *


if __name__ == '__main__':
    my_strate = TinyStrateMeanLine()
    frame = TinyQuantFrame(my_strate)
    frame.run()

