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
import datetime
import random

import backtrader as bt
import backtrader.feeds as btfeeds

import __init__
import futuquant as ft

BTVERSION = tuple(int(x) for x in bt.__version__.split('.'))


class FixedPerc(bt.Sizer):
    '''This sizer simply returns a fixed size for any operation

    Params:
      - ``perc`` (default: ``0.20``) Perc of cash to allocate for operation
    '''

    params = (
        ('perc', 0.20),  # perc of cash to use for operation
    )

    def _getsizing(self, comminfo, cash, data, isbuy):
        cashtouse = self.p.perc * cash
        if BTVERSION > (1, 7, 1, 93):
            size = comminfo.getsize(data.close[0], cashtouse)
        else:
            size = cashtouse // data.close[0]
        return size


class TheStrategy(bt.Strategy):
    '''
    This strategy is loosely based on some of the examples from the Van
    K. Tharp book: *Trade Your Way To Financial Freedom*. The logic:

      - Enter the market if:
        - The MACD.macd line crosses the MACD.signal line to the upside
        - The Simple Moving Average has a negative direction in the last x
          periods (actual value below value x periods ago)

     - Set a stop price x times the ATR value away from the close

     - If in the market:

       - Check if the current close has gone below the stop price. If yes,
         exit.
       - If not, update the stop price if the new stop price would be higher
         than the current
    '''

    params = (
        # Standard MA Parameters
        ('ma1', 1),
        ('ma2', 3),
        ('ma3', 5),
        ('ma4', 34),
        ('ma5', 120),
        ('ma6', 250),
        ('atrperiod', 14),  # ATR Period (standard)
        ('atrdist', 3.0),   # ATR distance for stop price
        ('smaperiod', 30),  # SMA Period (pretty standard)
        ('dirperiod', 10),  # Lookback period to consider SMA trend direction
    )

    def notify_order(self, order):
        if order.status == order.Completed:
            pass

        if not order.alive():
            self.order = None  # indicate no order is pending

    def __init__(self):
        print(self.data)
        self.ma1 = bt.indicators.EMA(self.data, period=self.p.ma1)
        self.ma2 = bt.indicators.EMA(self.data, period=self.p.ma2)
        self.ma3 = bt.indicators.EMA(self.data, period=self.p.ma3)
        self.ma4 = bt.indicators.EMA(self.data, period=self.p.ma4)
        self.ma5 = bt.indicators.EMA(self.data, period=self.p.ma5)
        self.ma6 = bt.indicators.EMA(self.data, period=self.p.ma6)

        # Cross of self.ma1 and self.ma2
        # self.ma_cross_up = bt.indicators.CrossOver(self.ma1, self.ma2)
        # self.ma_cross_down = bt.indicators.CrossOver(self.ma2, self.ma1)

        # life
        self.ma_cross_life_up = bt.indicators.CrossOver(self.ma2, self.ma4)
        print(self.ma_cross_life_up)
        # self.ma_cross_life_down = bt.indicators.CrossOver(self.ma3, self.ma1)

        # To set the stop price
        # self.atr = bt.indicators.ATR(self.data, period=self.p.atrperiod)

        # Control market trend
        # self.sma = bt.indicators.SMA(self.data, period=self.p.smaperiod)
        # self.smadir = self.sma - self.sma(-self.p.dirperiod)

    def start(self):
        self.order = None  # sentinel to avoid operrations on pending order

    def next(self):
        if self.order:
            return  # pending order execution

        if not self.position:  # not in the market
            if self.ma_cross_life_up[0] > 0.0:
                self.order = self.buy()
                # pdist = self.atr[0] * self.p.atrdist
                # self.pstop = self.data.close[0] - pdist

        else:  # in the market
            if self.ma_cross_life_up[0] < 0.0:
                self.close()
            # pclose = self.data.close[0]
            # pstop = self.pstop
            #
            # if pclose < pstop:
            #     self.close()  # stop met - get out
            # else:
            #     pdist = self.atr[0] * self.p.atrdist
            #     # Update only if greater than
            #     self.pstop = max(pstop, pclose - pdist)


def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(args.cash)
    comminfo = bt.commissions.CommInfo_Stocks_Perc(commission=args.commperc,
                                                   percabs=True)

    cerebro.broker.addcommissioninfo(comminfo)

    dkwargs = dict()
    if args.fromdate is not None:
        fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
        dkwargs['fromdate'] = fromdate

    if args.todate is not None:
        todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')
        dkwargs['todate'] = todate

    # print(args.fromdate)
    # print(dkwargs['fromdate'])
    quote_ctx = ft.OpenQuoteContext(host='127.0.0.1', port=11111)
    # ret, prices = quote_ctx.get_history_kline(args.symble, start=args.fromdate, end=args.todate, 
    #                                         fields=[ft.KL_FIELD.DATE_TIME, ft.KL_FIELD.OPEN, ft.KL_FIELD.HIGH,
    #                                                 ft.KL_FIELD.LOW, ft.KL_FIELD.CLOSE, ft.KL_FIELD.TRADE_VOL])
    print(args.symble, args.fromdate)
    ret, prices = quote_ctx.get_history_kline(args.symble, start=args.fromdate)
    quote_ctx.close()
    
    if ret != ft.common.constant.RET_OK:
        print(prices)
        return
    if len(prices) <= 0:
        print(ret)
        print('Empty DataFrame')
        return
    print(111111)
    # print(prices)
    prices = prices.assign(Data=prices.time_key.apply(lambda x:str(x)[0:10])).set_index('Data')
    prices = prices.drop(columns=['code', 'time_key'])
    prices = prices.rename(index=str, columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    
    prices['Volume'] = prices['Volume'].astype('int64')
    prices.index = prices.index.astype('datetime64[ns]')

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=prices,
                            #    datetime='Date',
                               nocase=True,
                               )
    
    cerebro.adddata(data)

    cerebro.addstrategy(TheStrategy,
                        ma1=args.ma1,
                        ma2=args.ma2,
                        ma3=args.ma3,
                        atrperiod=args.atrperiod,
                        atrdist=args.atrdist,
                        smaperiod=args.smaperiod,
                        dirperiod=args.dirperiod)

    cerebro.addsizer(FixedPerc, perc=args.cashalloc)

    # Add TimeReturn Analyzers for self and the benchmark data
    cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='alltime_roi',
                        timeframe=bt.TimeFrame.NoTimeFrame)

    cerebro.addanalyzer(bt.analyzers.TimeReturn, data=data, _name='benchmark',
                        timeframe=bt.TimeFrame.NoTimeFrame)

    # Add TimeReturn Analyzers for the annual returns
    cerebro.addanalyzer(bt.analyzers.TimeReturn, timeframe=bt.TimeFrame.Years)
    # Add a SharpeRatio
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, timeframe=bt.TimeFrame.Years,
                        riskfreerate=args.riskfreerate)

    # Add SQN to qualify the trades
    cerebro.addanalyzer(bt.analyzers.SQN)
    cerebro.addobserver(bt.observers.DrawDown)  # visualize the drawdown evol

    results = cerebro.run()
    st0 = results[0]

    for alyzer in st0.analyzers:
        alyzer.print()

    args.plot = 'style="candle"'
    if args.plot:
        pkwargs = dict(style='bar')
        if args.plot is not True:  # evals to True but is not True
            npkwargs = eval('dict(' + args.plot + ')')  # args were passed
            pkwargs.update(npkwargs)

        cerebro.plot(**pkwargs)


def parse_args(pargs=None):

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Sample for Tharp example with MA')

    # group1 = parser.add_mutually_exclusive_group(required=True)
    group1 = parser.add_mutually_exclusive_group(required=False)

    group1.add_argument('--symble', required=False, action='store',
                        default='US.CMCM',
                        # default='US.RYB',
                        # default='HK.00700',
                        # default='SZ.002027',
                        # default='SZ.300059',
                        # default='SH.600789',
                        help='The symble of the stock')

    parser.add_argument('--fromdate', required=False,
                        default='2018-03-01',
                        help='Starting date in YYYY-MM-DD format')

    parser.add_argument('--todate', required=False,
                        # default=None,
                        default='2018-06-07',
                        help='Ending date in YYYY-MM-DD format')

    parser.add_argument('--cash', required=False, action='store',
                        type=float, default=10000,
                        help=('Cash to start with'))

    parser.add_argument('--cashalloc', required=False, action='store',
                        type=float, default=0.20,
                        help=('Perc (abs) of cash to allocate for ops'))

    parser.add_argument('--commperc', required=False, action='store',
                        type=float, default=0.0033,
                        help=('Perc (abs) commision in each operation. '
                              '0.001 -> 0.1%%, 0.01 -> 1%%'))

    parser.add_argument('--ma1', required=False, action='store',
                        type=int, default=1,
                        help=('MA Period 1 value'))

    parser.add_argument('--ma2', required=False, action='store',
                        type=int, default=3,
                        help=('MA Period 2 value'))

    parser.add_argument('--ma3', required=False, action='store',
                        type=int, default=5,
                        help=('MA Signal Period value'))
    
    parser.add_argument('--ma4', required=False, action='store',
                        type=int, default=34,
                        help=('MA Signal Period value'))
    
    parser.add_argument('--ma5', required=False, action='store',
                        type=int, default=120,
                        help=('MA Signal Period value'))

    parser.add_argument('--ma6', required=False, action='store',
                        type=int, default=250,
                        help=('MA Signal Period value'))

    parser.add_argument('--atrperiod', required=False, action='store',
                        type=int, default=14,
                        help=('ATR Period To Consider'))

    parser.add_argument('--atrdist', required=False, action='store',
                        type=float, default=3.0,
                        help=('ATR Factor for stop price calculation'))

    parser.add_argument('--smaperiod', required=False, action='store',
                        type=int, default=30,
                        help=('Period for the moving average'))

    parser.add_argument('--dirperiod', required=False, action='store',
                        type=int, default=10,
                        help=('Period for SMA direction calculation'))

    parser.add_argument('--riskfreerate', required=False, action='store',
                        type=float, default=0.01,
                        help=('Risk free rate in Perc (abs) of the asset for '
                              'the Sharpe Ratio'))
    # Plot options
    parser.add_argument('--plot', '-p', nargs='?', required=False,
                        metavar='kwargs', const=True,
                        help=('Plot the read data applying any kwargs passed\n'
                              '\n'
                              'For example:\n'
                              '\n'
                              '  --plot style="candle" (to plot candles)\n'))

    if pargs is not None:
        return parser.parse_args(pargs)

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()
