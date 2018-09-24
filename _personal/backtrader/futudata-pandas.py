#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015, 2016 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import backtrader as bt
import backtrader.feeds as btfeeds

import pandas

# import __init__
import futuquant as ft
# from futuquant.constant import *

def runstrat():
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(bt.Strategy)

    # Get a pandas dataframe
    # datapath = ('E:/workspace/code/backtrader/datas/2006-day-001.txt')
    datapath = ('E:/workspace/code/backtrader/datas/yhoo-2003-2005.txt')

    # Simulate the header row isn't there if noheaders requested
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0

    dataframe = pandas.read_csv(
        datapath,
        skiprows=skiprows,
        header=header,
        # parse_dates=[0],
        parse_dates=True,
        index_col=0,
    )

    print(1)
    # print(dataframe['Open'])
    # print(dataframe.index)
    # print(dataframe.Volume)
    # print(dataframe)
    # if not args.noprint:
    #     print('--------------------------------------------------')
    #     print(dataframe)
    #     print('--------------------------------------------------')

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe,
                               # datetime='Date',
                               nocase=True,
                               )
    # print(data)

    quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    # _, prices = quote_ctx.get_history_kline('US.CMCM', start='2018-03-21',
    #                                         fields=[KL_FIELD.DATE_TIME, KL_FIELD.OPEN, KL_FIELD.HIGH,
    #                                                 KL_FIELD.LOW, KL_FIELD.CLOSE, KL_FIELD.TRADE_VOL])
    _, prices = quote_ctx.get_history_kline('US.CMCM', start='2018-03-21')
    quote_ctx.close()
    print(prices)
    
    # print(2)
    # print(prices['open'])
    # print(prices.open)
    
    # df.drop(columns=['B', 'C'])
    # df.reindex(new_index)
    # df.reindex(new_index, fill_value=0)
    # df.reindex(new_index, fill_value='missing')
    # df.reindex(columns=['http_status', 'user_agent'])
    # df.rename(index=str, columns={"A": "a", "C": "c"})

    # df.assign(Data=df.time_key.apply(lambda x:str(x)[0:10]).set_index('Data')

    # Date = 
    # print(3)
    # print(prices)
    # prices = prices.reindex()
    prices = prices.assign(Data=prices.time_key.apply(lambda x:str(x)[0:10])).set_index('Data')
    print(len(prices))

    print(4)
    prices = prices.drop(columns=['code', 'time_key'])
    prices = prices.rename(index=str, columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    # print(prices)
    print(prices.index)
    # print(prices['Open'])
    # print(prices['High'])
    # print(prices['Low'])
    # print(prices['Close'])
    
    # TypeError: must be real number, not str
    prices['Volume'] = prices['Volume'].astype('int64')
    # datetime64[ns]
    prices.index = prices.index.astype('datetime64[ns]')
    # print(prices['Volume'])

    # Pass it to the backtrader datafeed and add it to the cerebro
    data2 = bt.feeds.PandasData(dataname=prices,
                            #    datetime='Date',
                               nocase=True,
                               )

    cerebro.adddata(data2)

    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='style="candle"')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
