# -*- coding: utf-8 -*-
"""
    1. get_change_rate_raw_data
    2. get_change_rate_series_data
"""

from futuquant.open_context import *
from get_trade_status import *


def get_change_rate_raw_data(quote_context, code, start='2017-01-01', end='2017-12-30'):
    '''
    不考虑停牌，从历史数据中获取计算逐日涨跌幅
    :param quote_context: api行情对象
    :param code: 股票代码
    :param start: 开始时间 '%Y-%m-%d'
    :param end: 结束时间 '%Y-%m-%d'
    :return: (ret, data) ret == 0 data为pd dataframe数据， 表头'code' 'datetime' 'close' 'change_rate'
                         ret != 0 data为错误字符串
    '''
    ret, data = quote_context.get_history_kline(code, start, end, 'K_DAY', 'qfq')
    if 0 != ret:
        return ret, data
    data.sort_values(by='time_key', axis=0, ascending=True)

    raw_list = []
    for ix, row in data.iterrows():
        kl_close = row['close']
        kl_open = row['open']
        change_rate = (kl_close - kl_open) / kl_open * 100.0 if kl_open != 0 else 0.0
        raw_list.append({'code': code, 'close': kl_close, 'change_rate': change_rate, 'datetime': str(row['time_key']).split(' ')[0]})

    col_list = ['code', 'close', 'datetime', 'change_rate']
    pd_ret = pd.DataFrame(raw_list, columns=col_list)

    return RET_OK, pd_ret


def get_change_rate_series_data(quote_context, code, start='2017-01-01', end='2017-12-30', code_base=None):
    '''
    以交易日为时间序，从历史数据中计算逐日涨跌幅
    :param quote_context: api行情对象
    :param code: 股票代码
    :param start: 开始时间 '%Y-%m-%d'
    :param end: 结束时间 '%Y-%m-%d'
    :param code_base: 计算超额涨跌幅的基准code
    :return: (ret, data) ret == 0 data为pd dataframe数据， 表头'code' 'close'  'datetime' 'change_rate' 'excess_change_rate'(需指定code_base)
                         ret != 0 data为错误字符串
    '''
    # raw change_rate
    raw_dst = None
    raw_base = None
    for x in [code, code_base]:
        if not x:
            continue
        ret, data = get_change_rate_raw_data(quote_context, x, start, end)
        if 0 != ret:
            return ret, data
        if x == code and not raw_dst:
            raw_dst = data
        else:
            raw_base = data

    if raw_dst is None:
        return RET_ERROR, 'no data'

    # 获取股票对应的交易日时间序
    ret, trade_data = get_trade_status(quote_context, code, start, end, TRADE_DAYS)
    if 0 != ret:
        return ret, trade_data

    # 计算返回的数据
    last_close = 0
    last_val = 0
    last_base_val = 0
    list_ret = []
    dict_item = {}

    max_datetime = raw_dst.iloc[-1]['datetime']
    for ix, row in trade_data.iterrows():
        dict_item['code'] = code

        dt_time = row['datetime']
        dict_item['datetime'] = dt_time

        # raw 没有数据就中止
        if dt_time > max_datetime:
            break

        # 涨跌幅
        dst_find = raw_dst[raw_dst.datetime == dt_time]
        if dst_find.iloc[:, 0].size > 0:
            last_val = dst_find.iloc[0]['change_rate']
            last_close = dst_find.iloc[0]['close']

        dict_item['change_rate'] = last_val
        dict_item['close'] = last_close

        # 相对基准的超额涨跌幅
        if raw_base is not None:
            base_find = raw_base[raw_base.datetime == dt_time]
            if base_find.iloc[:, 0].size > 0:
                last_base_val = base_find.iloc[0]['change_rate']
            dict_item['excess_change_rate'] = last_val - last_base_val

        list_ret.append(dict_item.copy())

    col_list = ['code', 'close', 'datetime', 'change_rate', ]
    if raw_base is not None:
        col_list.append('excess_change_rate')

    pd_frame = pd.DataFrame(list_ret, columns=col_list)

    return RET_OK, pd_frame

if __name__ == "__main__":
    api_ip = '127.0.0.1'  # ''119.29.141.202'
    api_port = 11111
    code = 'HK.00700'
    start = '2017-01-01'
    end = '2017-12-30'

    quote_context = OpenQuoteContext(host=api_ip, port=api_port)

    # print(get_change_rate_raw_data(quote_context, code, start, end))
    print(get_change_rate_series_data(quote_context, code, start, end, 'HK.800000'))

    quote_context.close()