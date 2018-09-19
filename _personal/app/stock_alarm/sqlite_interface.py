# -*- coding: utf-8 -*-
import re
from Config import Config
import sqlite3

config = Config()

class SqliteInterface:
    def __init__(self):
        self.database = config.database + '.db'
        conn = sqlite3.connect(self.database)  # 创建sqlite.db数据库
        print("open database success")
        self.create_table_setting()
        self.create_table_price()
        print("Table created successfully")

    # setting 表
    def create_table_setting(self):
        conn = sqlite3.connect(self.database)  # 创建数据库
        query = """CREATE TABLE IF NOT EXISTS setting(
                    openid VARCHAR(100) PRIMARY KEY,
                    premium_rate DOUBLE,
                    warning_threshold DOUBLE,
                    single_deal_threshold DOUBLE,
                    warning_limit INT
                );"""
        conn.execute(query)
        conn.close()
        print("Table {0} is ready".format('setting'))

    def update_setting(self, open_id, parameter_list):
        conn = sqlite3.connect(self.database)
        statement = "INSERT OR REPLACE INTO {0} VALUES(?,?,?,?,?)".format('setting')
        data = [(open_id, parameter_list[0], parameter_list[1], parameter_list[2], parameter_list[3])]
        conn.executemany(statement, data)
        conn.commit()

    # price 表
    def create_table_price(self):
        conn = sqlite3.connect(self.database)  # 创建数据库
        query = """CREATE TABLE IF NOT EXISTS price(stockid VARCHAR(25) PRIMARY KEY, preprice DOUBLE)"""
        conn.execute(query)
        conn.close()
        print("Table {0} is ready".format('price'))

    def update_price(self, stock_id, price):
        conn = sqlite3.connect(self.database)
        statement = "INSERT OR REPLACE INTO {0} VALUES(?,?)".format('price')
        data = [(stock_id, price)]
        conn.executemany(statement, data)
        conn.commit()

    # 通用
    def print_table(self, table_name):
        conn = sqlite3.connect(self.database)
        sql = "select * from {0}".format(table_name)
        curson = conn.execute(sql)
        conn.commit()
        rows = curson.fetchall()
        print(rows)

        conn.close()

    def delete_table(self, table_name):
        conn = sqlite3.connect(self.database)
        sql = "drop table IF EXISTS {0}".format(table_name)
        conn.execute(sql)
        conn.close()

    def get_values_by_id(self, table_name, id_name, id_value):
        con = sqlite3.connect(self.database)
        cur = con.cursor()
        cur.execute('select * from {0} where {1} = "{2}"'.format(table_name, id_name, id_value))
        results = cur.fetchall()
        con.close()
        return results

    def change_tuple_to_string(self, parameter_tuple):
        res = ''
        # change tuple to string
        length = len(parameter_tuple)
        res = ''
        for i in range(1, length - 1):
            res += str(parameter_tuple[i]) + "  "
        res += str(parameter_tuple[length - 1])
        return res

    def check_setting_parameter(self, openid, content):
        parameter_list = re.split(r" +", content)
        if len(parameter_list) < 5:
            return False, "参数数量不足，需要的参数分别为：\n越价率，越价+大单的大单阈值，单笔大单阈值，一分钟内的预警次数限制", None
        if len(parameter_list) > 5:
            return False, "参数数量过多，请重新输入.需要的参数分别为：\n越价率，越价+大单的大单阈值，单笔大单阈值，一分钟内的预警次数限制", None
        for i in range(1, len(parameter_list)):
            try:
                if i < len(parameter_list) - 1:
                    f = float(parameter_list[i])
                else:
                    f = int(parameter_list[i])
            except ValueError:
                if i < len(parameter_list) - 1:
                    return False, "第{0}个参数不是数值.".format(i), None
                else:
                    return False, "第{0}个参数不是整数.".format(i), None
            if i < len(parameter_list) - 1:
                parameter_list[i] = float(parameter_list[i])
            else:
                parameter_list[i] = int(parameter_list[i])
        msg = ''
        premium_rate = parameter_list[1]
        warning_threshold = parameter_list[2]
        large_threshold = parameter_list[3]
        warning_limit = parameter_list[4]
        if premium_rate > 1:
            msg += "越价率请设成小于0到1之间的数，如设置成0.005，即0.5%\n"
        if premium_rate <= 1e-8:
            msg += "越价率请大于1e-8\n"
        if warning_threshold <= 0:
            msg += "越价+大单组合预警的大单阈值，只能为正数.\n"
        if large_threshold <= 0:
            msg += "大单预警的阈值，只能为正数."
        if warning_limit > 15 or warning_limit < 1:
            msg += "一分钟内的预警次数限制，最少设置为1，最多设置为15.\n"
        if msg != '':
            return False, msg + "请重新输入.", None

        msg += "参数输入正确.\n"
        old_parameter_tuple = self.get_values_by_id('setting', 'openid', openid)
        if not old_parameter_tuple:   # 如果数据库没有存在这个
            msg += "这是您首次设置."
        else:
            if self.check_old_and_new(old_parameter_tuple[0], parameter_list):   # 如果不相同
                old_parameter_string = self.change_tuple_to_string(old_parameter_tuple[0])
                msg += "您上次的设置是：\n{0}".format(old_parameter_string)
            else:
                msg += "您的设置与上次一致，无需设置."
                return False, msg, None

        return True, msg, parameter_list[1:]

    def check_old_and_new(self, old_parameter_tuple, new_parameter_list):
        for i in range(1, len(old_parameter_tuple)):
            if old_parameter_tuple[i] != new_parameter_list[i]:
                return True   # 不相同
        return False


# ---- 单元测试代码
if __name__ == '__main__':
    mi = SqliteInterface()
    mi.check_setting_parameter("djkfhkdhsf","设置 0.005 1000000 2000000 10")
    mi.print_table('setting')
    print(mi.get_values_by_id('setting', 'openid', 'djkfhkdhsf'))

    mi.delete_table('setting')
    mi.update_price('HK.00001', 15.6)
    mi.print_table('price')
    mi.delete_table('price')