# -*- coding: utf-8 -*-

import pandas as pd
from futuquant.common.open_context_base import OpenContextBase
from futuquant.common.utils import *
from futuquant.trade.order_list_manager import SafeTradeSubscribeList
from futuquant.trade.trade_query import *
from futuquant.quote.response_handler import HKTradeOrderPreHandler


class OpenHKTradeContext(OpenContextBase):
    """Class for set context of HK stock trade"""
    cookie = 100000

    def __init__(self, host="127.0.0.1", port=11111):
        self._ctx_unlock = None
        self._obj_order_sub = SafeTradeSubscribeList()

        super(OpenHKTradeContext, self).__init__(host, port, True, True)
        self.set_pre_handler(HKTradeOrderPreHandler(self))

    def close(self):
        """
        to call close old obj before loop create new, otherwise socket will encounter erro 10053 or more!
        """
        super(OpenHKTradeContext, self).close()

    def on_api_socket_reconnected(self):
        """for API socket reconnected"""
        # auto unlock
        if self._ctx_unlock is not None:
            for i in range(3):
                password, password_md5 = self._ctx_unlock
                ret, data = self.unlock_trade(password, password_md5)
                if ret == RET_OK:
                    break
                sleep(1)

        # auto subscribe order deal push
        list_sub = self._obj_order_sub.copy()
        dic_order = {}
        list_zero_order_env = []
        for (orderid, envtype) in list_sub:
            if str(orderid) == u'':
                list_zero_order_env.append(envtype)
                continue
            if envtype not in dic_order:
                dic_order[envtype] = []
            dic_order[envtype].append(orderid)

        for envtype in dic_order:
            self._subscribe_order_deal_push(dic_order[envtype], True, True,
                                            envtype)

        # use orderid blank to subscrible all order
        for envtype in list_zero_order_env:
            self._subscribe_order_deal_push([], True, False, envtype)

    def on_trade_order_check(self, orderid, envtype, status):
        '''multi thread notify order finish after subscribe order push'''
        if is_HKTrade_order_status_finish(status):
            self._obj_order_sub.del_val(orderid=orderid, envtype=envtype)
        elif (not self._obj_order_sub.has_val(
                orderid, envtype)) and self._obj_order_sub.has_val(
                    u'', envtype):
            self._obj_order_sub.add_val(
                orderid, envtype)  #record info for subscribe order u''

    def _subscribe_order_deal_push(self,
                                   orderid_list,
                                   order_deal_push=True,
                                   push_atonce=True,
                                   envtype=0):
        """subscribe order for recv push data"""
        for orderid in orderid_list:
            if order_deal_push is False:
                self._obj_order_sub.del_val(orderid, envtype)
            else:
                self._obj_order_sub.add_val(orderid, envtype)

        ret_code, _, push_req_str = TradePushQuery.hk_pack_subscribe_req(
            str(self.cookie), str(envtype), orderid_list,
            str(int(order_deal_push)), str(int(push_atonce)))
        if ret_code == RET_OK:
            ret_code, _ = self._send_async_req(push_req_str)

        return ret_code

    def unlock_trade(self, password, password_md5=None):
        '''
        交易解锁，安全考虑，所有的交易api,需成功解锁后才可操作
        :param password: 明文密码字符串 (二选一）
        :param password_md5: 密码的md5字符串（二选一）
        :return:(ret, data) ret == 0 时, data为None
                            ret != 0 时， data为错误字符串
        '''
        query_processor = self._get_sync_query_processor(
            UnlockTrade.pack_req, UnlockTrade.unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'password': str(password) if password else '',
            'password_md5': str(password_md5) if password_md5 else ''
        }

        ret_code, msg, unlock_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        # reconnected to auto unlock
        if RET_OK == ret_code:
            self._ctx_unlock = (password, password_md5)

            # unlock push socket
            ret_code, msg, push_req_str = UnlockTrade.pack_req(**kargs)
            if ret_code == RET_OK:
                self._send_async_req(push_req_str)

        return RET_OK, None

    def lock_trade(self, password, password_md5=None):
        '''
        交易锁定
        :param password: 明文密码字符串 (二选一）
        :param password_md5: 密码的md5字符串（二选一）
        :return:(ret, data) ret == 0 时, data为None
                            ret != 0 时， data为错误字符串
        '''
        query_processor = self._get_sync_query_processor(
            UnlockTrade.pack_lock_req, UnlockTrade.unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'password': str(password) if password else '',
            'password_md5': str(password_md5) if password_md5 else ''
        }

        ret_code, msg, unlock_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        # reconnected to auto unlock
        if RET_OK == ret_code:
            self._ctx_unlock = (password, password_md5)

            # unlock push socket
            ret_code, msg, push_req_str = UnlockTrade.pack_req(**kargs)
            if ret_code == RET_OK:
                self._send_async_req(push_req_str)

        return RET_OK, None

    def subscribe_order_deal_push(self,
                                  orderid_list,
                                  order_deal_push=True,
                                  envtype=0):
        """
        subscribe_order_deal_push
        """
        if not TRADE.check_envtype_hk(envtype):
            return RET_ERROR

        list_sub = [u'']
        if orderid_list is None:
            list_sub = [u'']
        elif isinstance(orderid_list, list):
            list_sub = [str(x) for x in orderid_list]
        else:
            list_sub = [str(orderid_list)]

        return self._subscribe_order_deal_push(list_sub, order_deal_push, True,
                                               envtype)

    def place_order(self,
                    price,
                    qty,
                    strcode,
                    orderside,
                    ordertype=0,
                    envtype=0,
                    order_deal_push=False,
                    price_mode=PriceRegularMode.IGNORE,
                    adjust_limit=0):
        """
        place order
        use  set_handle(HKTradeOrderHandlerBase) to recv order push !
        """
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        ret_code, content = split_stock_str(str(strcode))
        if ret_code == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        if int(market_code) != 1:
            error_str = ERROR_STR_PREFIX + "the type of stocks is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            PlaceOrder.hk_pack_req, PlaceOrder.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'envtype': str(envtype),
            'orderside': str(orderside),
            'ordertype': str(ordertype),
            'price': str(price),
            'qty': str(qty),
            'strcode': str(stock_code),
            'price_mode': str(price_mode),
            'adjust_limit': adjust_limit
        }

        ret_code, msg, order_id = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        # handle order push
        self._subscribe_order_deal_push(
            orderid_list=[order_id],
            order_deal_push=order_deal_push,
            envtype=envtype)

        col_list = [
            "envtype", "orderid", "code", "stock_name", "dealt_avg_price",
            "dealt_qty", "qty", "order_type", "order_side", "price", "status",
            "submited_time", "updated_time"
        ]
        order_pd = self.order_list_query(orderid=order_id, envtype=envtype)
        place_order_list = [{
            'envtype':
            envtype,
            'orderid':
            order_id,
            'code':
            strcode,
            'stock_name':
            order_pd.at[0, 'stock_name'],
            'dealt_avg_price':
            order_pd.at[0, 'dealt_avg_price'],
            'dealt_qty':
            order_pd.at[0, 'dealt_qty'],
            'qty':
            qty,
            'order_type':
            ordertype,
            'order_side':
            orderside,
            'price':
            price,
            'status':
            order_pd.at[0, 'status'],
            'submited_time':
            order_pd.at[0, 'submited_time'],
            'updated_time':
            order_pd.at[0, 'updated_time']
        }]

        place_order_table = pd.DataFrame(place_order_list, columns=col_list)

        return RET_OK, place_order_table

    def set_order_status(self, status, orderid=0, envtype=0):
        """for setting the status of order"""
        if int(status) not in TRADE.REV_ORDER_STATUS:
            error_str = ERROR_STR_PREFIX + "the type of status is wrong "
            return RET_ERROR, error_str

        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            SetOrderStatus.hk_pack_req, SetOrderStatus.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'envtype': str(envtype),
            'localid': str(0),
            'orderid': str(orderid),
            'status': str(status)
        }

        ret_code, msg, set_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['envtype', 'orderID']
        set_order_table = pd.DataFrame(set_order_list, columns=col_list)

        return RET_OK, set_order_table

    def change_order(self, price, qty, orderid=0, envtype=0):
        """for changing the order"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            ChangeOrder.hk_pack_req, ChangeOrder.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'envtype': str(envtype),
            'localid': str(0),
            'orderid': str(orderid),
            'price': str(price),
            'qty': str(qty)
        }

        ret_code, msg, change_order_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ['envtype', 'orderID']
        change_order_table = pd.DataFrame(change_order_list, columns=col_list)

        return RET_OK, change_order_table

    def get_accinfo(self):
        """
        query account information
        :param envtype: trading environment parameters,0 means real transaction and 1 means simulation trading
        :return:error return RET_ERROR,msg and ok return RET_OK,ret
        """
        query_processor = self._get_sync_query_processor(
            GetAccountList.hk_pack_req, GetAccountList.hk_unpack_rsp)

        ret_code, msg, acc_list = query_processor()
        logger.debug(acc_list)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = ["acc_id", "trd_env", "acc_market"]

        acc_table = pd.DataFrame(acc_list, columns=col_list)

        return RET_OK, acc_table

    def accinfo_query(self, envtype=0):
        """
        query account information
        :param envtype: trading environment parameters,0 means real transaction and 1 means simulation trading
        :return:error return RET_ERROR,msg and ok return RET_OK,ret
        """
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            AccInfoQuery.hk_pack_req, AccInfoQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': envtype}

        ret_code, msg, accinfo_list = query_processor(**kargs)
        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = [
            'Power', 'ZCJZ', 'ZQSZ', 'XJJY', 'KQXJ', 'DJZJ', 'ZSJE', 'ZGJDE',
            'YYJDE', 'GPBZJ'
        ]
        accinfo_frame_table = pd.DataFrame(accinfo_list, columns=col_list)

        return RET_OK, accinfo_frame_table

    def order_list_query(self,
                         orderid="",
                         statusfilter="",
                         strcode='',
                         start='',
                         end='',
                         envtype=0):
        """for querying the order list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(
            OrderListQuery.hk_pack_req, OrderListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'orderid': str(orderid),
            'statusfilter': str(statusfilter),
            'strcode': str(stock_code),
            'start': str(start),
            'end': str(end),
            'envtype': str(envtype)
        }
        ret_code, msg, order_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = [
            "code", "stock_name", "dealt_avg_price", "dealt_qty", "qty",
            "orderid", "order_type", "order_side", "price", "status",
            "submited_time", "updated_time", "last_err_msg"
        ]

        order_list_table = pd.DataFrame(order_list, columns=col_list)

        return RET_OK, order_list_table

    def position_list_query(self,
                            strcode='',
                            stocktype='',
                            pl_ratio_min='',
                            pl_ratio_max='',
                            envtype=0):
        """for querying the position list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(
            PositionListQuery.hk_pack_req, PositionListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'strcode': str(stock_code),
            'stocktype': str(stocktype),
            'pl_ratio_min': str(pl_ratio_min),
            'pl_ratio_max': str(pl_ratio_max),
            'envtype': str(envtype)
        }
        ret_code, msg, position_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = [
            "code", "stock_name", "qty", "can_sell_qty", "cost_price",
            "cost_price_valid", "market_val", "nominal_price", "pl_ratio",
            "pl_ratio_valid", "pl_val", "pl_val_valid", "today_buy_qty",
            "today_buy_val", "today_pl_val", "today_sell_qty", "today_sell_val"
        ]

        position_list_table = pd.DataFrame(position_list, columns=col_list)

        return RET_OK, position_list_table

    def deal_list_query(self, envtype=0):
        """for querying deal list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        query_processor = self._get_sync_query_processor(
            DealListQuery.hk_pack_req, DealListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {'cookie': str(self.cookie), 'envtype': str(envtype)}
        ret_code, msg, deal_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        # "orderside" 保留是为了兼容旧版本, 对外文档统一为"order_side"
        col_list = [
            "code", "stock_name", "dealid", "orderid", "qty", "price",
            "orderside", "time", "order_side"
        ]

        deal_list_table = pd.DataFrame(deal_list, columns=col_list)

        return RET_OK, deal_list_table

    def history_order_list_query(self,
                                 statusfilter='',
                                 strcode='',
                                 start='',
                                 end='',
                                 envtype=0):
        """for querying the order list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(
            HistoryOrderListQuery.hk_pack_req,
            HistoryOrderListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'statusfilter': str(statusfilter),
            'strcode': str(stock_code),
            'start': str(start),
            'end': str(end),
            'envtype': str(envtype)
        }
        ret_code, msg, order_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = [
            "code", "stock_name", "dealt_qty", "qty", "orderid", "order_type",
            "order_side", "price", "status", "submited_time", "updated_time"
        ]

        order_list_table = pd.DataFrame(order_list, columns=col_list)

        return RET_OK, order_list_table

    def history_deal_list_query(self, strcode, start, end, envtype=0):
        """for querying deal list"""
        if not TRADE.check_envtype_hk(envtype):
            error_str = ERROR_STR_PREFIX + "the type of environment param is wrong "
            return RET_ERROR, error_str

        stock_code = ''
        if strcode != '':
            ret_code, content = split_stock_str(str(strcode))
            if ret_code == RET_ERROR:
                return RET_ERROR, content
            _, stock_code = content

        query_processor = self._get_sync_query_processor(
            HistoryDealListQuery.hk_pack_req,
            HistoryDealListQuery.hk_unpack_rsp)

        # the keys of kargs should be corresponding to the actual function arguments
        kargs = {
            'cookie': str(self.cookie),
            'strcode': str(stock_code),
            'start': str(start),
            'end': str(end),
            'envtype': str(envtype)
        }

        ret_code, msg, deal_list = query_processor(**kargs)

        if ret_code != RET_OK:
            return RET_ERROR, msg

        col_list = [
            "code", "stock_name", "dealid", "orderid", "qty", "price",
            "order_side", "time", "contra_broker_id", "contra_broker_name"
        ]

        deal_list_table = pd.DataFrame(deal_list, columns=col_list)

        return RET_OK, deal_list_table

    def login_new_account(self,
                          user_id,
                          login_password_md5,
                          trade_password,
                          trade_password_md5=None):
        '''
        自动登陆一个新的牛牛帐号
        :param user_id: 牛牛号
        :param login_password_md5: 新帐号的登陆密码的md5值
        :param trade_password: 新帐号的交易密码
        :param trade_password_md5: 新帐号的交易密码的md5值 (跟交易密码二选一)
        :return:
        '''
        query_processor = self._get_sync_query_processor(
            LoginNewAccountQuery.pack_req, LoginNewAccountQuery.unpack_rsp)

        kargs = {
            'cookie': str(self.cookie),
            'user_id': str(user_id),
            'password_md5': str(login_password_md5)
        }

        # 切换帐号，必然会断线，故判断ret_code 无意义
        try:
            query_processor(**kargs)
        except Exception as e:
            pass

        # 触发重连等待
        self.get_global_state()

        # 接下来就是解锁交易密码
        ret = RET_OK
        data = ''
        if trade_password or trade_password_md5:
            ret, data = self.unlock_trade(trade_password, trade_password_md5)
        else:
            self._ctx_unlock = None

        return ret, data
