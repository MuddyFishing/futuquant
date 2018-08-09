from futuquant import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

#------------- get_owner_plate
# code_list = ['HK.00700', 'HK.00001']
# print(quote_ctx.get_owner_plate(code_list))

#------------- get_holding_change_list
print(quote_ctx.get_holding_change_list('US.AAPL', 3, '2016-10-01 10:00:00'))



quote_ctx.close()




#++++++++++++ trade +++++++++++++#

# ------ _acc_index
# trd_ctx = OpenHKTradeContext(host='127.0.0.1', port=11111)
# trd_env = TrdEnv.SIMULATE
# print(trd_ctx.accinfo_query(trd_env=trd_env))
# print(trd_ctx.place_order(price=5.86, qty=500, code='HK.01357', trd_side=TrdSide.BUY, order_type=OrderType.NORMAL, trd_env=trd_env))
# trd_ctx.close()
