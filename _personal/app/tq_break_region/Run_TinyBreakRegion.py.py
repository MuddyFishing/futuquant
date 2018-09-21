# -*- coding: utf-8 -*-

'''
    策略运行脚本
'''
import __init__
from futuquant.examples.TinyQuant.TinyQuantFrame import *
from TinyBreakRegion import *


if __name__ == '__main__':
    my_strate = TinyBreakRegion()
    frame = TinyQuantFrame(my_strate)
    frame.run()
