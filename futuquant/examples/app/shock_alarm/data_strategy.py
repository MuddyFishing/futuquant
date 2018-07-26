# -*- coding: utf-8 -*-
from futuquant import *
from wx_push import wechat_push
import logging
from mysql_interface import mysql_interface
import common_parameter
import collections

mi = mysql_interface()
wp = wechat_push()
echo_queue = collections.deque()

def detect(content, prev_price, openid, premium_rate, warning_threshold, large_threshold):

    code = content[0]['code']
    time = content[0]['time']
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

    # 检测是否超过一分钟预警次数

    if(sent_msg_sig):
        # print("+------------------------------------+")
        # print(openid, warning_threshold, large_threshold)
        # print("+------------------------------------+")
        msg.update({'code':str(code), 'price': str(price), 'total_deal_price':str(int(vol)*price/10000), 'quantity': str(vol), 'time': str(time)})
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
    # setting_list = mi.get_all_user_setting()
    # for usr_setting in setting_list:
    #     detect(content, usr_setting[0], usr_setting[1], usr_setting[2])

    # user_list = wp.get_user_openid_list()

    prev_price = get_preprice(content)

    # 检测已经预警的次数
    now_time = time.time()
    while echo_queue.__len__() > 0:
        tmp = echo_queue.popleft()
        print(tmp)
        if(now_time - tmp < 60):   # 在1分钟内的压回队首
            echo_queue.appendleft(tmp)
            break;
    echo_queue.append(now_time)
    already_warning_times = echo_queue.__len__()


    user_list = common_parameter.test_user_list
    for openid in user_list:
        usr_setting = mi.get_setting_by_openid(openid)
        if usr_setting:
            if(already_warning_times > usr_setting[0][4]):
                print("The number of warning is exceeded. %d, %d" %(already_warning_times, usr_setting[0][4]))
                continue
            detect(content, prev_price, usr_setting[0][0], usr_setting[0][1], usr_setting[0][2], usr_setting[0][3])
        else:
            if(already_warning_times > common_parameter.warning_limit):
                print("The number of warning is exceeded. %d, %d" %(already_warning_times, common_parameter.warning_limit))
                continue
            detect(content, prev_price, openid, common_parameter.premium_rate, common_parameter.warning_threshold, common_parameter.large_threshold)

    update_price(content)