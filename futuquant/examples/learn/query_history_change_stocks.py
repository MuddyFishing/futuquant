# -*- coding: utf-8 -*-
"""
    query_history_change_stocks
    指定涨跌幅，查询本地下载的历史日k数据，返回符合条件的股票
"""

from datetime import datetime

from futuquant import *



def query_history_change_stocks(quote_context=None, markets=[Market.HK], start='2017-01-05', end='2017-1-10', change_min=5.0,
                            change_max=None, stock_type=SecurityType.STOCK, ascend=True):
    '''
    :param quote_context: api 行情对象
    :param markets: 要查询的市场列表, 可以只传单个市场如'HK'字符串
    :param start: 开始时间
    :param end: 截止时间
    :param change_min: 涨跌幅最小值 eg: 1.0% 传值 1.0, None表示忽略
    :param change_max: 涨跌幅最大值
    :param stock_type: 要查询的股票类型, 见 SEC_TYPE_MAP - 'STOCK','IDX','ETF','WARRANT','BOND'
    :param ascend: 结果是否升序排列
    :return: (ret, data), ret == 0返回pd dataframe, 表头为 'code'(股票代码), 'change_rate'(涨跌率*100), 'real_times'(起止真实交易时间字符串)
                          ret != 0 data 为错误字符串
    '''
    if not markets or (not is_str(markets) and not isinstance(markets, list)):
        error_str = "the type of markets param is wrong"
        return RET_ERROR, error_str
    req_markets = markets if isinstance(markets, list) else [markets]

    if change_min is None and change_max is None:
        return RET_ERROR, "param change is wrong"

    # float 比较有偏差 比如 a = 1.0 , b = 1.1, c = (b-a)/a * 100, d = 10 ,  c<=d 结果为False
    if change_min is not None:
        change_min = int(float(change_min) * 1000)
    if change_max is not None:
        change_max = int(float(change_max) * 1000)

    # 汇总得到需要查询的所有股票code
    list_stocks = []
    for mk in req_markets:
        ret, data = quote_context.get_stock_basicinfo(mk, stock_type)
        if 0 != ret:
            return ret, data
        for ix, row in data.iterrows():
            list_stocks.append(row['code'])

    # 多点k线数据查询
    dt_last = datetime.now()
    ret_list = []
    ret, data_start = quote_context.get_multi_points_history_kline(list_stocks, [start],
                                                             [KL_FIELD.DATE_TIME, KL_FIELD.CLOSE], KLType.K_DAY, AuType.QFQ,
                                                                   KLNoDataMode.FORWARD)
    if ret != 0:
        return ret, data_start
    ret, data_end = quote_context.get_multi_points_history_kline(list_stocks, [end],
                                                             [KL_FIELD.DATE_TIME, KL_FIELD.CLOSE], KLType.K_DAY, AuType.QFQ,
                                                                 KLNoDataMode.FORWARD)
    if ret != 0:
        return ret, data_end

    # 合并数据
    data = data_start.append(data_end)

    dt = datetime.now() - dt_last
    print('get_multi_points_history_kline - run time = %s秒' % dt.seconds)

    # 返回计算涨跌幅，统计符合条件的股票
    for stock in list_stocks:
        pd_find = data[data.code == stock]
        close_start = 0
        close_end = 0
        real_times = []
        for _, row in pd_find.iterrows():
            if KLDataStatus.NONE == row['data_status']:
                break
            if row['time_point'] == start:
                close_start = row['close']
                real_times.append(row['time_key'])
            elif row['time_point'] == end:
                close_end = row['close']
                real_times.append(row['time_key'])
        if close_start and close_end:
            change_rate = (close_end - close_start) / float(close_start) * 100000.0
            data_ok = True
            if change_min is not None:
                data_ok = change_rate >= change_min
            if data_ok and change_max is not None:
                data_ok = change_rate <= change_max
            if data_ok:
                ret_list.append({'code': stock, 'change_rate':  float(change_rate / 1000.0), 'real_times': ','.join(real_times)})

    # 数据排序
    ret_list = sorted(ret_list, key=lambda x: x['change_rate'], reverse=(not ascend))

    # 组装返回pdframe数据
    col_list = ['code', 'change_rate', 'real_times']
    pd_frame = pd.DataFrame(ret_list, columns=col_list)

    return RET_OK, pd_frame

if __name__ == "__main__":
    api_ip = '127.0.0.1'  # ''119.29.141.202'
    api_port = 11111
    change_min = 1
    change_max = 2

    quote_context = OpenQuoteContext(host=api_ip, port=api_port)
    print(query_history_change_stocks(quote_context, [Market.HK], '2017-01-10', '2017-1-15', change_min, change_max, SecurityType.ETF))
    quote_context.close()