# -*- coding: utf-8 -*-
from futuquant import *
from wx_push import wechat_push
import logging
from mysql_interface import mysql_interface

mi = mysql_interface()
wp = wechat_push()

def detect(content, openid, warning_threshold, large_threshold):

    code = content[0]['code']
    time = content[0]['time']
    price = content[0]['price']
    vol = content[0]['volume']
    direction = content[0]['ticker_direction']

    prev_price = mi.get_preprice_by_shockid(code)

    msg = {}
    sent_msg_sig = 0
    # print(warning_threshold, large_threshold)

    if not prev_price:   # 之前数据库里无这股票的价格记录
        pass
    elif price - prev_price > 0.5:
        # 检查成交量：
        if int(vol) * price > warning_threshold:   # price * vol
            sent_msg_sig = 1
            msg.update({'echo_type': '异常成交提醒'})
    elif int(vol) * price > large_threshold:   # 单笔成交金额超过400万
        sent_msg_sig = 1
        msg.update({'echo_type': '单笔大额成交'})

    if(sent_msg_sig):
        print(warning_threshold, large_threshold)
        msg.update({'code':str(code), 'price': str(price), 'total_deal_price':str(int(vol)*price/10000), 'quantity': str(vol), 'time': str(time)})
        wechat_push.send_template_msg(openid, msg)
        logging.info("Send a message.")

    # 更新 逐笔成交信息
    mi.update_price(code, price)

def detect_and_send(content):
    setting_list = mi.get_all_user_setting()
    for usr_setting in setting_list:
        detect(content, usr_setting[0], usr_setting[1], usr_setting[2])





