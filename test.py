from futuquant import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

#------------- get_owner_plate
# code_list = ['HK.00700', 'HK.00001']
# print(quote_ctx.get_owner_plate(code_list))

#------------- get_holding_change_list
# print(quote_ctx.get_holding_change_list('US.AAPL', StockHolder.INSTITUTE, '2016-10-01 10:00:00'))

#------------- get_stock_basicinfo
# print(quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.WARRANT))
# print(quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK))

option_type = 2
print(OptionType.PUT)
print(QUOTE.REV_OPTION_TYPE_CLASS_MAP)
print(option_type in QUOTE.REV_OPTION_TYPE_CLASS_MAP)
output = QUOTE.REV_OPTION_TYPE_CLASS_MAP[option_type] if option_type in QUOTE.REV_OPTION_TYPE_CLASS_MAP else OptionType.UNKNOWN
print(output)


quote_ctx.close()




#++++++++++++ trade +++++++++++++#

# ------ _acc_index
# trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
# trd_env = TrdEnv.SIMULATE
# print(trd_ctx.accinfo_query(trd_env=trd_env))
# print(trd_ctx.place_order(price=5.86, qty=500, code='HK.01357', trd_side=TrdSide.BUY, order_type=OrderType.NORMAL, trd_env=trd_env))
# trd_ctx.close()

# api_ip = '127.0.0.1'
# api_port = 11111
# unlock_pwd = '123123'
# trade_context = OpenUSTradeContext(host=api_ip, port=api_port)
# trd_env = TrdEnv.REAL
# print(trade_context.unlock_trade(unlock_pwd))
# print(trade_context.place_order(price=4.4, qty=1, code='US_OPTION.AAPL180907C207500', trd_side=TrdSide.BUY, order_type=OrderType.NORMAL, trd_env=trd_env, acc_id=281756460277401516))
# trade_context.close()


warning_time_list = {}
openid = 'hhhh'
warning_list = ''
warning_time_list.update({openid:warning_list})
if openid in warning_time_list:
    time_str = warning_time_list[openid]
    time_list = time_str.split(',')
    print(len(time_list))
    if len(time_list) == 1 and time_list[0] == '':
        print("no")
    else:
        print(time_list)