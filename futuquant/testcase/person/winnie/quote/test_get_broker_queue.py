import time
from futuquant import *

class BrokerTest(BrokerHandlerBase):
        def on_recv_rsp(self, rsp_str):
                ret_code, data, content = super(BrokerTest,self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                        print("BrokerTest: error, msg: %s" % data)
                        return RET_ERROR, data

                print("BrokerTest ", content) # BrokerTest自己的处理逻辑

                return RET_OK, data


quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
quote_ctx.subscribe(['HK.00700'], SubType.BROKER)
ret_code, ret_data1, ret_data2 = quote_ctx.get_broker_queue('HK.00700')
print(ret_data1)
print(ret_data2)
# handler = BrokerTest()

# quote_ctx.set_handler(handler)
time.sleep(15)
quote_ctx.close()