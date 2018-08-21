# -*- coding:utf-8 -*-
from futuquant import *
import pandas


def test_get_option_chain():
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ret_code, ret_data = quote_ctx.get_option_chain('US.AAPL', '2018-09-07', '2018-09-07',
                                                    OptionType.CALL, OptionCondType.ALL)
    print(ret_data)


if __name__ == '__main__':
    pandas.set_option('max_columns', 100)
    pandas.set_option('display.width', 1000)
    test_get_option_chain()



