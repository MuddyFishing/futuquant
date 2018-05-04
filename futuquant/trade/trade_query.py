# -*- coding: utf-8 -*-
"""
    Trade query
"""
import datetime as dt
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


class GetAccountList:
    """Get the trade account list"""
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, user_id):
        from futuquant.common.pb.Trd_GetAccList_pb2 import Request

        req = Request()
        req.c2s.userID = user_id
        return pack_pb_req(req, ProtoId.Trd_GetAccList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_acc_list = rsp_pb.s2c.accList
        acc_list = [{
            'acc_id': record.accID,
            'trd_env': TRADE.REV_ENVTYPE_MAP[record.trdEnv] if record.trdEnv in TRADE.REV_ENVTYPE_MAP else "",
            'trdMarket_list': [(TRADE.REV_TRD_MKT_MAP[trdMkt] if trdMkt in TRADE.REV_TRD_MKT_MAP else TrdMarket.NONE) for trdMkt in record.trdMarketAuth]
        } for record in raw_acc_list]

        return RET_OK, "", acc_list


class UnlockTrade:
    """Unlock trade limitation lock"""
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, is_unlock, password_md5):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Trd_UnlockTrade_pb2 import Request
        req = Request()
        req.c2s.unlock = is_unlock
        req.c2s.pwdMD5 = password_md5

        return pack_pb_req(req, ProtoId.Trd_UnlockTrade)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, "", None


class SubAccPush:
    """sub acc push"""
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, acc_id):
        from futuquant.common.pb.Trd_SubAccPush_pb2 import Request
        req = Request()
        req.c2s.accID = acc_id

        return pack_pb_req(req, ProtoId.Trd_SubAccPush)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, "", None


class AccInfoQuery:
    """Class for querying information of account"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, acc_id, trd_market, trd_env):
        from futuquant.common.pb.Trd_GetFunds_pb2 import Request
        req = Request()
        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_market]

        return pack_pb_req(req, ProtoId.Trd_GetFunds)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
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
        }]
        return RET_OK, "", accinfo_list


class PositionListQuery:
    """Class for querying position list"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, strcode, pl_ratio_min,
                 pl_ratio_max, trd_env, acc_id, trd_mkt):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Trd_GetPositionList_pb2 import Request
        req = Request()
        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_mkt]
        if strcode:
            req.c2s.filterConditions.code.append(strcode)
        if pl_ratio_min:
            req.c2s.filterPLRatioMin = float(pl_ratio_min) / 100.0
        if pl_ratio_max:
            req.c2s.filterPLRatioMax = float(pl_ratio_max) / 100.0

        return pack_pb_req(req, ProtoId.Trd_GetPositionList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_position_list = rsp_pb.s2c.positionList

        position_list = [{
                             "code": merge_trd_mkt_stock_str(rsp_pb.s2c.header.trdMarket, position.code),
                             "stock_name": position.name,
                             "qty": position.qty,
                             "can_sell_qty": position.canSellQty,
                             "cost_price": position.costPrice if position.HasField('costPrice') else 0,
                             "cost_price_valid": 1 if position.HasField('costPrice') else 0,
                             "market_val": position.val,
                             "nominal_price": position.price,
                             "pl_ratio": 100 * position.plRatio if position.HasField('plRatio') else 0,
                             "pl_ratio_valid": 1 if position.HasField('plRatio') else 0,
                             "pl_val": position.td_plVal if position.HasField('plVal') else 0,
                             "pl_val_valid": 1 if position.HasField('plVal') else 0,
                             "today_buy_qty": position.td_buyQty if position.HasField('td_buyQty') else 0,
                             "today_buy_val": position.td_buyVal if position.HasField('td_buyVal') else 0,
                             "today_pl_val": position.td_plVal if position.HasField('td_plVal') else 0,
                             "today_sell_qty": position.td_sellQty if position.HasField('td_sellQty') else 0,
                             "today_sell_val": position.td_sellVal if position.HasField('td_sellVal') else 0,
                             "position_side": TRADE.REV_POSITION_SIDE_MAP[position.positionSide]
                                if position.positionSide in TRADE.REV_POSITION_SIDE_MAP else PositionSide.NONE,
                         } for position in raw_position_list]
        return RET_OK, "", position_list


class OrderListQuery:
    """Class for querying list queue"""
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, order_id, status_filter_list, strcode, start, end,
                 trd_env, acc_id, trd_mkt):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Trd_GetOrderList_pb2 import Request
        req = Request()
        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_mkt]

        if strcode:
            req.c2s.filterConditions.code.append(strcode)
        if order_id:
            req.c2s.filterConditions.id.append(int(order_id))

        if start:
            req.c2s.filterConditions.beginTime = start
        if end:
            req.c2s.filterConditions.endTime = end

        if len(status_filter_list):
            for order_status in status_filter_list:
                req.c2s.filterStatus.append(ORDER_STATUS_MAP[order_status])

        return pack_pb_req(req, ProtoId.Trd_GetOrderList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_order_list = rsp_pb.s2c.orderList
        order_list = [{
            "code": merge_trd_mkt_stock_str(rsp_pb.s2c.header.trdMarket, order.code),
            "stock_name": order.name,
            "trd_side": TRADE.REV_TRD_SIDE_MAP[order.trdSide] if order.trdSide in TRADE.REV_TRD_SIDE_MAP else TrdSide.NONE,
            "order_type": TRADE.REV_ORDER_TYPE_MAP[order.orderType] if order.orderType in TRADE.REV_ORDER_TYPE_MAP else OrderType.NONE,
            "order_status": TRADE.REV_ORDER_STATUS_MAP[order.orderStatus] if order.orderStatus in TRADE.REV_ORDER_STATUS_MAP else OrderStatus.NONE,
            "order_id": str(order.orderID),
            "qty": order.qty,
            "price": order.price,
            "create_time": order.createTime,
            "updated_time": order.updateTime,
            "dealt_qty": order.fillQty,
            "dealt_avg_price": order.fillAvgPrice,
            "last_err_msg": order.lastErrMsg
        } for order in raw_order_list]
        return RET_OK, "", order_list


class PlaceOrder:
    """Palce order class"""
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, conn_id, trd_side, order_type, price, qty,
                    strcode, adjust_limit, trd_env, acc_id, trd_mkt):
        """Convert from user request for place order to PLS request"""
        from futuquant.common.pb.Trd_PlaceOrder_pb2 import Request
        req = Request()
        serial_no = get_unique_id32()
        req.c2s.packetID.serialNo = serial_no
        req.c2s.packetID.connID = conn_id

        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_mkt]

        req.c2s.trdSide = TRD_SIDE_MAP[trd_side]
        req.c2s.orderType = ORDER_TYPE_MAP[order_type]
        req.c2s.code = strcode
        req.c2s.qty = qty
        req.c2s.price = price
        req.c2s.adjustPrice = adjust_limit != 0
        req.c2s.adjustSideAndLimit = adjust_limit

        return pack_pb_req(req, ProtoId.Trd_PlaceOrder, serial_no)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb, None
        order_id = rsp_pb.s2c.orderID

        return RET_OK, "", str(order_id)


class ModifyOrder:
    """modify order class"""
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, modify_order_op, order_id, price, qty,
                 adjust_limit, trd_env, acc_id, trd_mkt, conn_id):
        """Convert from user request for place order to PLS request"""
        from futuquant.common.pb.Trd_ModifyOrder_pb2 import Request
        req = Request()
        serial_no = get_unique_id32()
        req.c2s.packetID.serialNo = serial_no
        req.c2s.packetID.connID = conn_id

        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_mkt]

        req.c2s.orderID = int(order_id)
        req.c2s.modifyOrderOp = MODIFY_ORDER_OP_MAP[modify_order_op]
        req.c2s.forAll = False

        if modify_order_op == ModifyOrderOp.NORMAL:
            req.c2s.qty = qty
            req.c2s.price = price
            req.c2s.adjustPrice = adjust_limit != 0
            req.c2s.adjustSideAndLimit = adjust_limit

        return pack_pb_req(req, ProtoId.Trd_ModifyOrder, serial_no)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        order_id = rsp_pb.s2c.orderID
        modify_order_list = [{
            'trd_env': TRADE.REV_TRD_MKT_MAP[rsp_pb.s2c.header.trdEnv],
            'order_id': str(order_id)
        }]

        return RET_OK, "", modify_order_list


class DealListQuery:
    """Class for """
    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, strcode, trd_env, acc_id, trd_mkt):
        """Convert from user request for place order to PLS request"""
        from futuquant.common.pb.Trd_GetOrderFillList_pb2 import Request
        req = Request()
        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_mkt]

        if strcode:
            req.c2s.filterConditions.code.append(strcode)

        return pack_pb_req(req, ProtoId.Trd_GetOrderFillList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_deal_list = rsp_pb.s2c.orderFillList
        deal_list = [{
            "code": merge_trd_mkt_stock_str(rsp_pb.s2c.header.trdMarket, deal.code),
            "stock_name": deal.name,
            "deal_id": deal.fillID,
            "order_id": deal.orderID if deal.HasField('orderID') else 0,
            "qty": deal.qty,
            "price": deal.price,
            "trd_side": TRADE.REV_TRD_SIDE_MAP[deal.trdSide] if dael.trdSide in TRADE.REV_TRD_SIDE_MAP else TrdSide.NONE,
            "create_time": deal.createTime,
            "counter_broker_id": deal.counterBrokerID,
            "counter_broker_name": deal.counterBrokerName,
        } for deal in raw_deal_list]

        return RET_OK, "", deal_list



class HistoryOrderListQuery:
    """Class for querying Histroy Order"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, status_filter_list, strcode, start, end,
                 trd_env, acc_id, trd_mkt):

        from futuquant.common.pb.Trd_GetHistoryOrderList_pb2 import Request
        req = Request()
        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_mkt]

        if strcode:
            req.c2s.filterConditions.code.append(strcode)

        req.c2s.filterConditions.beginTime = start
        req.c2s.filterConditions.endTime = end

        if status_filter_list:
            for order_status in status_filter_list:
                req.c2s.filterStatus.append(ORDER_STATUS_MAP[order_status])

        return pack_pb_req(req, ProtoId.Trd_GetHistoryOrderList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):

        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_order_list = rsp_pb.s2c.orderList
        order_list = [{
                      "code": merge_trd_mkt_stock_str(rsp_pb.s2c.header.trdMarket, order.code),
                      "stock_name": order.name,
                      "trd_side": TRADE.REV_TRD_SIDE_MAP[order.trdSide] if order.trdSide in TRADE.REV_TRD_SIDE_MAP else TrdSide.NONE,
                      "order_type": TRADE.REV_ORDER_TYPE_MAP[order.orderType] if order.orderType in TRADE.REV_ORDER_TYPE_MAP else OrderType.NONE,
                      "order_status": TRADE.REV_ORDER_STATUS_MAP[order.orderStatus] if order.orderStatus in TRADE.REV_ORDER_STATUS_MAP else OrderStatus.NONE,
                      "order_id": str(order.orderID),
                      "qty": order.qty,
                      "price": order.price,
                      "create_time": order.createTime,
                      "updated_time": order.updateTime,
                      "dealt_qty": order.fillQty,
                      "dealt_avg_price": order.fillAvgPrice,
                      "last_err_msg": order.lastErrMsg
                      } for order in raw_order_list]
        return RET_OK, "", order_list



class HistoryDealListQuery:
    """Class for """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, strcode, start, end, trd_env, acc_id, trd_mkt):

        from futuquant.common.pb.Trd_GetHistoryOrderFillList_pb2 import Request
        req = Request()
        req.c2s.header.trdEnv = TRD_ENV_MAP[trd_env]
        req.c2s.header.accID = acc_id
        req.c2s.header.trdMarket = TRD_MKT_MAP[trd_mkt]

        if strcode:
            req.c2s.filterConditions.code.append(strcode)

        req.c2s.filterConditions.beginTime = start
        req.c2s.filterConditions.endTime = end

        return pack_pb_req(req, ProtoId.Trd_GetHistoryOrderFillList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):

        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_deal_list = rsp_pb.s2c.orderFillList
        deal_list = [{
                    "code": merge_trd_mkt_stock_str(rsp_pb.s2c.header.trdMarket, deal.code),
                    "stock_name": deal.name,
                    "deal_id": deal.fillID,
                    "order_id": deal.orderID if deal.HasField('orderID') else 0,
                    "qty": deal.qty,
                    "price": deal.price,
                    "trd_side": TRADE.REV_TRD_SIDE_MAP[deal.trdSide] if deal.trdSide in TRADE.REV_TRD_SIDE_MAP else TrdSide.NONE,
                    "create_time": deal.createTime,
                    "counter_broker_id": deal.counterBrokerID,
                    "counter_broker_name": deal.counterBrokerName
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

