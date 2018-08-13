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

    def update_setting(self, open_id, user_setting):
        parameter_list = re.split(r" +", user_setting)
        p1 = float(parameter_list[1])
        p2 = float(parameter_list[2])
        p3 = float(parameter_list[3])
        p4 = int(parameter_list[4])
        conn = sqlite3.connect(self.database)
        statement = "INSERT OR REPLACE INTO {0} VALUES(?,?,?,?,?)".format('setting')
        data = [(open_id, p1, p2, p3, p4)]
        conn.executemany(statement, data)
        conn.commit()

    # price 表
    def create_table_price(self):
        conn = sqlite3.connect(self.database)  # 创建数据库
        query = """CREATE TABLE IF NOT EXISTS price(stockid VARCHAR(25) PRIMARY KEY, preprice DOUBLE)"""
        conn.execute(query)
        conn.close()
        print("Table {0} is ready".format('setting'))

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

# ---- 单元测试代码
if __name__ == '__main__':
    mi = SqliteInterface()
    mi.update_setting("djkfhkdhsf","设置 0.005 1000000 2000000 10")
    mi.print_table('setting')
    mi.get_values_by_id('setting', 'openid', 'djkfhkdhsf')
    mi.delete_table('setting')
    mi.update_price('HK.00001', 15.6)
    mi.print_table('price')
    mi.delete_table('price')