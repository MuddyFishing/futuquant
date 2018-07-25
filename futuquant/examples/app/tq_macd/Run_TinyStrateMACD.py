# encoding: UTF-8

'''
    策略运行脚本
'''
from futuquant.examples.TinyQuant.TinyQuantFrame import *
from TinyStrateMACD import *


if __name__ == '__main__':
    my_strate = TinyStrateMACD()
    frame = TinyQuantFrame(my_strate)
    frame.run()

