import logging
logger = logging.getLogger('FT')

# 设置logger的level为DEBUG
logger.setLevel(logging.CRITICAL)

# 创建一个输出日志到控制台的StreamHandler
hdr = logging.StreamHandler()
formatter = logging.Formatter(
    '[%(filename)s] %(funcName)s:%(lineno)d: %(message)s')
hdr.setFormatter(formatter)

# 给logger添加上handler
logger.addHandler(hdr)

