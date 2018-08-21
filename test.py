from futuquant import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret, data = quote_ctx.get_market_snapshot(['US_OPTION.AAPL180914C215000', 'HK.00700'])

print(ret, data)

# data.to_csv('C:\\Users\\admin\\Desktop\\option_chain.csv')
# print(data)

# code = 'US.AAPL'
# print(quote_ctx.get_option_chain(code, '2018-08-01', '2018-08-18', OptionType.ALL, OptionCondType.ALL))

# print(quote_ctx.get_stock_basicinfo(Market.US, SecurityType.DRVT, 'US_OPTION.AAPL180817C20000'))
code_list = ['US_OPTION.AAPL180914C212500']
# print(quote_ctx.subscribe(code_list, [SubType.QUOTE]))
# print(quote_ctx.get_stock_quote(code_list))

quote_ctx.close()