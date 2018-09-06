from datetime import datetime
from futuquant import *
import collect_stock
import simple_logger
import sys
import signal
import pdb

log_tick = simple_logger.SimpleLogger('log/tick_{}.log'.format(datetime.now().date()))
log_price = simple_logger.SimpleLogger('log/price_{}.log'.format(datetime.now().date()))
log_obook = simple_logger.SimpleLogger('log/obook_{}.log'.format(datetime.now().date()))

quote_ctx = None
tick_count = 0

def on_signal(signum, tb):
    global quote_ctx
    # pdb.set_trace()
    logger.debug('signal: {}'.format(quote_ctx))
    if quote_ctx:
        logger.debug('close: {}'.format(quote_ctx))
        quote_ctx.close()
        quote_ctx = None
    log_tick.info('tick_count={}'.format(tick_count))
    log_tick.flush()

    log_price.flush()
    log_obook.flush()

    sys.exit(0)

signal.signal(signal.SIGINT, on_signal)
signal.signal(signal.SIGTERM, on_signal)


class TickHandlerReal(TickerHandlerBase):
    def __init__(self):
        super().__init__()

    def on_recv_rsp(self, rsp_pb):
        global tick_count
        ret, data = super().parse_rsp_pb(rsp_pb)

        if ret == RET_OK:
            tick_count += len(data)
        else:
            log_tick.warning(data)
            return ret, data

        for tick in data:
            self.handle_tick(tick)

        return ret, data

    def handle_tick(self, tick):
        code = tick['code']
        now = datetime.now().timestamp()
        opend_recv_time = tick['recv_timestamp']
        data_src_time = time.mktime(time.strptime(tick['time'], "%Y-%m-%d %H:%M:%S"))
        if 'US.' in code:
            data_src_time += 12 * 3600

        log_tick.info('{} {} {}'.format(now - opend_recv_time, opend_recv_time - data_src_time, now - data_src_time))
        # log_tick.flush()


class QuoteHandlerReal(StockQuoteHandlerBase):
    def __init__(self):
        super().__init__()

    def on_recv_rsp(self, rsp_pb):
        ret, data = super().parse_rsp_pb(rsp_pb)

        if ret != RET_OK:
            log_price.warning(data)
        else:
            for quote in data:
                self.handle_quote(quote)
        return ret, data

    def handle_quote(self, quote):
        code = quote['code']
        now = datetime.now().timestamp()
        opend_recv_time = quote['recv_timestamp']
        data_src_time = time.mktime(time.strptime(quote['date_time'], "%Y-%m-%d %H:%M:%S"))
        if 'US.' in code:
            data_src_time += 12 * 3600

        log_price.info('{} {} {}'.format(now - opend_recv_time, opend_recv_time - data_src_time, now - data_src_time))
        # log_price.flush()


class OBookHandlerReal(OrderBookHandlerBase):
    def __init__(self):
        super().__init__()

    def on_recv_rsp(self, rsp_pb):
        ret, data = super().parse_rsp_pb(rsp_pb)

        if ret != RET_OK:
            log_obook.warning(data)
        else:
            self.handle_obook(data)

        return ret, data

    def handle_obook(self, obook):

        now = datetime.now().timestamp()
        opend_recv_time = obook['recv_timestamp']

        log_obook.info('{}'.format(now - opend_recv_time))
        # log_obook.flush()


def test_tick():
    global quote_ctx
    codes = collect_stock.load_stock_code('stock-hk.csv')

    ip = '127.0.0.1'
    port = 11111
    quote_ctx = OpenQuoteContext(ip, port)

    ret, data = quote_ctx.get_global_state()
    if ret != RET_OK:
        return

    lastLocalSvrTimeDiff = data['lastLocalSvrTimeDiff']
    str_diff = 'lastLocalSvrTimeDiff={}'.format(lastLocalSvrTimeDiff)
    log_tick.info(str_diff)
    log_tick.flush()

    log_price.info(str_diff)
    log_price.flush()

    log_obook.info(str_diff)
    log_obook.flush()

    quote_ctx.set_handler(TickHandlerReal())
    quote_ctx.set_handler(QuoteHandlerReal())
    quote_ctx.set_handler(OBookHandlerReal())
    quote_ctx.start()

    code_sub = codes[:100]
    # code_sub.append('HK_FUTURE.999010')
    print(quote_ctx.subscribe(code_sub, [SubType.TICKER, SubType.QUOTE, SubType.ORDER_BOOK], False))


if __name__ == "__main__":

    test_tick()
    while True:
        time.sleep(0.2)

