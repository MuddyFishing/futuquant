
from futuquant import *
from futuquant.examples.app.shock_alarm.wx_push import wechat_push
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
wp = wechat_push()

prev_price = {}


def detect(content):
    global prev_price
    code = content[0]['code']
    time = content[0]['time']
    price = content[0]['price']
    vol = content[0]['volume']
    direction = content[0]['ticker_direction']

    msg = {}
    sent_msg_sig = 0
    if prev_price[code] == 0.0:   # 首次成交
        pass
    elif price - prev_price[code] > 0.5:
        # 检查成交量：
        if int(vol) * price > 1000000:   # price * vol
            sent_msg_sig = 1
            msg.update({'echo_type': 'Warning'})
    elif int(vol) * price > 4000000:   # 单笔成交金额超过400万
        sent_msg_sig = 1
        msg.update({'echo_type': '单笔大额成交'})

    if(sent_msg_sig):
        msg.update({'code':str(code), 'direction': str(direction), 'prev_price': str(prev_price[code]), 'price': str(price), 'total_deal_price':str(int(vol)*price/10000), 'time': str(time)})

        wp.send_msg(msg)
        logging.info("Send a message.")

    # 更新逐笔
    prev_price[code] = price

class TickerTest(TickerHandlerBase):
    """ 获取逐笔推送数据 """
    def on_recv_rsp(self, rsp_pb):
        """数据响应回调函数"""
        ret_code, content = super(TickerTest, self).parse_rsp_pb(rsp_pb)
        if ret_code != RET_OK:
            print("* TickerTest: error, msg: %s" % content)
            return RET_ERROR, content
        # print("* TickerTest\n", content)
        detect(content)
        return RET_OK, content

def quote_test(code_list, host, port):
    quote_ctx = OpenQuoteContext(host, port)
    print("Server lim.app:%s connected..." % port)
    # 设置异步回调接口
    quote_ctx.set_handler(TickerTest())
    quote_ctx.start()

    quote_ctx.subscribe(code_list, SubType.TICKER)
    print(quote_ctx.query_subscription())


host='127.0.0.1'
port=11111
subtype_list = [SubType.QUOTE, SubType.ORDER_BOOK, SubType.TICKER, SubType.K_DAY, SubType.RT_DATA, SubType.BROKER]
code_list = ['HK.00700', 'HK.00388', 'HK_FUTURE.999010']
big_sub_codes = ['HK.02318', 'HK.02828', 'HK.00939', 'HK.01093', 'HK.01299', 'HK.00175',
                 'HK.01299', 'HK.01833', 'HK.00005', 'HK.00883', 'HK.00388', 'HK.01398',
                 'HK.01114', 'HK.02800', 'HK.02018', 'HK.03988', 'HK.00386', 'HK.01211',
                 'HK.00857', 'HK.01177',  'HK.02601', 'HK.02628', 'HK_FUTURE.999010']
for code in big_sub_codes:
    prev_price[code] = 0.0
quote_test(big_sub_codes, host, port)