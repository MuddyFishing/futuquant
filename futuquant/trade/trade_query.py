# -*- coding: utf-8 -*-
"""
    Trade query
"""
import json
from futuquant.common.constant import *
from futuquant.common.utils import *
from futuquant.quote.quote_query import pack_pb_req


def is_HKTrade_order_status_finish(status):
    val = int(status)
    if val == 3 or val == 5 or val == 6 or val == 7:
        return True
    return False


def is_USTrade_order_status_finish(status):
    val = int(status)
    if val == 3 or val == 5 or val == 6 or val == 7:
        return True
    return False


class UnlockTrade:
    """Unlock trade limitation lock"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, cookie, password, password_md5):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Trd_UnlockTrade_pb2 import Request
        req = Request()
        req.c2s.unlock = True
        req.c2s.pwdMD5 = password_md5 if password_md5 != '' else md5_transform(
            password)

        return pack_pb_req(req, ProtoId.Trd_UnlockTrade)

    @classmethod
    def pack_lock_req(cls, cookie, password, password_md5):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Trd_UnlockTrade_pb2 import Request
        req = Request()
        req.c2s.unlock = False
        req.c2s.pwdMD5 = password_md5 if password_md5 != '' else md5_transform(
            password)

        return pack_pb_req(req, ProtoId.Trd_UnlockTrade)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, "", None


class PlaceOrder:
    """Palce order class"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype, orderside, ordertype, price, qty,
                    strcode, price_mode, adjust_limit):
        """Convert from user request for place order to PLS request"""
        if int(orderside) < 0 or int(orderside) > 1:
            error_str = ERROR_STR_PREFIX + "parameter orderside is wrong"
            return RET_ERROR, error_str, None

        if int(ordertype) is not 0 and int(ordertype) is not 1 and int(
                ordertype) is not 3:
            error_str = ERROR_STR_PREFIX + "parameter ordertype is wrong"
            return RET_ERROR, error_str, None

        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None
        from futuquant.common.pb.Trd_PlaceOrder_pb2 import Request
        req = Request()
        req.c2s.header.trdEnv = envtype
        req.c2s.header.accMarket = get_trd_market()
        req.c2s.header.accID = get_trd_accID()
        req.c2s.trdMarket = get_trd_market()
        req.c2s.trdSide = orderside
        req.c2s.orderType = ordertype
        req.c2s.code = strcode
        req.c2s.qty = qty
        req.c2s.price = price
        if price_mode != PriceRegularMode.IGNORE:
            req.c2s.adjustPrice = True
            req.c2s.adjustSideAndLimit = adjust_limit
        else:
            req.c2s.adjustPrice = False

        return pack_pb_req(req, ProtoId.Trd_PlaceOrder)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb, None
        order_id = rsp_pb.s2c.orderID

        return RET_OK, "", order_id

    @classmethod
    def us_pack_req(cls, cookie, envtype, orderside, ordertype, price, qty,
                    strcode, price_mode):
        """Convert from user request for trading days to PLS request"""
        if int(orderside) < 0 or int(orderside) > 1:
            error_str = ERROR_STR_PREFIX + "parameter orderside is wrong"
            return RET_ERROR, error_str, None

        if int(ordertype) is not 1 and int(ordertype) is not 2 \
                and int(ordertype) is not 51 and int(ordertype) is not 52:
            error_str = ERROR_STR_PREFIX + "parameter ordertype is wrong"
            return RET_ERROR, error_str, None

        req = {
            "Protocol": "7003",
            "Version": "1",
            "ReqParam": {
                "Cookie": cookie,
                "EnvType": envtype,
                "OrderSide": orderside,
                "OrderType": ordertype,
                "Price": price_to_str_int1000(price),
                "Qty": qty,
                "StockCode": strcode,
                "PriceMode": price_mode
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        place_order_list = [{
            'envtype':
            rsp_data['EnvType'],
            'orderid':
            rsp_data['OrderID'],
            "code":
            merge_stock_str(2, rsp_data['StockCode'])
            if 'StockCode' in rsp_data else '',
            "stock_name":
            rsp_data["StockName"] if 'StockName' in rsp_data else '',
            "dealt_avg_price":
            int1000_price_to_float(rsp_data['DealtAvgPrice'])
            if 'DealtAvgPrice' in rsp_data else None,
            "dealt_qty":
            rsp_data['DealtQty'] if 'DealtQty' in rsp_data else None,
            "qty":
            rsp_data['Qty'] if 'Qty' in rsp_data else None,
            "order_type":
            rsp_data['OrderType'] if 'OrderType' in rsp_data else None,
            "order_side":
            rsp_data['OrderSide'] if 'OrderSide' in rsp_data else None,
            "price":
            int1000_price_to_float(rsp_data['Price'])
            if 'Price' in rsp_data else None,
            "status":
            rsp_data['Status'] if 'Status' in rsp_data else None,
            "submited_time":
            rsp_data['SubmitedTime'] if 'SubmitedTime' in rsp_data else None,
            "updated_time":
            rsp_data['UpdatedTime'] if 'UpdatedTime' in rsp_data else None,
        }]

        return RET_OK, "", place_order_list


class GetAccountList:
    """Get the trade account list"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls):
        from futuquant.common.pb.Trd_GetAccList_pb2 import Request

        req = Request()
        req.c2s.userID = get_user_id()
        return pack_pb_req(req, ProtoId.Trd_GetAccList)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_acc_list = rsp_pb.s2c.accList
        acc_list = [{
            'acc_id': record.accID,
            'trd_env': record.trdEnv,
            'acc_market': QUOTE.REV_MKT_MAP[record.accMarket]
        } for record in raw_acc_list]

        return RET_OK, "", acc_list


class SetOrderStatus:
    """calss for setting status of order"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype, localid, orderid, status):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        if int(status) < 0 or int(status) > 3:
            error_str = ERROR_STR_PREFIX + "parameter status is wrong"
            return RET_ERROR, error_str, None

        req = {
            "Protocol": "6004",
            "Version": "1",
            "ReqParam": {
                "Cookie": cookie,
                "EnvType": envtype,
                "LocalID": localid,
                "OrderID": orderid,
                "SetOrderStatus": status,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        set_order_list = [{
            'envtype': rsp_data['EnvType'],
            'orderID': rsp_data['OrderID']
        }]

        return RET_OK, "", set_order_list

    @classmethod
    def us_pack_req(cls, cookie, envtype, localid, orderid, status):
        """Convert from user request for trading days to PLS request"""
        req = {
            "Protocol": "7004",
            "Version": "1",
            "ReqParam": {
                "Cookie": cookie,
                "EnvType": envtype,
                "LocalID": localid,
                "OrderID": orderid,
                "SetOrderStatus": status,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        set_order_list = [{
            'envtype': rsp_data['EnvType'],
            'orderID': rsp_data['OrderID']
        }]

        return RET_OK, "", set_order_list


class ChangeOrder:
    """Class for changing order"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype, localid, orderid, price, qty):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        req = {
            "Protocol": "6005",
            "Version": "1",
            "ReqParam": {
                "Cookie": cookie,
                "EnvType": envtype,
                "LocalID": localid,
                "OrderID": orderid,
                "Price": price_to_str_int1000(price),
                "Qty": qty,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        change_order_list = [{
            'envtype': rsp_data['EnvType'],
            'orderID': rsp_data['OrderID']
        }]

        return RET_OK, "", change_order_list

    @classmethod
    def us_pack_req(cls, cookie, envtype, localid, orderid, price, qty):
        """Convert from user request for trading days to PLS request"""
        req = {
            "Protocol": "7005",
            "Version": "1",
            "ReqParam": {
                "Cookie": cookie,
                "EnvType": envtype,
                "LocalID": localid,
                "OrderID": orderid,
                "Price": price_to_str_int1000(price),
                "Qty": qty,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'SvrResult' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find SvrResult in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None
        elif int(rsp_data['SvrResult']) != 0:
            error_str = ERROR_STR_PREFIX + rsp['ErrDesc']
            return RET_ERROR, error_str, None

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        if 'OrderID' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find OrderID in client rsp: %s" % rsp_str
            return RET_ERROR, error_str, None

        change_order_list = [{
            'envtype': rsp_data['EnvType'],
            'orderID': rsp_data['OrderID']
        }]

        return RET_OK, "", change_order_list


class AccInfoQuery:
    """Class for querying information of account"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Trd_GetFunds_pb2 import Request
        req = Request()
        req.c2s.header.accID = get_trd_accID()
        req.c2s.header.trdEnv = envtype
        req.c2s.header.accMarket = get_trd_market()

        return pack_pb_req(req, ProtoId.Trd_GetFunds)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_funds = rsp_pb.s2c.funds
        accinfo_list = [{
            'Power': raw_funds.gml,
            'ZCJZ': raw_funds.zcjz,
            'ZQSZ': raw_funds.zqsz,
            'XJJY': raw_funds.xj,
            'KQXJ': raw_funds.ktje,
            'DJZJ': raw_funds.djje,
            'ZSJE': 0,
            'ZGJDE': 9999,
            'YYJDE': 0,
            'GPBZJ': 0
        }]

        return RET_OK, "", accinfo_list

    @classmethod
    def us_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {
            "Protocol": "7007",
            "Version": "1",
            "ReqParam": {
                "Cookie": str(cookie),
                "EnvType": str(envtype),
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            return RET_ERROR, msg, None

        if 'Power' not in rsp_data or 'ZCJZ' not in rsp_data or 'ZQSZ' not in rsp_data or 'XJJY' not in rsp_data:
            return RET_ERROR, msg, None

        if 'KQXJ' not in rsp_data or 'DJZJ' not in rsp_data or 'ZSJE' not in rsp_data or 'ZGJDE' not in rsp_data:
            return RET_ERROR, msg, None

        if 'YYJDE' not in rsp_data or 'GPBZJ' not in rsp_data:
            return RET_ERROR, msg, None

        accinfo_list = [{
            'Power': int1000_price_to_float(rsp_data['Power']),
            'ZCJZ': int1000_price_to_float(rsp_data['ZCJZ']),
            'ZQSZ': int1000_price_to_float(rsp_data['ZQSZ']),
            'XJJY': int1000_price_to_float(rsp_data['XJJY']),
            'KQXJ': int1000_price_to_float(rsp_data['KQXJ']),
            'DJZJ': int1000_price_to_float(rsp_data['DJZJ']),
            'ZSJE': int1000_price_to_float(rsp_data['ZSJE']),
            'ZGJDE': int1000_price_to_float(rsp_data['ZGJDE']),
            'YYJDE': int1000_price_to_float(rsp_data['YYJDE']),
            'GPBZJ': int1000_price_to_float(rsp_data['GPBZJ'])
        }]

        return RET_OK, "", accinfo_list


class OrderListQuery:
    """Class for querying list queue"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, orderid, statusfilter, strcode, start, end,
                    envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Trd_GetOrderList_pb2 import Request
        req = Request()
        req.c2s.header.accID = get_trd_accID()
        req.c2s.header.accMarket = get_trd_market()
        req.c2s.header.trdEnv = envtype
        if strcode:
            req.c2s.filterConditions.code.append(strcode)
        if orderid:
            req.c2s.filterConditions.id.append(orderid)
        if start:
            req.c2s.filterConditions.beginTime = start
        if end:
            req.c2s.filterConditions.endTime = end
        if statusfilter:
            status_list = [int(x) for x in statusfilter.split(',')]
            for order_status in status_list:
                req.c2s.filterStatus.append(order_status)

        return pack_pb_req(req, ProtoId.Trd_GetOrderList)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_order_list = rsp_pb.s2c.orderList
        order_list = [{
            "code": order.code,
            "stock_name": order.name,
            "dealt_avg_price": order.fillAvgPrice,
            "dealt_qty": order.fillQty,
            "qty": order.qty,
            "orderid": order.orderID,
            "order_type": order.orderType,
            "order_side": order.trdSide,
            "price": order.price,
            "status": order.orderStatus,
            "submited_time": order.createTime,
            "updated_time": order.updateTime,
            "last_err_msg": order.lastErrMsg
        } for order in raw_order_list]
        return RET_OK, "", order_list

    @classmethod
    def us_pack_req(cls, cookie, orderid, statusfilter, strcode, start, end,
                    envtype):
        """Convert from user request for trading days to PLS request"""
        req = {
            "Protocol": "7008",
            "Version": "1",
            "ReqParam": {
                "Cookie": str(cookie),
                "EnvType": str(envtype),
                "OrderID": orderid,
                "StatusFilterStr": str(statusfilter),
                "StockCode": strcode,
                "start_time": start,
                "end_time": end,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USOrderArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USOrderArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_list = rsp_data["USOrderArr"]
        if raw_order_list is None or len(raw_order_list) == 0:
            return RET_OK, "", []

        order_list = [{
            "code":
            merge_stock_str(2, order['StockCode']),
            "dealt_avg_price":
            int1000_price_to_float(order['DealtAvgPrice']),
            "stock_name":
            order["StockName"],
            "dealt_qty":
            order['DealtQty'],
            "qty":
            order['Qty'],
            "orderid":
            order['OrderID'],
            "order_type":
            order['OrderType'],
            "order_side":
            order['OrderSide'],
            "price":
            int1000_price_to_float(order['Price']),
            "status":
            order['Status'],
            "submited_time":
            order['SubmitedTime'],
            "updated_time":
            order['UpdatedTime']
        } for order in raw_order_list]
        return RET_OK, "", order_list


class PositionListQuery:
    """Class for querying position list"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, strcode, stocktype, pl_ratio_min,
                    pl_ratio_max, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype or stocktype is wrong"
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Trd_GetPositionList_pb2 import Request
        req = Request()
        req.c2s.header.accID = get_trd_accID()
        req.c2s.header.trdEnv = int(envtype)
        req.c2s.header.accMarket = get_trd_market()
        if strcode:
            req.c2s.filterConditions.code.append(strcode)
        if pl_ratio_min:
            req.c2s.filterPLRatioMin = pl_ratio_min
        if pl_ratio_max:
            req.c2s.filterPLRatioMax = pl_ratio_max

        return pack_pb_req(req, ProtoId.Trd_GetPositionList)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_position_list = rsp_pb.s2c.positionList

        position_list = [{
            "code":
            position.code,
            "stock_name":
            position.StockName,
            "qty":
            position.qty,
            "can_sell_qty":
            position.canSellQty,
            "cost_price":
            position.costPrice if position.HasField('costPrice') else 0,
            "cost_price_valid":
            1 if position.HasField('costPrice') else 0,
            "market_val":
            position.val,
            "nominal_price":
            position.price,
            "pl_ratio":
            position.plRatio if position.HasField('plRatio') else 0,
            "pl_ratio_valid":
            1 if position.HasField('plRatio') else 0,
            "pl_val":
            position.td_plVal if position.HasField('plVal') else 0,
            "pl_val_valid":
            1 if position.HasField('plVal') else 0,
            "today_buy_qty":
            position.td_buyQty if position.HasField('td_buyQty') else 0,
            "today_buy_val":
            position.td_buyVal if position.HasField('td_buyVal') else 0,
            "today_pl_val":
            position.td_plVal if position.HasField('td_plVal') else 0,
            "today_sell_qty":
            position.td_sellQty if position.HasField('td_sellQty') else 0,
            "today_sell_val":
            position.td_sellVal if position.HasField('td_sellVal') else 0
        } for position in raw_position_list]
        return RET_OK, "", position_list

    @classmethod
    def us_pack_req(cls, cookie, strcode, stocktype, pl_ratio_min,
                    pl_ratio_max, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1 or (
                stocktype != '' and stocktype not in SEC_TYPE_MAP):
            error_str = ERROR_STR_PREFIX + "parameter envtype or stocktype is wrong"
            return RET_ERROR, error_str, None

        req = {
            "Protocol": "7009",
            "Version": "1",
            "ReqParam": {
                "Cookie":
                cookie,
                "StockCode":
                strcode,
                "StockType":
                str(SEC_TYPE_MAP[stocktype]) if not stocktype == '' else '',
                "PLRatioMin":
                price_to_str_int1000(pl_ratio_min),
                "PLRatioMax":
                price_to_str_int1000(pl_ratio_max),
                "EnvType":
                envtype,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USPositionArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USPositionArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_position_list = rsp_data["USPositionArr"]
        if raw_position_list is None or len(raw_position_list) == 0:
            return RET_OK, "", []

        position_list = [{
            "code":
            merge_stock_str(2, position['StockCode']),
            "stock_name":
            position["StockName"],
            "qty":
            position['Qty'],
            "can_sell_qty":
            position['CanSellQty'],
            "cost_price":
            int1000_price_to_float(position['CostPrice']),
            "cost_price_valid":
            position['CostPriceValid'],
            "market_val":
            int1000_price_to_float(position['MarketVal']),
            "nominal_price":
            int1000_price_to_float(position['NominalPrice']),
            "pl_ratio":
            int1000_price_to_float(position['PLRatio']),
            "pl_ratio_valid":
            position['PLRatioValid'],
            "pl_val":
            int1000_price_to_float(position['PLVal']),
            "pl_val_valid":
            position['PLValValid'],
            "today_buy_qty":
            position['Today_BuyQty'],
            "today_buy_val":
            int1000_price_to_float(position['Today_BuyVal']),
            "today_pl_val":
            int1000_price_to_float(position['Today_PLVal']),
            "today_sell_qty":
            position['Today_SellQty'],
            "today_sell_val":
            int1000_price_to_float(position['Today_SellVal'])
        } for position in raw_position_list]
        return RET_OK, "", position_list


class DealListQuery:
    """Class for """

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        if int(envtype) < 0 or int(envtype) > 1:
            error_str = ERROR_STR_PREFIX + "parameter envtype is wrong"
            return RET_ERROR, error_str, None
        from futuquant.common.pb.Trd_GetOrderFillList_pb2 import Request
        req = Request()
        req.c2s.header.accID = get_trd_accID()
        req.c2s.header.accMarket = get_trd_market()
        req.c2s.header.trdEnv = envtype

        return pack_pb_req(req, ProtoId.Trd_GetOrderFillList)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_deal_list = rsp_pb.s2c.orderFillList
        deal_list = [{
            "code":
            deal.code,
            "stock_name":
            deal.name,
            "dealid":
            deal.fillID,
            "orderid":
            deal.orderID if deal.HasField('orderID') else 0,
            "qty":
            deal.qty,
            "price":
            dael.price,
            "orderside":
            deal.trdSide,
            "time":
            deal.createTime,
            "order_side":
            deal.trdSide,
        } for deal in raw_deal_list]
        return RET_OK, "", deal_list

    @classmethod
    def us_pack_req(cls, cookie, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {
            "Protocol": "7010",
            "Version": "1",
            "ReqParam": {
                "Cookie": cookie,
                "EnvType": envtype,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USDealArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USDealArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_deal_list = rsp_data["USDealArr"]
        if raw_deal_list is None or len(raw_deal_list) == 0:
            return RET_OK, "", []

        deal_list = [{
            "code": merge_stock_str(2, deal['StockCode']),
            "stock_name": deal["StockName"],
            "dealid": deal['DealID'],
            "orderid": deal['OrderID'],
            "qty": deal['Qty'],
            "price": int1000_price_to_float(deal['Price']),
            "orderside": deal['OrderSide'],
            "time": deal['Time'],
            "order_side": deal['OrderSide'],
        } for deal in raw_deal_list]
        return RET_OK, "", deal_list


class TradePushQuery:
    """ Query Trade push info"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_subscribe_req(cls, cookie, envtype, orderid_list,
                              order_deal_push, push_at_once):
        """Pack the pushed response"""
        """By default subscribe all order in the given account ID"""
        from futuquant.common.pb.Trd_SubAccPush_pb2 import Request
        req = Request()
        req.c2s.accID.append(get_trd_accID())

        return pack_pb_req(req, ProtoId.Trd_SubAccPush)

    @classmethod
    def us_pack_subscribe_req(cls, cookie, envtype, orderid_list,
                              order_deal_push, push_at_once):
        """Pack the pushed response"""
        str_id = u''
        for orderid in orderid_list:
            if len(str_id) > 0:
                str_id += u','
            str_id += str(orderid)

        req = {
            "Protocol": "7100",
            "Version": "1",
            "ReqParam": {
                "Cookie": cookie,
                "EnvType": envtype,
                "OrderID": str_id,
                "SubOrder": order_deal_push,
                "SubDeal": order_deal_push,
                "FirstPush": push_at_once,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def hk_unpack_order_push_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_order_info = rsp_pb.s2c.order
        order_info = {
            "envtype": rsp_pb.s2c.header.trdEnv,
            "code": raw_order_info.code,
            "stock_name": raw_order_info.name,
            "dealt_avg_price": raw_order_info.fillAvgPrice,
            "dealt_qty": raw_order_info.fillQty,
            "qty": raw_order_info.qty,
            "orderid": raw_order_info.orderID,
            "order_type": raw_order_info.orderType,
            "order_side": raw_order_info.trdSide,
            "price": raw_order_info.price,
            "status": raw_order_info.orderStatus,
            "submited_time": raw_order_info.createTime,
            "updated_time": raw_order_info.updateTime
        }
        return RET_OK, "", order_info

    @classmethod
    def hk_unpack_deal_push_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_deal_info = rsp_pb.s2c.orderFill
        deal_info = {
            "envtype":
            rsp_pb.s2c.header.trdEnv,
            "code":
            raw_deal_info.code,
            "stock_name":
            raw_deal_info.name,
            "dealid":
            raw_deal_info.fillID,
            "orderid":
            raw_deal_info.orderID if raw_deal_info.HasField('orderID') else 0,
            "qty":
            raw_deal_info.qty,
            "price":
            raw_deal_info.price,
            "order_side":
            raw_deal_info.trdSide,
            "time":
            raw_deal_info.createTime,
            "contra_broker_id":
            raw_deal_info.counterBrokerID
            if raw_deal_info.HasField('counterBrokerID') else 0,
            "contra_broker_name":
            raw_deal_info.counterBrokerName
            if raw_deal_info.HasField('counterBrokerName') else ""
        }
        return RET_OK, "", deal_info

    @classmethod
    def us_unpack_order_push_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        order_info = {
            "envtype": int(rsp_data['EnvType']),
            "code": merge_stock_str(2, rsp_data['StockCode']),
            "stock_name": rsp_data["StockName"],
            "dealt_avg_price":
            int1000_price_to_float(rsp_data['DealtAvgPrice']),
            "dealt_qty": rsp_data['DealtQty'],
            "qty": rsp_data['Qty'],
            "orderid": rsp_data['OrderID'],
            "order_type": rsp_data['OrderType'],
            "order_side": rsp_data['OrderSide'],
            "price": int1000_price_to_float(rsp_data['Price']),
            "status": rsp_data['Status'],
            "submited_time": rsp_data['SubmitedTime'],
            "updated_time": rsp_data['UpdatedTime']
        }
        return RET_OK, "", order_info

    @classmethod
    def us_unpack_deal_push_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if 'EnvType' not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find EnvType in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        deal_info = {
            "envtype": int(rsp_data['EnvType']),
            "code": merge_stock_str(1, rsp_data['StockCode']),
            "stock_name": rsp_data["StockName"],
            "dealid": rsp_data['DealID'],
            "orderid": rsp_data['OrderID'],
            "qty": rsp_data['Qty'],
            "price": int1000_price_to_float(rsp_data['Price']),
            "order_side": rsp_data['OrderSide'],
            "time": rsp_data['Time']
        }
        return RET_OK, "", deal_info


class HistoryOrderListQuery:
    """Class for querying Histroy Order"""

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, statusfilter, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Trd_GetHistoryOrderList_pb2 import Request
        req = Request()
        req.c2s.header.accID = get_trd_accID()
        req.c2s.header.accMarket = get_trd_market()
        req.c2s.header.trdEnv = envtype
        if strcode:
            req.c2s.filterConditions.code.append(strcode)
        if start:
            req.c2s.filterConditions.beginTime = start
        if end:
            req.c2s.filterConditions.endTime = end

        return pack_pb_req(req, ProtoId.Trd_GetHistoryOrderList)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_order_list = rsp_pb.s2c.orderList
        order_list = [{
            "code":
            order.code,
            "stock_name":
            order.name,
            "dealt_qty":
            order.fillQty if order.HasField('fillQty') else 0,
            "qty":
            order.qty,
            "orderid":
            order.orderID,
            "order_type":
            order.orderType,
            "order_side":
            order.trdSide,
            "price":
            order.price if order.HasField('price') else 0,
            "status":
            order.orderStatus,
            "submited_time":
            order.createTime,
            "updated_time":
            order.updateTime
        } for order in raw_order_list]
        return RET_OK, "", order_list

    @classmethod
    def us_pack_req(cls, cookie, statusfilter, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {
            "Protocol": "7011",
            "Version": "1",
            "ReqParam": {
                "Cookie": str(cookie),
                "EnvType": str(envtype),
                "StatusFilterStr": str(statusfilter),
                "StockCode": strcode,
                "start_date": start,
                "end_date": end,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USOrderArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USOrderArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_order_list = rsp_data["USOrderArr"]
        if raw_order_list is None or len(raw_order_list) == 0:
            return RET_OK, "", []

        order_list = [{
            "code": merge_stock_str(2, order['StockCode']),
            "stock_name": order["StockName"],
            "dealt_qty": order['DealtQty'],
            "qty": order['Qty'],
            "orderid": order['OrderID'],
            "order_type": order['OrderType'],
            "order_side": order['OrderSide'],
            "price": int1000_price_to_float(order['Price']),
            "status": order['Status'],
            "submited_time": order['SubmitedTime'],
            "updated_time": order['UpdatedTime']
        } for order in raw_order_list]
        return RET_OK, "", order_list


class HistoryDealListQuery:
    """Class for """

    def __init__(self):
        pass

    @classmethod
    def hk_pack_req(cls, cookie, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Trd_GetHistoryOrderFillList_pb2 import Request
        req = Request()
        req.c2s.header.accID = get_trd_accID()
        req.c2s.header.accMarket = get_trd_market()
        req.c2s.header.trdEnv = envtype
        if strcode:
            req.c2s.filterConditions.code.append(strcode)
        if start:
            req.c2s.filterConditions.beginTime = start
        if end:
            req.c2s.filterConditions.endTime = end

        return pack_pb_req(req, ProtoId.Trd_GetHistoryOrderFillList)

    @classmethod
    def hk_unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_deal_list = rsp_pb.s2c.orderFillList

        deal_list = [{
            "code":
            deal.code,
            "stock_name":
            deal.name,
            "dealid":
            deal.fillID,
            "orderid":
            deal.orderID if deal.HasField('orderID') else 0,
            "qty":
            deal.qty,
            "price":
            deal.price,
            "time":
            deal.createTime,
            "order_side":
            deal.trdSide,
            "contra_broker_id":
            deal.counterBrokerID if deal.HasField('counterBrokerID') else 0,
            "contra_broker_name":
            deal.counterBrokerName
            if deal.HasField('counterBrokerName') else "",
        } for deal in raw_deal_list]
        return RET_OK, "", deal_list

    @classmethod
    def us_pack_req(cls, cookie, strcode, start, end, envtype):
        """Convert from user request for trading days to PLS request"""
        req = {
            "Protocol": "7012",
            "Version": "1",
            "ReqParam": {
                "Cookie": str(cookie),
                "EnvType": str(envtype),
                "StockCode": strcode,
                "start_date": start,
                "end_date": end,
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def us_unpack_rsp(cls, rsp_str):
        """Convert from PLS response to user response"""
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        if "USDealArr" not in rsp_data:
            error_str = ERROR_STR_PREFIX + "cannot find USDealArr in client rsp. Response: %s" % rsp_str
            return RET_ERROR, error_str, None

        raw_deal_list = rsp_data["USDealArr"]
        if raw_deal_list is None or len(raw_deal_list) == 0:
            return RET_OK, "", []

        deal_list = [{
            "code": merge_stock_str(2, deal['StockCode']),
            "stock_name": deal["StockName"],
            "dealid": deal['DealID'],
            "orderid": deal['OrderID'],
            "qty": deal['Qty'],
            "price": int1000_price_to_float(deal['Price']),
            "order_side": deal['OrderSide'],
            "time": deal['Time'],
        } for deal in raw_deal_list]
        return RET_OK, "", deal_list


class LoginNewAccountQuery:
    """
    LoginNewAccountQuery 切换牛牛号登陆
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, cookie, user_id, password_md5):
        # pack to json
        req = {
            "Protocol": "1037",
            "Version": "1",
            "ReqParam": {
                "Cookie": str(cookie),
                "UserID": user_id,
                "PasswordMD5": password_md5
            }
        }
        req_str = json.dumps(req) + '\r\n'
        return RET_OK, "", req_str

    @classmethod
    def unpack_rsp(cls, rsp_str):
        # response check and unpack response json to objects
        ret, msg, rsp = extract_pls_rsp(rsp_str)
        if ret != RET_OK:
            return RET_ERROR, msg, None

        rsp_data = rsp['RetData']

        return RET_OK, "", rsp_data
