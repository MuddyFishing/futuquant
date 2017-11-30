# -*- coding: utf-8 -*-

import sys


def is_str(obj):
    if sys.version_info.major == 3:
        return isinstance(obj, str) or isinstance(obj, bytes)
    else:
        return isinstance(obj, basestring)


def price_to_str_int1000(price):
    return str(int(round(float(price) * 1000, 0))) if str(price) is not '' else ''


# 1000*int price to float val
def int1000_price_to_float(price):
    return round(float(price) / 1000.0, 3) if str(price) is not '' else float(0)


# 10^9 int price to float val
def int10_9_price_to_float(price):
    return round(float(price) / float(10**9), 3) if str(price) is not '' else float(0)


# list 参数除重及规整
def unique_and_normalize_list(lst):
    ret = []
    if not lst:
        return ret
    tmp = lst if isinstance(lst, list) else [lst]
    [ret.append(x) for x in tmp if x not in ret]
    return ret


