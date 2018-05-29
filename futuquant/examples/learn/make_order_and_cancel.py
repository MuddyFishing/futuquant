# -*- coding: utf-8 -*-
"""
验证接口：下单然后立即撤单, 为避免成交损失，买单价格港股放在十档，美股为一档下降10%, 买单数量为1手（美股为1股）
"""
import os
import sys
from time import sleep

sys.path.append(os.path.split(os.path.abspath(os.path.pardir))[0])

import futuquant as ft


'''
  验证接口：下单然后立即撤单, 为避免成交损失，买单价格港股放在十档，美股为一档下降10%, 买单数量为1手（美股为1股）
  使用请先配置正确参数:
  api_svr_ip: (string)ip
  api_svr_port: (string)ip
  unlock_password: (string)交易解锁密码, 必需修改！！！
  test_code: (string)股票 'HK.xxxxx' or 'US.xxxx'
  trade_env:   ft.TrdEnv.SIMULATE or  ft.TrdEnv.REAL
'''


def make_order_and_cancel(api_svr_ip, api_svr_port, unlock_password, test_code, trade_env, acc_id):
    """
    使用请先配置正确参数:
    :param api_svr_ip: (string) ip
    :param api_svr_port: (string) ip
    :param unlock_password: (string) 交易解锁密码, 必需修改!
    :param test_code: (string) 股票
    :param trade_env:  参见 ft.TrdEnv的定义
    :param acc_id:  交易子账号id
    """
    if unlock_password == "":
        raise Exception("请先配置交易解锁密码!")

    quote_ctx = ft.OpenQuoteContext(host=api_svr_ip, port=api_svr_port)  # 创建行情api
    quote_ctx.subscribe(test_code, ft.SubType.ORDER_BOOK) # 定阅摆盘

    # 创建交易api
    is_hk_trade = 'HK.' in test_code
    if is_hk_trade:
        trade_ctx = ft.OpenHKTradeContext(host=api_svr_ip, port=api_svr_port)
    else:
        trade_ctx = ft.OpenUSTradeContext(host=api_svr_ip, port=api_svr_port)

    # 每手股数
    lot_size = 0
    is_unlock_trade = False
    is_fire_trade = False
    while not is_fire_trade:
        sleep(2)
        # 解锁交易
        if not is_unlock_trade:
            print("unlocking trade...")
            ret_code, ret_data = trade_ctx.unlock_trade(unlock_password)
            is_unlock_trade = (ret_code == ft.RET_OK)
            if not is_unlock_trade:
                print("请求交易解锁失败：{}".format(ret_data))
                break

        if lot_size == 0:
            print("get lotsize...")
            ret, data = quote_ctx.get_market_snapshot(test_code)
            lot_size = data.iloc[0]['lot_size'] if ret == ft.RET_OK else 0
            if ret != ft.RET_OK:
                print("取不到每手信息，重试中: {}".format(data))
                continue
            elif lot_size <= 0:
                raise BaseException("该股票每手信息错误，可能不支持交易 code ={}".format(test_code))

        print("get order book...")
        ret, data = quote_ctx.get_order_book(test_code)  # 得到第十档数据
        if ret != ft.RET_OK:
            continue

        # 计算交易价格
        bid_order_arr = data['Bid']
        if is_hk_trade:
            if len(bid_order_arr) != 10:
                continue
            # 港股下单: 价格定为第十档
            price, _, _ = bid_order_arr[9]
        else:
            if len(bid_order_arr) == 0:
                continue
            # 美股下单： 价格定为一档降10%
            price, _, _ = bid_order_arr[0]
            price = round(price * 0.9, 2)

        qty = lot_size

        # 价格和数量判断
        if qty == 0 or price == 0.0:
            continue

        # 下单
        order_id = 0
        print("place order : price={} qty={} code={}".format(price, qty, test_code))
        ret_code, ret_data = trade_ctx.place_order(price=price, qty=qty, code=test_code, trd_side=ft.TrdSide.BUY,
                                                   order_type=ft.OrderType.NORMAL, trd_env=trade_env, acc_id=acc_id)
        is_fire_trade = True
        print('下单ret={} data={}'.format(ret_code, ret_data))
        if ret_code == ft.RET_OK:
            row = ret_data.iloc[0]
            order_id = row['order_id']

        # 循环撤单
        sleep(2)


        if order_id:
            while True:
                ret_code, ret_data = trade_ctx.order_list_query(order_id=order_id, status_filter_list=[], code='',
                                                                start='', end='', trd_env=trade_env, acc_id=acc_id)

                if ret_code != ft.RET_OK:
                    sleep(2)
                    continue
                order_status = ret_data.iloc[0]['order_status']
                if order_status in [ft.OrderStatus.SUBMIT_FAILED, ft.OrderStatus.TIMEOUT, ft.OrderStatus.FILLED_ALL,
                                    ft.OrderStatus.FAILED, ft.OrderStatus.DELETED]:
                    break

                print("cancel order...")
                ret_code, ret_data = trade_ctx.modify_order(modify_order_op=ft.ModifyOrderOp.CANCEL, order_id=order_id,
                                price=price, qty=qty, adjust_limit=0, trd_env=trade_env, acc_id=acc_id)
                print("撤单ret={} data={}".format(ret_code, ret_data))
                if ret_code == ft.RET_OK:
                    break
                else:
                    sleep(2)
    # destroy object
    quote_ctx.close()
    trade_ctx.close()


if __name__ == "__main__":
    ip = '127.0.0.1'
    port = 11111
    unlock_pwd = "123456"       # 交易密码
    code = 'HK.69261'           # 'US.BABA' 'HK.00700'
    trd_env = ft.TrdEnv.REAL    # 交易环境：真实或模拟
    acc_id = 0                  # get_acc_list可查询交易子账号列表， 默认传0取列表中的第1个

    make_order_and_cancel(ip, port, unlock_pwd, code, trd_env, acc_id)
