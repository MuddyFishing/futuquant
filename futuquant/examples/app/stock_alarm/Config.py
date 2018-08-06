class Config:
    # wechat
    appid = 'wx7a25fbe5fc90799a'       # AppID
    secrect = 'f34624551ea8f5f784f2622378fe91f8'      # Secret

    # test_user_list
    test_user_list = {#'oaeaj0xqRf_m3l1Ln4FQ8rdoAvHc',  # ysq
                      #'oaeaj02eXJu9OuaiBtaHjNnvzv-Y',  # 享阝木木¹³¹¹ºº⁷⁷⁵⁵º
                      'oaeaj02DzklyZHavotk2X3mt6JuA'  # lpt
                      }

    # test_user_nickname
    test_user_nickname = {'lpt'}

    # wechat token
    token = 'yundun999'  # token

    # parameter: 越价率，
    premium_rate = 0.005
    warning_threshold = 1000000
    large_threshold = 5000000
    warning_limit = 5

    # template_id
    template_id = "jr67sFJ5w4ln_ty6e0BHSBLZNOUOgMXOC-ph9u6xWwQ"

    # mysql
    host = '127.0.0.1'
    port = 3306
    user = 'root'
    passwd = 'hackch'
    database = 'stock_alarm'