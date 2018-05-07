# -*- coding: utf-8 -*-
"""
    Quote query
"""
import json
import sys
import struct
import time
from datetime import timedelta
from google.protobuf.json_format import MessageToJson
from futuquant.common.constant import *
from futuquant.common.utils import *
from futuquant.common.pb.Common_pb2 import RetType


class InitConnect:
    """
    A InitConnect request must be sent first
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, client_ver, client_id, recv_notify=False):
        """
        Send a init connection request to establish the connection btw gateway and client
        :param client_ver:
        :param client_id:
        :param recv_notify:
         :return: pb binary request data
        """
        from futuquant.common.pb.InitConnect_pb2 import Request
        req = Request()
        req.c2s.clientVer = client_ver
        req.c2s.clientID = client_id
        req.c2s.recvNotify = recv_notify
        return pack_pb_req(req, ProtoId.InitConnect)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Unpack the init connect response"""
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        res = {}
        if rsp_pb.HasField('s2c'):
            res['server_version'] = rsp_pb.s2c.serverVer
            res['login_user_id'] = rsp_pb.s2c.loginUserID
            res['conn_id'] = rsp_pb.s2c.connID
        else:
            return RET_ERROR, "rsp_pb error", None

        return RET_OK, "", res

class TradeDayQuery:
    """
    Query Conversion for getting trading days.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, start_date=None, end_date=None):
        """
        Convert from user request for trading days to PLS request
        :param market:
        :param start_date:
        :param end_date:
        :return: pb binary request data
        """

        # '''Parameter check'''
        if market not in MKT_MAP:
            error_str = ERROR_STR_PREFIX + " market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None

        if start_date is None:
            today = datetime.today()
            start = today - timedelta(days=365)

            start_date = start.strftime("%Y-%m-%d")
        else:
            ret, msg = check_date_str_format(start_date)
            if ret != RET_OK:
                return ret, msg, None
            start_date = normalize_date_format(start_date)

        if end_date is None:
            today = datetime.today()
            end_date = today.strftime("%Y-%m-%d")
        else:
            ret, msg = check_date_str_format(end_date)
            if ret != RET_OK:
                return ret, msg, None
            end_date = normalize_date_format(end_date)

        # pack to json
        mkt = MKT_MAP[market]
        from futuquant.common.pb.Qot_ReqTradeDate_pb2 import Request
        req = Request()
        req.c2s.market = mkt
        req.c2s.beginTime = start_date
        req.c2s.endTime = end_date

        return pack_pb_req(req, ProtoId.Qot_ReqTradeDate)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """
        Convert from PLS response to user response
        :return: trading day list

        Example:

        rsp_str : '{"ErrCode":"0","ErrDesc":"","Protocol":"1013","RetData":{"Market":"2",
        "TradeDateArr":["2017-01-17","2017-01-13","2017-01-12","2017-01-11",
        "2017-01-10","2017-01-09","2017-01-06","2017-01-05","2017-01-04",
        "2017-01-03"],"end_date":"2017-01-18","start_date":"2017-01-01"},"Version":"1"}\n\r\n\r\n'

         ret,msg,content = TradeDayQuery.unpack_rsp(rsp_str)

         ret : 0
         msg : ""
         content : ['2017-01-17',
                    '2017-01-13',
                    '2017-01-12',
                    '2017-01-11',
                    '2017-01-10',
                    '2017-01-09',
                    '2017-01-06',
                    '2017-01-05',
                    '2017-01-04',
                    '2017-01-03']

        """
        # response check and unpack response json to objects
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_trading_day_list = rsp_pb.s2c.tradeDate
        # convert to list format that we use
        trading_day_list = [x.time.split()[0] for x in raw_trading_day_list]

        return RET_OK, "", trading_day_list


class StockBasicInfoQuery:
    """
    Query Conversion for getting stock basic information.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, stock_type='STOCK'):
        """
        Convert from user request for trading days to PLS request
        :param market:
        :param stock_type:
        :return:  pb binary request data

        """
        if market not in MKT_MAP:
            error_str = ERROR_STR_PREFIX + " market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None

        if stock_type not in SEC_TYPE_MAP:
            error_str = ERROR_STR_PREFIX + " stock_type is %s, which is not valid. (%s)" \
                                           % (stock_type, ",".join([x for x in SEC_TYPE_MAP]))
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_ReqStockList_pb2 import Request
        req = Request()
        req.c2s.market = MKT_MAP[market]
        req.c2s.secType = SEC_TYPE_MAP[stock_type]

        return pack_pb_req(req, ProtoId.Qot_ReqStockList)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """
        Convert from PLS response to user response
        :return: (ret, msg , data)
            ret == 0, data = basic_info_list

        """
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_basic_info_list = rsp_pb.s2c.staticInfo

        basic_info_list = [{
            "code": merge_qot_mkt_stock_str(record.basic.stock.market,
                                            record.basic.stock.code),
            "stock_id": record.basic.id,
            "name": record.basic.name,
            "lot_size": record.basic.lotSize,
            "stock_type": QUOTE.REV_SEC_TYPE_MAP[record.basic.secType]
                if record.basic.secType in QUOTE.REV_SEC_TYPE_MAP else SecurityType.NONE,
            "stock_child_type": QUOTE.REV_WRT_TYPE_MAP[record.warrantExData.type]
                if record.warrantExData.type in QUOTE.REV_WRT_TYPE_MAP else WrtType.NONE,
            "stock_owner":merge_qot_mkt_stock_str(
                    record.warrantExData.ownerStock.market,
                    record.warrantExData.ownerStock.code) if record.HasField('warrantExData') else "",
            "listing_date": record.basic.listTime,
        } for record in raw_basic_info_list]
        return RET_OK, "", basic_info_list


class MarketSnapshotQuery:
    """
    Query Conversion for getting market snapshot.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """Convert from user request for trading days to PLS request"""
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_ReqStockSnapshot_pb2 import Request
        req = Request()
        for market, code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.market = market
            stock_inst.code = code

        return pack_pb_req(req, ProtoId.Qot_ReqStockSnapshot)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_snapshot_list = rsp_pb.s2c.snapshot
        snapshot_list = []
        for record in raw_snapshot_list:
            snapshot_tmp = {}
            snapshot_tmp['code'] = merge_qot_mkt_stock_str(
                int(record.basic.stock.market), record.basic.stock.code)
            snapshot_tmp['update_time'] = record.basic.updateTime
            snapshot_tmp['last_price'] = record.basic.curPrice
            snapshot_tmp['open_price'] = record.basic.openPrice
            snapshot_tmp['high_price'] = record.basic.highPrice
            snapshot_tmp['low_price'] = record.basic.lowPrice
            snapshot_tmp['prev_close_price'] = record.basic.lastClosePrice
            snapshot_tmp['volume'] = record.basic.volume
            snapshot_tmp['turnover'] = record.basic.turnover
            snapshot_tmp['turnover_rate'] = record.basic.turnoverRate
            snapshot_tmp['suspension'] = record.basic.isSuspend
            snapshot_tmp['listing_date'] = record.basic.listTime
            snapshot_tmp['price_spread'] = record.basic.priceSpread
            snapshot_tmp['lot_size'] = record.basic.lotSize

            # equityExData
            snapshot_tmp[
                'circular_market_val'] = record.equityExData.outstandingMktVal
            snapshot_tmp[
                'total_market_val'] = record.equityExData.issuedMktVal
            snapshot_tmp[
                'issued_shares'] = record.equityExData.issuedShares
            snapshot_tmp['net_asset'] = record.equityExData.netAsset
            snapshot_tmp['net_profit'] = record.equityExData.netProfit
            snapshot_tmp[
                'earning_per_share'] = record.equityExData.earningsPershare
            snapshot_tmp[
                'outstanding_shares'] = record.equityExData.outstandingShares
            snapshot_tmp[
                'net_asset_per_share'] = record.equityExData.netAssetPershare
            snapshot_tmp['ey_ratio'] = record.equityExData.eyRate
            snapshot_tmp['pe_ratio'] = record.equityExData.peRate
            snapshot_tmp['pb_ratio'] = record.equityExData.pbRate
            snapshot_tmp['wrt_valid'] = False

            if record.basic.type == SEC_TYPE_MAP[SecurityType.WARRANT]:
                snapshot_tmp['wrt_valid'] = True
                snapshot_tmp[
                    'wrt_conversion_ratio'] = record.warrantExData.conversionRate
                snapshot_tmp['wrt_type'] = QUOTE.REV_WRT_TYPE_MAP[
                    record.warrantExData.warrantType]
                snapshot_tmp[
                    'wrt_strike_price'] = record.warrantExData.strikePrice
                snapshot_tmp[
                    'wrt_maturity_date'] = record.warrantExData.maturityTime
                snapshot_tmp[
                    'wrt_end_trade'] = record.warrantExData.endTradeTime
                snapshot_tmp['wrt_code'] = merge_qot_mkt_stock_str(
                    record.warrantExData.ownerStock.market,
                    record.warrantExData.ownerStock.code)
                snapshot_tmp[
                    'wrt_recovery_price'] = record.warrantExData.recoveryPrice
                snapshot_tmp[
                    'wrt_street_vol'] = record.warrantExData.streetVolumn
                snapshot_tmp[
                    'wrt_issue_vol'] = record.warrantExData.issueVolumn
                snapshot_tmp[
                    'wrt_street_ratio'] = record.warrantExData.streetRate
                snapshot_tmp['wrt_delta'] = record.warrantExData.delta
                snapshot_tmp[
                    'wrt_implied_volatility'] = record.warrantExData.impliedVolatility
                snapshot_tmp['wrt_premium'] = record.warrantExData.premium
            else:
                pass
            snapshot_list.append(snapshot_tmp)

        return RET_OK, "", snapshot_list


class RtDataQuery:
    """
    Query Conversion for getting stock real-time data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(code)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        from futuquant.common.pb.Qot_ReqRT_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code

        return pack_pb_req(req, ProtoId.Qot_ReqRT)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        ret_type = rsp_pb.retType
        ret_msg = rsp_pb.retMsg

        if ret_type != RET_OK:
            return RET_ERROR, ret_msg, None

        raw_rt_data_list = rsp_pb.s2c.rt
        rt_list = [
            {
                "code": merge_qot_mkt_stock_str(rsp_pb.s2c.stock.market, rsp_pb.s2c.stock.code),
                "time": record.time,
                "is_blank":  True if record.isBlank else False,
                "opened_mins": record.minute,
                "cur_price": record.price,
                "last_close": record.lastClosePrice,
                "avg_price": record.avgPrice,
                "turnover": record.turnover,
                "volume": record.volume
            } for record in raw_rt_data_list
        ]
        return RET_OK, "", rt_list


class SubplateQuery:
    """
    Query Conversion for getting sub-plate stock list.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, market, plate_class):
        """Convert from user request for trading days to PLS request"""
        from futuquant.common.pb.Qot_ReqPlateSet_pb2 import Request
        req = Request()
        req.c2s.market = MKT_MAP[market]
        req.c2s.plateSetType = PLATE_CLASS_MAP[plate_class]

        return pack_pb_req(req, ProtoId.Qot_ReqPlateSet)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_plate_list = rsp_pb.s2c.plateInfo

        plate_list = [{
            "code": merge_qot_mkt_stock_str(record.plate.market, record.plate.code),
            "plate_name":
            record.name,
            "plate_id":
            record.plate.code
        } for record in raw_plate_list]

        return RET_OK, "", plate_list


class PlateStockQuery:
    """
    Query Conversion for getting all the stock list of a given plate.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, plate_code):
        """Convert from user request for trading days to PLS request"""
        ret_code, content = split_stock_str(plate_code)
        if ret_code != RET_OK:
            msg = content
            error_str = ERROR_STR_PREFIX + msg
            return RET_ERROR, error_str, None

        market, code = content
        if market not in QUOTE.REV_MKT_MAP:
            error_str = ERROR_STR_PREFIX + "market is %s, which is not valid. (%s)" \
                                           % (market, ",".join([x for x in MKT_MAP]))
            return RET_ERROR, error_str, None
        from futuquant.common.pb.Qot_ReqPlateStock_pb2 import Request
        req = Request()
        req.c2s.plate.market = market
        req.c2s.plate.code = code

        return pack_pb_req(req, ProtoId.Qot_ReqPlateStock)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_stock_list = rsp_pb.s2c.staticInfo

        stock_list = []
        for record in raw_stock_list:
            stock_tmp = {}
            stock_tmp['stock_id'] = record.basic.id
            stock_tmp['lot_size'] = record.basic.lotSize
            stock_tmp['code'] = merge_qot_mkt_stock_str(record.basic.stock.market, record.basic.stock.code)
            stock_tmp['stock_name'] = record.basic.name
            stock_tmp['stock_owner'] = merge_qot_mkt_stock_str(
                record.warrantExData.ownerStock.market,
                record.warrantExData.ownerStock.code) if record.HasField('warrantExData') else ""
            stock_tmp['list_time'] = record.basic.listTime
            stock_tmp['stock_child_type'] = QUOTE.REV_WRT_TYPE_MAP[
                record.warrantExData.type] if record.HasField('warrantExData') else ""
            stock_tmp['stock_type'] = QUOTE.REV_SEC_TYPE_MAP[record.basic.secType] if record.basic.secType in QUOTE.REV_SEC_TYPE_MAP else SecurityType.NONE
            stock_list.append(stock_tmp)

        return RET_OK, "", stock_list


class BrokerQueueQuery:
    """
    Query Conversion for getting broker queue information.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code):
        """Convert from user request for trading days to PLS request"""
        ret_code, content = split_stock_str(code)
        if ret_code == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market, code = content
        from futuquant.common.pb.Qot_ReqBroker_pb2 import Request
        req = Request()
        req.c2s.stock.market = market
        req.c2s.stock.code = code

        return pack_pb_req(req, ProtoId.Qot_ReqBroker)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_broker_bid = rsp_pb.s2c.brokerBid
        bid_list = []
        if raw_broker_bid is not None:
            bid_list = [{
                "bid_broker_id": record.id,
                "bid_broker_name": record.name,
                "bid_broker_pos": record.pos,
                "code": merge_qot_mkt_stock_str(rsp_pb.s2c.stock.market, rsp_pb.s2c.stock.code)
            } for record in raw_broker_bid]

        raw_broker_ask = rsp_pb.s2c.brokerAsk
        ask_list = []
        if raw_broker_ask is not None:
            ask_list = [{
                "ask_broker_id": record.id,
                "ask_broker_name": record.name,
                "ask_broker_pos": record.pos,
                "code": merge_qot_mkt_stock_str(rsp_pb.s2c.stock.market, rsp_pb.s2c.stock.code)
            } for record in raw_broker_ask]

        return RET_OK, bid_list, ask_list


class HistoryKlineQuery:
    """
    Query Conversion for getting historic Kline data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code, start_date, end_date, ktype, autype, fields,
                 max_num):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(code)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        # check date format
        if start_date is None:
            start_date = datetime.now().strftime('%Y-%m-%d')
        else:
            ret, msg = check_date_str_format(start_date)
            if ret != RET_OK:
                return ret, msg, None
            start_date = normalize_date_format(start_date)

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            ret, msg = check_date_str_format(end_date)
            if ret != RET_OK:
                return ret, msg, None
            end_date = normalize_date_format(end_date)

        # check k line type
        if ktype not in KTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in KTYPE_MAP]))
            return RET_ERROR, error_str, None

        if autype not in AUTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in AUTYPE_MAP]))
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_HistoryKL_pb2 import Request

        req = Request()
        req.c2s.rehabType = AUTYPE_MAP[autype]
        req.c2s.klType = KTYPE_MAP[ktype]
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code
        req.c2s.beginTime = start_date
        req.c2s.endTime = end_date
        req.c2s.maxAckKLNum = max_num
        req.c2s.needKLFieldsFlag = KL_FIELD.kl_fields_to_flag_val(fields)

        return pack_pb_req(req, ProtoId.Qot_ReqHistoryKL)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        has_next = False
        next_time = ""
        if rsp_pb.s2c.HasField('nextKLTime'):
            has_next = True
            next_time = rsp_pb.s2c.nextKLTime

        stock_code = merge_qot_mkt_stock_str(rsp_pb.s2c.stock.market,
                                     rsp_pb.s2c.stock.code)

        list_ret = []
        dict_data = {}
        raw_kline_list = rsp_pb.s2c.kl
        for record in raw_kline_list:
            dict_data['code'] = stock_code
            dict_data['time_key'] = record.time
            if record.isBlank:
                continue
            if record.HasField('openPrice'):
                dict_data['open'] = record.openPrice
            if record.HasField('highPrice'):
                dict_data['high'] = record.highPrice
            if record.HasField('lowPrice'):
                dict_data['low'] = record.lowPrice
            if record.HasField('closePrice'):
                dict_data['close'] = record.closePrice
            if record.HasField('volume'):
                dict_data['volume'] = record.volume
            if record.HasField('turnover'):
                dict_data['turnover'] = record.turnover
            if record.HasField('pe'):
                dict_data['pe_ratio'] = record.pe
            if record.HasField('turnoverRate'):
                dict_data['turnover_rate'] = record.turnoverRate
            if record.HasField('changeRate'):
                dict_data['change_rate'] = record.changeRate
            if record.HasField('lastClosePrice'):
                dict_data['last_close'] = record.lastClosePrice
            list_ret.append(dict_data.copy())

        return RET_OK, "", (list_ret, has_next, next_time)


class ExrightQuery:
    """
    Query Conversion for getting exclude-right information of stock.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """Convert from user request for trading days to PLS request"""
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue

            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None
        from futuquant.common.pb.Qot_ReqRehab_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.market = market_code
            stock_inst.code = stock_code

        return pack_pb_req(req, ProtoId.Qot_ReqRehab)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        class KLRehabFlag(object):
            SPLIT = 1
            JOIN = 2
            BONUS = 4
            TRANSFER = 8
            ALLOT = 16
            ADD = 32
            DIVIDED = 64
            SP_DIVIDED = 128

        raw_exr_list = rsp_pb.s2c.stockRehab
        exr_list = []
        for stock_rehab in raw_exr_list:
            code = merge_qot_mkt_stock_str(stock_rehab.stock.market,
                                        stock_rehab.stock.code)
            for rehab in stock_rehab.rehab:
                stock_rehab_tmp = {}
                stock_rehab_tmp['code'] = code
                stock_rehab_tmp['ex_div_date'] = rehab.time.split()[0]
                stock_rehab_tmp['forward_adj_factorA'] = rehab.fwdFactorA
                stock_rehab_tmp['forward_adj_factorB'] = rehab.fwdFactorB
                stock_rehab_tmp['backward_adj_factorA'] = rehab.bwdFactorA
                stock_rehab_tmp['backward_adj_factorB'] = rehab.bwdFactorB

                act_flag = rehab.companyActFlag
                if act_flag == 0:
                    continue

                if act_flag & KLRehabFlag.SP_DIVIDED:
                    stock_rehab_tmp['special_dividend'] = rehab.spDivident
                if act_flag & KLRehabFlag.DIVIDED:
                    stock_rehab_tmp['per_cash_div'] = rehab.dividend
                if act_flag & KLRehabFlag.ADD:
                    stock_rehab_tmp[
                        'stk_spo_ratio'] = rehab.addBase / rehab.addErt
                    stock_rehab_tmp['stk_spo_price'] = rehab.addPrice
                if act_flag & KLRehabFlag.ALLOT:
                    stock_rehab_tmp[
                        'allotment_ratio'] = rehab.allotBase / rehab.allotErt
                    stock_rehab_tmp['allotment_price'] = rehab.allotPrice
                if act_flag & KLRehabFlag.TRANSFER:
                    stock_rehab_tmp[
                        'per_share_trans_ratio'] = rehab.transferBase / rehab.transferErt
                if act_flag & KLRehabFlag.BONUS:
                    stock_rehab_tmp[
                        'per_share_div_ratio'] = rehab.bonusBase / rehab.bonusErt
                if act_flag & KLRehabFlag.JOIN:
                    stock_rehab_tmp[
                        'join_ratio'] = rehab.joinBase / rehab.joinErt
                if act_flag & KLRehabFlag.SPLIT:
                    stock_rehab_tmp[
                        'split_ratio'] = rehab.splitBase / rehab.splitErt
                exr_list.append(stock_rehab_tmp)

        return RET_OK, "", exr_list


class SubscriptionQuery:
    """
    Query Conversion for getting user's subscription information.
    """
    def __init__(self):
        pass

    @classmethod
    def pack_sub_or_unsub_req(cls, code_list, subtype_list, is_sub):

        stock_tuple_list = []
        for code in code_list:
            ret_code, content = split_stock_str(code)
            if ret_code != RET_OK:
                return ret_code, content, None
            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        from futuquant.common.pb.Qot_Sub_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.code = stock_code
            stock_inst.market = market_code
        for subtype in subtype_list:
            req.c2s.subType.append(SUBTYPE_MAP[subtype])
        req.c2s.isSubOrUnSub = is_sub

        return pack_pb_req(req, ProtoId.Qot_Sub)

    @classmethod
    def pack_subscribe_req(cls, code_list, subtype_list):
        return SubscriptionQuery.pack_sub_or_unsub_req(code_list, subtype_list, True)

    @classmethod
    def unpack_subscribe_rsp(cls, rsp_pb):
        """Unpack the subscribed response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, "", None

    @classmethod
    def pack_unsubscribe_req(cls, code_list, subtype_list):
        """Pack the un-subscribed request"""
        return SubscriptionQuery.pack_sub_or_unsub_req(code_list, subtype_list, False)

    @classmethod
    def unpack_unsubscribe_rsp(cls, rsp_pb):
        """Unpack the un-subscribed response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, "", None

    @classmethod
    def pack_subscription_query_req(cls, is_all_conn):
        """Pack the subscribed query request"""
        from futuquant.common.pb.Qot_ReqSubInfo_pb2 import Request
        req = Request()
        req.c2s.isReqAllConn = is_all_conn

        return pack_pb_req(req, ProtoId.Qot_ReqSubInfo)

    @classmethod
    def unpack_subscription_query_rsp(cls, rsp_pb):
        """Unpack the subscribed query response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None
        raw_sub_info = rsp_pb.s2c
        result = {}
        result['total_used'] = raw_sub_info.totalUsedQuota
        result['remain'] = raw_sub_info.remainQuota
        result['conn_sub_list'] = []
        for conn_sub_info in raw_sub_info.connSubInfo:
            conn_sub_info_tmp = {}
            conn_sub_info_tmp['used'] = conn_sub_info.usedQuota
            conn_sub_info_tmp['is_own_conn'] = conn_sub_info.isOwnConnData
            conn_sub_info_tmp['sub_list'] = []
            for sub_info in conn_sub_info.subInfo:
                sub_info_tmp = {}
                if sub_info.subType not in QUOTE.REV_SUBTYPE_MAP:
                    logger.error("error subtype:{}".format(sub_info.subType))
                    continue

                sub_info_tmp['subtype'] = QUOTE.REV_SUBTYPE_MAP[sub_info.subType]
                sub_info_tmp['code_list'] = []
                for stock in sub_info.stock:
                    sub_info_tmp['code_list'].append(merge_qot_mkt_stock_str(int(stock.market), stock.code),)

                conn_sub_info_tmp['sub_list'].append(sub_info_tmp)

            result['conn_sub_list'].append(conn_sub_info_tmp)

        return RET_OK, "", result

    @classmethod
    def pack_push_or_unpush_req(cls, code_list, subtype_list, is_push):
        stock_tuple_list = []
        for code in code_list:
            ret_code, content = split_stock_str(code)
            if ret_code != RET_OK:
                return ret_code, content, None
            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        from futuquant.common.pb.Qot_RegQotPush_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.code = stock_code
            stock_inst.market = market_code
        for subtype in subtype_list:
            req.c2s.subType.append(SUBTYPE_MAP[subtype])
        req.c2s.isRegOrUnReg = is_push

        return pack_pb_req(req, ProtoId.Qot_RegQotPush)

    @classmethod
    def pack_push_req(cls, code_list, subtype_list):
        """Pack the push request"""
        return SubscriptionQuery.pack_push_or_unpush_req(code_list, subtype_list, True)

    @classmethod
    def pack_unpush_req(cls, code_list, subtype_list):
        """Pack the un-pushed request"""
        return SubscriptionQuery.pack_push_or_unpush_req(code_list, subtype_list, False)


class StockQuoteQuery:
    """
    Query Conversion for getting stock quote data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, stock_list):
        """Convert from user request for trading days to PLS request"""
        stock_tuple_list = []
        failure_tuple_list = []
        for stock_str in stock_list:
            ret_code, content = split_stock_str(stock_str)
            if ret_code != RET_OK:
                msg = content
                error_str = ERROR_STR_PREFIX + msg
                failure_tuple_list.append((ret_code, error_str))
                continue
            market_code, stock_code = content
            stock_tuple_list.append((market_code, stock_code))

        if len(failure_tuple_list) > 0:
            error_str = '\n'.join([x[1] for x in failure_tuple_list])
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_ReqStockBasic_pb2 import Request
        req = Request()
        for market_code, stock_code in stock_tuple_list:
            stock_inst = req.c2s.stock.add()
            stock_inst.market = market_code
            stock_inst.code = stock_code

        return pack_pb_req(req, ProtoId.Qot_ReqStockBasic)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, []
        raw_quote_list = rsp_pb.s2c.stockBasic

        quote_list = [{
            'code': merge_qot_mkt_stock_str(int(record.stock.market), record.stock.code),
            'data_date': record.updateTime.split()[0],
            'data_time': record.updateTime.split()[1],
            'last_price': record.curPrice,
            'open_price': record.openPrice,
            'high_price': record.highPrice,
            'low_price': record.lowPrice,
            'prev_close_price': record.lastClosePrice,
            'volume': int(record.volume),
            'turnover': record.turnover,
            'turnover_rate': record.turnoverRate,
            'amplitude': record.amplitude,
            'suspension': record.isSuspended,
            'listing_date': record.listTime,
            'price_spread': record.priceSpread if record.HasField('priceSpread') else 0,
        } for record in raw_quote_list]

        return RET_OK, "", quote_list


class TickerQuery:
    """Stick ticker data query class"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code, num=500):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(code)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        if isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "num is %s of type %s, and the type shoud be %s" \
                                           % (num, str(type(num)), str(int))
            return RET_ERROR, error_str, None

        if num < 0:
            error_str = ERROR_STR_PREFIX + "num is %s, which is less than 0" % num
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        from futuquant.common.pb.Qot_ReqTicker_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code
        req.c2s.maxRetNum = num

        return pack_pb_req(req, ProtoId.Qot_ReqTicker)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        stock_code = merge_qot_mkt_stock_str(rsp_pb.s2c.stock.market,
                                     rsp_pb.s2c.stock.code)
        raw_ticker_list = rsp_pb.s2c.ticker
        ticker_list = [{
            "code": stock_code,
            "time": record.time,
            "price": record.price,
            "volume": record.volume,
            "turnover": record.turnover,
            "ticker_direction": str(QUOTE.REV_TICKER_DIRECTION[record.dir]) if record.dir in QUOTE.REV_TICKER_DIRECTION else "",
            "sequence": record.sequence,
        } for record in raw_ticker_list]
        return RET_OK, "", ticker_list


class CurKlineQuery:
    """Stock Kline data query class"""

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code, num, ktype, autype):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(code)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content

        if ktype not in KTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in KTYPE_MAP]))
            return RET_ERROR, error_str, None

        if autype not in AUTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in AUTYPE_MAP]))
            return RET_ERROR, error_str, None

        if isinstance(num, int) is False:
            error_str = ERROR_STR_PREFIX + "num is %s of type %s, which type should be %s" \
                                           % (num, str(type(num)), str(int))
            return RET_ERROR, error_str, None

        if num < 0:
            error_str = ERROR_STR_PREFIX + "num is %s, which is less than 0" % num
            return RET_ERROR, error_str, None
        from futuquant.common.pb.Qot_ReqKL_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code
        req.c2s.rehabType = AUTYPE_MAP[autype]
        req.c2s.reqNum = num
        req.c2s.klType = KTYPE_MAP[ktype]

        return pack_pb_req(req, ProtoId.Qot_ReqKL)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, []

        stock_code = merge_qot_mkt_stock_str(rsp_pb.s2c.stock.market,
                                     rsp_pb.s2c.stock.code)
        raw_kline_list = rsp_pb.s2c.rt
        kline_list = [{
            "code": stock_code,
            "time_key": record.time,
            "open": record.openPrice,
            "high": record.highPrice,
            "low": record.lowPrice,
            "close": record.closePrice,
            "volume": record.volume,
            "turnover": record.turnover,
            "pe_ratio": record.pe,
            "turnover_rate": record.turnoverRate,
            "last_close": record.lastClosePrice,
        } for record in raw_kline_list]

        return RET_OK, "", kline_list


class CurKlinePush:
    """Stock Kline data push class"""

    def __init__(self):
        pass

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, []

        if rsp_pb.s2c.rehabType != AUTYPE_MAP[AuType.QFQ]:
            return RET_ERROR, "kline push only support AuType.QFQ", None

        kl_type = QUOTE.REV_KTYPE_MAP[rsp_pb.s2c.klType] if rsp_pb.s2c.klType in QUOTE.REV_KTYPE_MAP else None
        if not kl_type:
            return RET_ERROR, "kline push error kltype", None

        stock_code = merge_qot_mkt_stock_str(rsp_pb.s2c.stock.market,
                                     rsp_pb.s2c.stock.code)
        raw_kline_list = rsp_pb.s2c.kl
        kline_list = [{
                          "k_type": kl_type,
                          "code": stock_code,
                          "time_key": record.time,
                          "open": record.openPrice,
                          "high": record.highPrice,
                          "low": record.lowPrice,
                          "close": record.closePrice,
                          "volume": record.volume,
                          "turnover": record.turnover,
                          "pe_ratio": record.pe,
                          "turnover_rate": record.turnoverRate,
                          "last_close": record.lastClosePrice,
                      } for record in raw_kline_list]

        return RET_OK, "", kline_list


class OrderBookQuery:
    """
    Query Conversion for getting stock order book data.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code):
        """Convert from user request for trading days to PLS request"""
        ret, content = split_stock_str(code)
        if ret == RET_ERROR:
            error_str = content
            return RET_ERROR, error_str, None

        market_code, stock_code = content
        from futuquant.common.pb.Qot_ReqOrderBook_pb2 import Request
        req = Request()
        req.c2s.stock.market = market_code
        req.c2s.stock.code = stock_code
        req.c2s.num = 10

        return pack_pb_req(req, ProtoId.Qot_ReqOrderBook)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, []

        raw_order_book_ask = rsp_pb.s2c.orderBookAsk
        raw_order_book_bid = rsp_pb.s2c.orderBookBid

        order_book = {}
        order_book['Bid'] = []
        order_book['Ask'] = []

        for record in raw_order_book_bid:
            order_book['Bid'].append((record.price, record.volume,
                                      record.orederCount))
        for record in raw_order_book_ask:
            order_book['Ask'].append((record.price, record.volume,
                                      record.orederCount))

        return RET_OK, "", order_book


class SuspensionQuery:
    """
    Query SuspensionQuery.
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code_list, start, end):
        """Convert from user request for trading days to PLS request"""
        list_req_stock = []
        for stock_str in code_list:
            ret, content = split_stock_str(stock_str)
            if ret == RET_ERROR:
                return RET_ERROR, content, None
            else:
                list_req_stock.append(content)
        '''
        for x in [start, end]:
            ret, msg = check_date_str_format(x)
            if ret != RET_OK:
                return ret, msg, None
        '''
        from futuquant.common.pb.Qot_ReqSuspend_pb2 import Request
        req = Request()
        if start:
            req.c2s.beginTime = start
        if end:
            req.c2s.endTime = end
        for market, code in list_req_stock:
            stock_inst = req.c2s.stock.add()
            stock_inst.market = market
            stock_inst.code = code

        return pack_pb_req(req, ProtoId.Qot_ReqSuspend)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        ret_susp_list = []
        for record in rsp_pb.s2c.stockSuspendList:
            suspend_info_tmp = {}
            code = merge_qot_mkt_stock_str(record.stock.market, record.stock.code)
            for suspend_info in record.suspendList:
                suspend_info_tmp['code'] = code
                suspend_info_tmp['suspension_dates'] = suspend_info.time
            ret_susp_list.append(suspend_info_tmp)

        return RET_OK, "", ret_susp_list


class GlobalStateQuery:
    """
    Query process "FTNN.exe" global state : market state & logined state
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls,user_id):
        """
        Convert from user request for trading days to PLS request
        :param state_type: for reserved, no use now !
        :return: pb binary request data

        """
        '''Parameter check'''

        # pack to json
        from futuquant.common.pb.GlobalState_pb2 import Request
        req = Request()
        req.c2s.userID = user_id
        return pack_pb_req(req, ProtoId.GlobalState)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """
        Convert from PLS response to user response

        Example:

        rsp_str : '{"ErrCode":"0","ErrDesc":"","Protocol":"1029","RetData":{"Market_HK":"5",
        "Market_HKFuture":"15","Market_SH":"6","Market_SZ":"6","Market_US":"11","Quote_Logined":"1","Trade_Logined":"1"
        },"Version":"1"}\r\n\r\n'

         ret,msg,content = TradeDayQuery.unpack_rsp(rsp_str)

         ret : 0
         msg : ""
         content : {"Market_HK":"5",
                    "Market_HKFuture":"15",
                    "Market_SH":"6",
                    "Market_SZ":"6",
                    "Market_US":"11",
                    "Quote_Logined":"1",
                    "Trade_Logined":"1"
                    "TimeStamp":"1508250058"
                   }

        """
        # response check and unpack response json to objects
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        raw_state = rsp_pb.s2c
        state_dict = {
            'Market_SZ': str(raw_state.marketSZ),
            'Version': str(raw_state.serverVer),
            'Trade_Logined': "1" if raw_state.trdLogined else "0",
            'TimeStamp': str(raw_state.time),
            'Market_US': str(raw_state.marketUS),
            'Quote_Logined': "1" if raw_state.qotLogined else "0",
            'Market_SH': str(raw_state.marketSH),
            'Market_HK': str(raw_state.marketHK),
            'Market_HKFuture': str(raw_state.marketHKFuture)
        }
        return RET_OK, "", state_dict


class HeartBeatPush:
    """
    HeartBeatPush  per 30 second
    """

    def __init__(self):
        pass

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """
        Convert from PLS response to user response

        """
        # response check and unpack response pb to objects
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        return RET_OK, '', rsp_pb.s2c.time


class SysNotifyPush:
    """ SysNotifyPush """
    def __init__(self):
        pass
    @classmethod
    def unpack_rsp(cls, rsp_pb):
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg,

        tmp_type = rsp_pb.s2c.type

        notify_type = SysNoitfy.REV_SYS_EVENT_TYPE_MAP[tmp_type] if tmp_type in SysNoitfy.REV_SYS_EVENT_TYPE_MAP else SysNotifyType.NONE
        sub_type = GtwEventType.NONE
        msg = ""
        if notify_type == SysNotifyType.GTW_EVENT:
            tmp_type = rsp_pb.s2c.event.eventType
            if tmp_type in SysNoitfy.REV_GTW_EVENT_MAP:
                sub_type = SysNoitfy.REV_GTW_EVENT_MAP[tmp_type]
            msg = rsp_pb.s2c.event.desc

        return RET_OK, (notify_type, sub_type, msg)


class MultiPointsHisKLine:
    """
    Query MultiPointsHisKLine
    """

    def __init__(self):
        pass

    @classmethod
    def pack_req(cls, code_list, dates, fields, ktype, autype, max_req,
                 no_data_mode):
        """Convert from user request for multiple history kline points to PLS request"""
        list_req_stock = []
        for code in code_list:
            ret, content = split_stock_str(code)
            if ret == RET_ERROR:
                return RET_ERROR, content, None
            else:
                list_req_stock.append(content)

        for x in dates:
            ret, msg = check_date_str_format(x)
            if ret != RET_OK:
                return ret, msg, None

        if ktype not in KTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "ktype is %s, which is not valid. (%s)" \
                                           % (ktype, ", ".join([x for x in KTYPE_MAP]))
            return RET_ERROR, error_str, None

        if autype not in AUTYPE_MAP:
            error_str = ERROR_STR_PREFIX + "autype is %s, which is not valid. (%s)" \
                                           % (autype, ", ".join([str(x) for x in AUTYPE_MAP]))
            return RET_ERROR, error_str, None

        from futuquant.common.pb.Qot_HistoryKLPoints_pb2 import Request
        req = Request()
        req.c2s.needKLFieldsFlag = KL_FIELD.kl_fields_to_flag_val(fields)
        req.c2s.rehabType = AUTYPE_MAP[autype]
        req.c2s.klType = KTYPE_MAP[ktype]
        req.c2s.noDataMode = no_data_mode
        req.c2s.maxReqStockNum = max_req
        for market_code, code in list_req_stock:
            stock_inst = req.c2s.stock.add()
            stock_inst.market = market_code
            stock_inst.code = code
        for date_ in dates:
            req.c2s.time.append(date_)

        return pack_pb_req(req, ProtoId.Qot_ReqHistoryKLPoints)

    @classmethod
    def unpack_rsp(cls, rsp_pb):
        """Convert from PLS response to user response"""
        if rsp_pb.retType != RET_OK:
            return RET_ERROR, rsp_pb.retMsg, None

        has_next = False
        has_next = rsp_pb.s2c.hasNext if rsp_pb.s2c.HasField(
            'hasNext') else False

        list_ret = []
        dict_data = {}
        raw_kline_points = rsp_pb.s2c.klPoints

        for raw_kline in raw_kline_points:
            code = merge_qot_mkt_stock_str(raw_kline.stock.market,
                                         raw_kline.stock.code)
            for raw_kl in raw_kline.kl:
                dict_data['code'] = code
                dict_data['time_point'] = raw_kl.reqTime
                dict_data['data_status'] = QUOTE.REV_KLDATA_STATUS_MAP[raw_kl.status] if raw_kl.status in QUOTE.REV_KLDATA_STATUS_MAP else KLDataStatus.NONE
                dict_data['time_key'] = raw_kl.kl.time

                dict_data['open'] = raw_kl.kl.openPrice if raw_kl.kl.HasField(
                    'openPrice') else 0
                dict_data['high'] = raw_kl.kl.highPrice if raw_kl.kl.HasField(
                    'highPrice') else 0
                dict_data['low'] = raw_kl.kl.lowPrice if raw_kl.kl.HasField(
                    'lowPrice') else 0
                dict_data[
                    'close'] = raw_kl.kl.closePrice if raw_kl.kl.HasField(
                        'closePrice') else 0
                dict_data['volume'] = raw_kl.kl.volume if raw_kl.kl.HasField(
                    'volume') else 0
                dict_data[
                    'turnover'] = raw_kl.kl.turnover if raw_kl.kl.HasField(
                        'turnover') else 0
                dict_data['pe_ratio'] = raw_kl.kl.pe if raw_kl.kl.HasField(
                    'pe') else 0
                dict_data[
                    'turnover_rate'] = raw_kl.kl.turnoverRate if raw_kl.kl.HasField(
                        'turnoverRate') else 0
                dict_data[
                    'change_rate'] = raw_kl.kl.changeRate if raw_kl.kl.HasField(
                        'changeRate') else 0
                dict_data[
                    'last_close'] = raw_kl.kl.lastClosePrice if raw_kl.kl.HasField(
                        'lastClosePrice') else 0

                list_ret.append(dict_data.copy())

        return RET_OK, "", (list_ret, has_next)
