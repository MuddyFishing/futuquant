# -*- coding: utf-8 -*-

import logging
from datetime import datetime
import os

logger = logging.getLogger('FT')
log_level = logging.INFO
is_file_log = True

# 设置logger的level为DEBUG
logger.setLevel(log_level)

# 创建一个输出日志到控制台的StreamHandler
hdr = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s [%(filename)s] %(funcName)s:%(lineno)d: %(message)s')
hdr.setFormatter(formatter)

# 给logger添加上handler
logger.addHandler(hdr)

# 添加文件handle
if is_file_log:
    filename = 'ft_' + datetime.now().strftime('%Y%m%d') + '.log'
    tempPath = os.path.join(os.getcwd(), 'log')
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)
    filepath = os.path.join(tempPath, filename)
    fileHandler = logging.FileHandler(filepath)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)


def make_log_msg(title, **kwargs):
    msg = ''
    if len(kwargs) > 0:
        msg = ':'
        for k, v in kwargs.items():
            msg += ' {0}={1};'.format(k, v)
    return title + msg



