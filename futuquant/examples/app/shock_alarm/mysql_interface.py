# -*- coding: utf-8 -*-
import pymysql
import sys
import re
import common_parameter


class MysqlInterface:
    def __init__(self):
        self.host = common_parameter.host
        self.port = common_parameter.port
        self.user = common_parameter.user
        self.passwd = common_parameter.passwd
        self.database = common_parameter.database

    def mysql_connect(self):
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        row = cursor.fetchone()
        print("MySQL server version:", row[0])
        cursor.close()
        conn.close()

    def create_table_setting(self):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS setting(openid VARCHAR(100) PRIMARY KEY, premium_rate double, warning_threshold double, single_deal_threshold double, warning_limit int)")
        # cur.execute('insert into setting(openid, warning_threshold, single_deal_threshold, stockid) values ("%s", "%f", "%f", "%s") ' % (myopenid, p1, p2, stockid))
        # con.commit()
        con.close()

    def print_setting_table(self):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute("select * from setting")
        results = cur.fetchall()

        for row in results:
            print(row)

        con.close()

    def update_threshold(self, openid, user_setting):
        parameter_list = re.split(r" +", user_setting)
        p1 = float(parameter_list[1])
        p2 = float(parameter_list[2])
        p3 = float(parameter_list[3])
        p4 = float(parameter_list[4])

        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        sql_update_threshold = 'insert into setting set openid = "%s", premium_rate = "%f", warning_threshold = "%f", single_deal_threshold = "%f", warning_limit = "%d" on duplicate key update premium_rate = "%f", warning_threshold = "%f", single_deal_threshold = "%f", warning_limit = "%d"'

        try:
            cur.execute(sql_update_threshold % (openid, p1, p2, p3, p4, p1, p2, p3, p4))
            # 提交
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def delete_user_setting(self, openid):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()

        sql_delete = 'delete from setting where openid = "%s"'
        try:
            cur.execute(sql_delete % (openid))
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def get_all_user_setting(self):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute('select * from setting')
        results = cur.fetchall()
        con.close()
        return results

    def get_setting_by_openid(self, openid):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute('select * from setting where openid = "%s"' % openid)
        results = cur.fetchall()
        con.close()
        return results    # 只返回一行

    def create_table_price(self):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS price(stockid VARCHAR(25) PRIMARY KEY, preprice double)")
        con.close()

    def update_price(self, stockid, price):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        sql_update_threshold = 'insert into price set stockid = "%s", preprice = "%f" on duplicate key update preprice = "%f"'

        try:
            cur.execute(sql_update_threshold % (stockid, price, price))
            # 提交
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def get_preprice_by_stockid(self, stockid):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute('select * from price where stockid = "%s"' % stockid)
        results = cur.fetchall()
        con.close()
        return results

    def delete_price(self, stockid):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()

        sql_delete = 'delete from price where stockid = "%s"'
        try:
            cur.execute(sql_delete % (stockid))
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def update_warning_limit(self, stockid, warning_limit):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        sql_update_threshold = 'insert into price set stockid = "%s", warning_limit = "%d" on duplicate key update warning_limit = "%d"'

        try:
            cur.execute(sql_update_threshold % (stockid, warning_limit, warning_limit))
            # 提交
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def create_table_warning_list(self):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS warning_list(openid VARCHAR(25) PRIMARY KEY, time_list VARCHAR(200))")
        con.close()

    def update_warning_list(self, openid, time_list):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        sql_update_threshold = 'insert into warning_list set stockid = "%s", time_list = "%s" on duplicate key update time_list = "%s"'

        try:
            cur.execute(sql_update_threshold % (openid, time_list, time_list))
            # 提交
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def delete_warning_list(self, openid):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()

        sql_delete = 'delete from warning_list where openid = "%s"'
        try:
            cur.execute(sql_delete % (openid))
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def get_time_list_by_openid(self, openid):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute('select * from warning_list where openid = "%s"' % openid)
        results = cur.fetchall()
        con.close()
        return results