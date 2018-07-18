# -*- coding: utf-8 -*-
import pymysql
import sys


class mysql_interface:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 3306
        self.user = 'root'
        self.passwd = 'hackch'
        self.database = 'shock_alarm'

    def mysql_connect(self):
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        row = cursor.fetchone()
        print("MySQL server version:", row[0])
        cursor.close()
        conn.close()

    def create_table(self):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS setting(openid VARCHAR(100) PRIMARY KEY, warning_threshold numeric(20, 8), single_deal_threshold numeric(20, 8), shockid VARCHAR(100))")
        # cur.execute('insert into setting(openid, warning_threshold, single_deal_threshold, shockid) values ("%s", "%f", "%f", "%s") ' % (myopenid, p1, p2, shockid))
        # con.commit()
        con.close()

    def print_table(self):
        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        cur.execute("select * from setting")
        results = cur.fetchall()

        for row in results:
            print(row)

        con.close()

    def update_threshold(self, openid, user_setting):
        list = user_setting.split(" ")
        p1 = float(list[1])
        p2 = float(list[2])


        con = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.database)
        cur = con.cursor()
        sql_update_threshold = 'insert into setting set openid = "%s", warning_threshold = "%f", single_deal_threshold = "%f" on duplicate key update warning_threshold = "%f", single_deal_threshold = "%f"'

        try:
            cur.execute(sql_update_threshold % (openid, p1, p2, p1, p2))
            # 提交
            con.commit()
        except Exception as e:
            # 错误回滚
            con.rollback()
        finally:
            con.close()

    def update_shockid(self):
        return 0

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
        return results



# test code
# myopenid = "kdhfskgadfvbsdvkjgkaghsdzfkigv_dgfjsdzfvbjazsgdcfvgh"
# p1 = 1000000.0
# p2 = 4000000.0
# shockid = ""
# user_setting = '设置' + ' ' + str(p1) + ' ' + str(p2) + ' '
# mi = mysql_interaction()
# mi.mysql_connect()
# mi.create_table()
# mi.update_threshold(myopenid, user_setting)
# mi.print_table()
# mi.delete_user_setting(myopenid)
# mi.print_table()
# mi.get_setting_by_openid(myopenid)
