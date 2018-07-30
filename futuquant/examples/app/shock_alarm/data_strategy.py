# -*- coding: utf-8 -*-
from futuquant import *
from wx_push import wechat_push
import logging
from mysql_interface import mysql_interface
import common_parameter
import time

mi = mysql_interface()
wp = wechat_push()

def detect_warning_times(openid, warning_limit):
    sent_msg_sig = 1
    now_time = time.time()
    result = mi.get_time_list_by_openid(openid)
    new_time_list = ''
    cnt = 0
    if result:
        time_str = result[0][1]
        time_list = time_str.split(',')
        if (time_list.__len__ == 1 and time_list[0] == ''):  # 当warning_time_list为“”时
            pass
        else:
            first_flag = 1
            for tmp_time in time_list:
                if (now_time - float(tmp_time) < 60):
                    if not first_flag:  # 如果不是第一个，就需要添加','符号
                        new_time_list += ','
                    new_time_list += tmp_time
                    cnt += 1

    if cnt <= warning_limit:
        new_time_list = new_time_list + ',' + now_time
    else:
        sent_msg_sig = 0
        print("The number of warning is exceeded. %d, %d" % (cnt, warning_limit))
    mi.update_warning_list(openid, new_time_list)
    return sent_msg_sig

def detect(content, prev_price, openid, premium_rate, warning_threshold, large_threshold, warning_limit):
    code = content[0]['code']
    ttime = content[0]['time']
    price = content[0]['price']
    vol = content[0]['volume']
    direction = content[0]['ticker_direction']

    msg = {}
    sent_msg_sig = 0
    # print(warning_threshold, large_threshold)

    if prev_price == 0:   # 之前数据库里无这股票的价格记录
        pass
    elif abs(price - prev_price) / prev_price > premium_rate:   # 越价
        # 检查成交量：
        if int(vol) * price > warning_threshold:   # price * vol
            sent_msg_sig = 1
            msg.update({'echo_type': '异常成交提醒'})
    elif int(vol) * price > large_threshold:   # 单笔成交金额超过400万
        sent_msg_sig = 1
        msg.update({'echo_type': '单笔大额成交'})

    if(sent_msg_sig):
        sent_msg_sig = detect_warning_times(openid, warning_limit)

    if(sent_msg_sig):
        # print("+------------------------------------+")
        # print(openid, warning_threshold, large_threshold)
        # print("+------------------------------------+")
        msg.update({'code':str(code), 'price': str(price), 'total_deal_price':str(int(vol)*price/10000), 'quantity': str(vol), 'time': str(ttime)})
        wp.send_template_msg(openid, msg)
        logging.info("Send a message.")

def get_preprice(content):
    code = content[0]['code']
    prev_price = 0
    result = mi.get_preprice_by_stockid(code)
    if result:
        prev_price = result[0][1]
    return prev_price

def update_price(content):
    code = content[0]['code']
    price = content[0]['price']
    # 更新 逐笔成交信息
    mi.update_price(code, price)

def detect_and_send(content):
    prev_price = get_preprice(content)

    user_list = common_parameter.test_user_list
    for openid in user_list:
        usr_setting = mi.get_setting_by_openid(openid)
        if usr_setting:
            detect(content, prev_price, usr_setting[0][0], usr_setting[0][1], usr_setting[0][2], usr_setting[0][3], usr_setting[0][4])
        else:
            detect(content, prev_price, openid, common_parameter.premium_rate, common_parameter.warning_threshold, common_parameter.large_threshold, common_parameter.warning_limit)

    update_price(content)