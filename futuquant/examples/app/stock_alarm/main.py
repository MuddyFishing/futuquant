# -*- coding: utf-8 -*-
from futuquant import *
from data_acquisition import *
host='127.0.0.1'
port=12345
subtype_list = [SubType.QUOTE, SubType.ORDER_BOOK, SubType.TICKER, SubType.K_DAY, SubType.RT_DATA, SubType.BROKER]
code_list = ['HK.00700', 'HK.00388', 'HK_FUTURE.999010']
big_sub_codes = ['HK.02318', 'HK.02828', 'HK.00939', 'HK.01093', 'HK.01299', 'HK.00175',
                 'HK.01299', 'HK.01833', 'HK.00005', 'HK.00883', 'HK.00388', 'HK.01398',
                 'HK.01114', 'HK.02800', 'HK.02018', 'HK.03988', 'HK.00386', 'HK.01211',
                 'HK.00857', 'HK.01177',  'HK.02601', 'HK.02628']

quote_test(big_sub_codes, host, port)