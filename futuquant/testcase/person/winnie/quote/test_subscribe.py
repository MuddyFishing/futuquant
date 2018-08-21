# -*- coding:utf-8 -*-
from futuquant import *


def test_subscribe():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    print(quote_ctx.subscribe(['HK.00001'], SubType.TICKER))
    print(quote_ctx.query_subscription())


if __name__ == '__main__':
    test_subscribe()
