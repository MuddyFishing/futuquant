#-*-coding:utf-8-*-

import futuquant

class GetGlobalState(object):
    # 获取牛牛程序全局状态 get_global_state

    def test1(self):
        quote_ctx = futuquant.OpenQuoteContext(host='127.0.0.1',port=11111)
        ret_code,state_dict = quote_ctx.get_global_state()

        print(ret_code)
        print(state_dict)
        quote_ctx.close()

if __name__ == '__main__':
    ggs = GetGlobalState()
    ggs.test1()