import requests
class Config:
    def __init__(self):
        # wechat
        self.appid = 'wx7a25fbe5fc90799a'       # AppID
        self.secrect = 'f34624551ea8f5f784f2622378fe91f8'      # Secret
        # self.appid = 'wxbe3ec6c53ff67a31'
        # self.secrect = 'd8f141fe58642381bac82a6f0102ca10'

        # test_user_list
        self.test_user_list = {#'oaeaj0xqRf_m3l1Ln4FQ8rdoAvHc',  # ysq
                          #'oaeaj02eXJu9OuaiBtaHjNnvzv-Y',  # 享阝木木¹³¹¹ºº⁷⁷⁵⁵º
                          'oaeaj02DzklyZHavotk2X3mt6JuA'  # lpt
                          }

        # test_user_nickname
        self.test_user_nickname = {'lpt'}

        # wechat token
        self.token = 'yundun999'  # token

        # parameter: 越价率
        self.premium_rate = 0.005
        self.warning_threshold = 1000000
        self.large_threshold = 5000000
        self.warning_limit = 5

        # template_id
        self.template_id = "jr67sFJ5w4ln_ty6e0BHSBLZNOUOgMXOC-ph9u6xWwQ"

        # mysql
        # self.host = '127.0.0.1'
        # self.port = 3306
        # self.user = ''
        # self.passwd = ''
        # self.database = 'stock_alarm'

        # sqlite
        self.database = 'stock_alarm'

        # FutuOpenD
        self.host = '127.0.0.1'
        self.port = 11111


