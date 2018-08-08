from .mysql_interface import MysqlInterface

myopenid = "kdhfskgadfvbsdvkjgkaghsdzfkigv_dgfjsdzfvbjazsgdcfvgh"

# setting table
p1 = 0.005
p2 = 1000000.0
p3 = 4000000.0
p4 = 4
stockid = ""
user_setting = '设置' + ' ' + str(p1) + ' ' + str(p2) + ' ' + str(p3) + ' ' + str(p4)
mi = MysqlInterface()
mi.mysql_connect()
mi.create_table_setting()
print("setting table generated, and test:")
mi.update_threshold(myopenid, user_setting)
mi.print_setting_table()
mi.delete_user_setting(myopenid)
mi.print_setting_table()
mi.get_setting_by_openid(myopenid)

# price table
mi = MysqlInterface()
mi.create_table_price()
print("price table generated, and test:")
mi.update_price("test", 12.1)
print(mi.get_preprice_by_stockid("test"))
result = mi.get_preprice_by_stockid("tes")
if not result:
    print("None")
else:
    print(result)
mi.delete_price("test")

# 最近一分钟warning_time_list这个表
mi.create_table_warning_list()
print("warning_list table generated.")