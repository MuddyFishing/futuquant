# encoding: UTF-8

"""
导入MC导出的CSV历史数据到MongoDB中
"""

from vnpy.trader.app.ctaStrategy.ctaBase import MINUTE_DB_NAME
from vnpy.trader.app.ctaStrategy.ctaHistoryData import loadMcCsv


if __name__ == '__main__':
    loadMcCsv('HK.00700_1min.csv', MINUTE_DB_NAME, 'HK.00700')

