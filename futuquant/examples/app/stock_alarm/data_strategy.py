# -*- coding: utf-8 -*-
from wx_push import WechatPush
import logging
from sqlite_interface import SqliteInterface
from Config import Config
import time

sqlite = SqliteInterface()
wp = WechatPush()
config = Config()
warning_time_list = {}


def detect_warning_times(openid, warning_limit):
    sent_msg_sig = 1
    now_time = time.time()
    result = None

    if openid in warning_time_list:
        result = warning_time_list[openid]

    new_time_list = ''
    cnt = 0
    if result:
        if result == '':  # 当warning_time_list为“”时
            pass
        else:
            time_list = result.split(',')
            first_flag = 1
            for tmp_time in time_list:
                if now_time - float(tmp_time) < 60:
                    if first_flag:
                        first_flag = 0
                    else:  # 如果不是第一个，就需要添加','符号
                        new_time_list += ','

                    new_time_list += str(tmp_time)
                    cnt += 1
        if cnt < warning_limit:
            if new_time_list == '':
                new_time_list = str(now_time)
            else:
                new_time_list = new_time_list + ',' + str(now_time)
        else:
            sent_msg_sig = 0
            print("The number of warning is exceeded. You set {1} times/min, "
                  "and has warned {0} times in the last 1 minutes.".format(cnt, warning_limit))
    else:
        new_time_list = str(now_time)

    warning_time_list.update({openid: new_time_list})
    print(now_time, warning_time_list[openid])
    return sent_msg_sig


def detect(content, prev_price, openid, premium_rate, warning_threshold, large_threshold, warning_limit):
    code = content['code']
    record_time = content['time']
    price = content['price']
    vol = content['volume']
    # direction = content[0]['ticker_direction']

    msg_list = []
    sent_msg_sig = 0
    # print(warning_threshold, large_threshold)

    if prev_price == 0:   # 之前数据库里无这股票的价格记录
        pass
    elif abs(price - prev_price) / prev_price - premium_rate > 1e-8:  # 越价, 小于1e-8视为相等
        # 检查成交量：
        if vol * price > warning_threshold:   # price * vol
            # print(vol * price, warning_threshold)
            sent_msg_sig = 1
            msg_list.append('异常成交提醒')
    elif vol * price > large_threshold:   # 单笔成交金额超过400万
        sent_msg_sig = 1
        msg_list.append('单笔大额成交')

    if sent_msg_sig:
        sent_msg_sig = detect_warning_times(openid, warning_limit)

    if sent_msg_sig:
        msg_list.append(code)
        msg_list.append(price)
        msg_list.append(vol * price)
        msg_list.append(vol)
        msg_list.append(record_time)
        msg_list.append('请及时查看，谢谢！')

        print(wp.send_template_msg(openid, msg_list))
        logging.info("Send a message.")

    print("* TickerTest\n", content)
    print("pre_price is {0}".format(prev_price))
    print("")


def get_preprice(content):
    code = content['code']
    prev_price = 0
    result = sqlite.get_values_by_id('price', 'stockid', code)
    if result:
        prev_price = result[0][1]
    return prev_price


def update_price(content):
    code = content['code']
    price = content['price']
    # 更新 逐笔成交信息
    sqlite.update_price(code, price)


def detect_and_send_each_ticker(content):
    prev_price = get_preprice(content)

    user_list = config.test_user_list
    for openid in user_list:
        usr_setting = sqlite.get_values_by_id('setting', 'openid', openid)
        if usr_setting:
            detect(content, prev_price, usr_setting[0][0], usr_setting[0][1], usr_setting[0][2], usr_setting[0][3],
                   usr_setting[0][4])
        else:
            detect(content, prev_price, openid, config.premium_rate, config.warning_threshold, config.large_threshold,
                   config.warning_limit)

    update_price(content)


def detect_and_send(content):
    for ticker in content:
        detect_and_send_each_ticker(ticker)
