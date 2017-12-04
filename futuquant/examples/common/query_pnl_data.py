# -*- coding: utf-8 -*-
"""
    1. get_pnl_raw_data
    2. get_pnl_series_data
"""

from futuquant.open_context import *
from get_trade_status import *


def get_pnl_raw_data(quote_context, code, start='2017-01-01', end='2017-12-30'):
    '''
    不考虑停牌，从历史数据中获取计算逐日累计收益率
    :param quote_context: api行情对象
    :param code: 股票代码
    :param start: 开始时间 '%Y-%m-%d'
    :param end: 结束时间 '%Y-%m-%d'
    :return: (ret, data) ret == 0 data为pd dataframe数据， 表头'code' 'datetime' 'pnl'
                         ret != 0 data为错误字符串
    '''
    ret, data = quote_context.get_history_kline(code, start, end, 'K_DAY', 'qfq')
    if 0 != ret:
        return ret, data
    data.sort_values(by='time_key', axis=0, ascending=True)

    raw_list = []
    close_0 = 0
    for ix, row in data.iterrows():
        close_n = row['close']
        if 0 == close_0:
            close_0 = float(close_n)
        pnl = (close_n - close_0) / close_0 * 100.0 if close_0 != 0 else 0.0
        raw_list.append({'code': code, 'pnl': pnl, 'datetime': str(row['time_key']).split(' ')[0]})

    col_list = ['code', 'datetime', 'pnl']
    pd_ret = pd.DataFrame(raw_list, columns=col_list)

    return RET_OK, pd_ret


def get_pnl_series_data(quote_context, code, start='2017-01-01', end='2017-12-30', code_base=None):
    '''
    以交易日为时间序，从历史数据中计算逐日累计收益率
    :param quote_context: api行情对象
    :param code: 股票代码
    :param start: 开始时间 '%Y-%m-%d'
    :param end: 结束时间 '%Y-%m-%d'
    :param code_base: 计算超额收益率的基准code
    :return: (ret, data) ret == 0 data为pd dataframe数据， 表头'code' 'datetime' 'pnl' 'excess_pnl'(需指定code_base)
                         ret != 0 data为错误字符串
    '''
    # raw pnl
    raw_dst = None
    raw_base = None
    for x in [code, code_base]:
        if not x:
            continue
        ret, data = get_pnl_raw_data(quote_context, x, start, end)
        if 0 != ret:
            return ret, data
        if x == code and not raw_dst:
            raw_dst = data
        else:
            raw_base = data

    if raw_dst is None or 0 == len(raw_dst):
        return RET_ERROR, ('%s has no history kline data!' % code)

    if raw_base is not None and 0 == len(raw_base):
        return RET_ERROR, ('%s has no history kline data!' % code_base)

    # 获取股票对应的交易日时间序
    ret, trade_data = get_trade_status(quote_context, code, start, end, TRADE_DAYS)
    if 0 != ret:
        return ret, trade_data

    # 计算返回的数据
    last_pnl = 0
    last_base_pnl = 0
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

        # 收益率
        dst_find = raw_dst[raw_dst.datetime == dt_time]
        if dst_find.iloc[:, 0].size > 0:
            last_pnl = dst_find.iloc[0]['pnl']

        dict_item['pnl'] = last_pnl
        # 相对基准的超额收益率
        if raw_base is not None:
            base_find = raw_base[raw_base.datetime == dt_time]
            if base_find.iloc[:, 0].size > 0:
                last_base_pnl = base_find.iloc[0]['pnl']
            dict_item['excess_pnl'] = last_pnl - last_base_pnl
            dict_item['base_pnl'] = last_base_pnl

        list_ret.append(dict_item.copy())

    col_list = ['code', 'datetime', 'pnl']
    if raw_base is not None:
        col_list.append('excess_pnl')
        col_list.append('base_pnl')

    pd_frame = pd.DataFrame(list_ret, columns=col_list)

    return RET_OK, pd_frame

if __name__ == "__main__":
    api_ip = '127.0.0.1'  # ''119.29.141.202'
    api_port = 11111
    code = 'HK.00700'
    start = '2017-01-01'
    end = '2017-12-30'
    code_base = 'HK.800000' #'HK.02858'

    quote_context = OpenQuoteContext(host=api_ip, port=api_port)

    # print(get_pnl_raw_data(quote_context, code, start, end))
    print(get_pnl_series_data(quote_context, code, start, end, code_base))

    quote_context.close()