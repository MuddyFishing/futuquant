# -*- coding: utf-8 -*-

from __future__ import division

import sys
from os.path import dirname, abspath, join, sep
futuquant = dirname(dirname(dirname(dirname(abspath(__file__)))))
assert futuquant.split(sep)[-1].lower() == 'futuquant'
# sys.path.append(futuquant)
sys.path.insert(0, futuquant)
print('futuquant folder appended to path: ', futuquant)
