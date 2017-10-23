import sys


def is_str(obj):
    if sys.version_info.major == 3:
        return isinstance(obj, str) or isinstance(obj, bytes)
    else:
        return isinstance(obj, basestring)

def str_price1000(price):
    return str(int(round(float(price) * 1000, 0))) if str(price) is not '' else ''

