# -*- coding: utf-8 -*-
"""
    get_trade_status
    指定股票、起止日期， 返回以日期为系列的交易状态: '' / 'trading' / 'suspension'
"""

from futuquant.open_context import *
from datetime import datetime, timedelta

# 指定日期类型
ALL_DAYS = 'Alldays'                # 所有的自然天
TRADE_DAYS = 'Tradedays'            # 仅交易日

# 股票交易状态 :
STATUS_NONE = ''                    # 非交易日
STATUS_TRADEING= 'trading'          # 交易日
STATUS_SUPENSION = 'suspension'     # 股票停牌


def get_trade_status(quote_context=None, strcode='HK.00700', start='2016-01-01', end='2017-12-30', days=ALL_DAYS):
    '''
    :param quote_context: api行情对象
    :param strcode: 股票code
    :param start: 开始日期
    :param end: 结束日期
    :param days: 返回的日期类型 见文件头定义 ALL_DAYS （所有的） / TRADE_DAYS (交易日)
    :return: (ret, data)  ret == 0  data为 pd.dataframe数据 表头为 “DateTime”  “Trade_status”
                          ret != 0  data为错误字符串
    '''
    if not quote_context:
        raise Exception("get_trade_status - quote_context param error!")

    # 获取股票市场
    ret_code, content = split_stock_str(strcode)
    if ret_code != RET_OK:
        raise Exception("get_trade_status - strcode param error!")
    market_val, _ = content

    # 得到该市场的所有交易日
    ret, data_trade = quote_context.get_trading_days(TRADE.REV_MKT_MAP[market_val], start, end)
    if ret != 0:
        return ret, str(data_trade)
    data_trade = sorted(data_trade)
    dict_trade = {x: True for x in data_trade}

    # 得到指定时间内，股票的停牌日
    ret, data_sup = quote_context.get_suspension_info(strcode, start, end)
    if ret != 0:
        return ret, str(data_sup)

    # 停牌数据转成list , dict, 以便后续计算
    str_dates = ''
    for ix, row in data_sup.iterrows():
        str_dates = row['suspension_dates']

    list_sup = str_dates.split(',')
    dict_sup = {x: True for x in list_sup}

    # 依据参数计算返回股票各天的交易状态
    ret_status = []
    if days == TRADE_DAYS:
        for x in data_trade:
            ret_status.append({'DateTime': x, 'Trade_status': STATUS_SUPENSION if (x in dict_sup) else STATUS_TRADEING})
    elif days == ALL_DAYS:
        dt_cur = datetime.strptime(start, '%Y-%m-%d')
        dt_end = datetime.strptime(end, '%Y-%m-%d')
        str_dt = start
        dt_finish = False
        while not dt_finish:
            str_status = STATUS_NONE
            if str_dt in dict_sup:
                str_status = STATUS_SUPENSION
            elif str_dt in dict_trade:
                str_status = STATUS_TRADEING

            ret_status.append({'DateTime': str_dt, 'Trade_status': str_status})
            dt_cur = dt_cur + timedelta(days=1)
            str_dt = dt_cur.strftime('%Y-%m-%d')
            dt_finish = dt_cur > dt_end
    else:
        raise Exception("get_trade_status - days param error!")

    # 组装返回数据为dataframe数据
    col_list = ['DateTime', 'Trade_status']
    pd_frame = pd.DataFrame(ret_status, columns=col_list)

    return RET_OK, pd_frame

if __name__ == "__main__":
    api_ip = '127.0.0.1'  # ''119.29.141.202'
    api_port = 11111

    quote_context = OpenQuoteContext(host=api_ip, port=api_port)
    print(get_trade_status(quote_context))
    quote_context.close()