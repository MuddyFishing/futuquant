# -*- coding: utf-8 -*-
"""
    query_change_stocks
    指定股票、起止日期， 返回以日期为系列的交易状态: '' / 'trading' / 'suspension'
"""

from futuquant.open_context import *
from datetime import datetime, timedelta


def query_change_stocks(quote_context=None, markets=['HK'], start='2017-01-05', end='2017-12-30', change_min=5.0,
                            change_max=None, stock_type='STOCK', ascend=True):
    '''
    :param quote_context: api
    :param markets:
    :param start:
    :param end:
    :param change_min:
    :param change_max:
    :param stock_type:
    :param ascend:
    :return:
    '''
    if not markets or (not is_str(markets) and not isinstance(markets, list)):
        error_str = "the type of markets param is wrong"
        return RET_ERROR, error_str
    req_markets = markets if isinstance(markets, list) else [markets]

    if not change_min and not change_max:
        return RET_ERROR, "param change is wrong"

    list_stocks = []
    for mk in req_markets:
        ret, data = quote_context.get_stock_basicinfo(mk, stock_type)
        if 0 != ret:
            return ret, data
        for ix, row in data.iterrows():
            list_stocks.append(row['code'])

    dt_last = datetime.now()
    ret_list = []
    ret, data = quote_context.get_multi_points_history_kline(list_stocks, [start, end], [KL_FIELD.DATE_TIME, KL_FIELD.CLOSE], 'K_DAY', 'hfq')
    if 0 != ret:
        return ret, data
    dt = datetime.now() - dt_last
    print('get_multi_points_history_kline - run time = %s秒' % dt.seconds)

    for stock in list_stocks:
        pd_find = data[data.code == stock]
        close_start = 0
        close_end = 0
        real_times = []
        for _, row in pd_find.iterrows():
            if 0 == row['data_valid']:
                break
            if row['time_point'] == start:
                close_start = row['close']
                real_times.append(row['time_key'])
            elif row['time_point'] == end:
                close_end = row['close']
                real_times.append(row['time_key'])
        if close_start and close_end:
            change_rate = (close_end - close_start) / float(close_start) * 100.0
            data_ok = True
            if change_min is not None:
                data_ok = change_rate >= change_min
            if data_ok and change_max is not None:
                data_ok = change_rate <= change_max
            if data_ok:
                ret_list.append({'code': stock, 'change_rate': change_rate, 'real_times': ','.join(real_times)})

    ret_list = sorted(ret_list, key=lambda x: x['change_rate'], reverse=(not ascend))

    col_list = ['code', 'change_rate', 'real_times']
    pd_frame = pd.DataFrame(ret_list, columns=col_list)

    return RET_OK, pd_frame

if __name__ == "__main__":
    api_ip = '127.0.0.1'  # ''119.29.141.202'
    api_port = 11111

    quote_context = OpenQuoteContext(host=api_ip, port=api_port)
    print(query_change_stocks(quote_context))
    quote_context.close()