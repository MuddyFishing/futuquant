# -*- coding: utf-8 -*-
"""
    export_csv_k1m_file
    从futu api中导出vnpy需要的1分k回测数据csv文件
"""

from futuquant import *


def export_csv_k1m_file(quote_context, code, start='2017-11-01', end=None):
    '''
    :param quote_context:
    :param code: futu 股票代码 eg HK.00700 / US.AAPL
    :param start:历史数据起始时间
    :param end: 历史数据结束时间
    :return: 0 = 成功 , 其它失败
    '''
    # 得到历史数据
    kl_fileds = [KL_FIELD.DATE_TIME, KL_FIELD.OPEN, KL_FIELD.CLOSE, KL_FIELD.HIGH, KL_FIELD.LOW, KL_FIELD.TRADE_VOL]
    ret, data_frame = quote_context.get_history_kline(code, start, end, 'K_1M', 'qfq', kl_fileds)

    if 0 != ret:
        print (data_frame)
        return ret

    # 增加一列，并修改原列名
    data_frame['Date'] = data_frame['time_key']
    data_frame.rename(columns={'time_key': 'Time', 'open': 'Open', 'close': 'Close', 'high': 'High', 'low': 'Low',
                               'volume': 'TotalVolume'}, inplace=True)
    # 修改Date/Time 列数据
    for ix, row in data_frame.iterrows():
        date_time = str(row['Date'])
        date, time = date_time.split(' ')
        data_frame.loc[ix, 'Date'] = date
        data_frame.loc[ix, 'Time'] = time

    print(data_frame)
    # 保存到csv文件中
    code_name = copy(code)
    csv_file = code_name + '_1min.csv'
    data_frame.to_csv(csv_file, index=False, sep=',',
                      columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'TotalVolume'])
    return RET_OK

if __name__ == "__main__":

    # 参数配置
    ip = '119.29.141.202'
    port = 11111
    code = 'HK.00700'  # 腾讯
    quote_context = OpenQuoteContext(ip, port)

    # 导出csv文件数据
    export_csv_k1m_file(quote_context, code)

    # 正常关闭对象
    quote_context.close()




