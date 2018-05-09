# -*- coding: utf-8 -*-

class FutuConnMng(object):
    All_Conn_Dict = {}
    @classmethod
    def add_conn(cls, conn_dict):
        all_conn = FutuConnMng.All_Conn_Dict
        conn_id = conn_dict['conn_id']
        all_conn[conn_id] = conn_dict

    @classmethod
    def remove_conn(cls, conn_id):
        all_conn = FutuConnMng.All_Conn_Dict
        if conn_id in all_conn:
            all_conn.pop(conn_id)

    @classmethod
    def get_conn_info(cls, conn_id):
        all_conn = FutuConnMng.All_Conn_Dict
        return all_conn[conn_id] if conn_id in all_conn else None

    @classmethod
    def get_conn_key(cls, conn_id):
        conn_info = FutuConnMng.get_conn_info(conn_id)
        return conn_info['conn_key'] if conn_info else None

    @classmethod
    def get_conn_user_id(cls, conn_id):
        conn_info = FutuConnMng.get_conn_info(conn_id)
        return conn_info['login_user_id'] if conn_info else 0

    @classmethod
    def is_conn_encrypt(cls, conn_id):
        # 连接暂时未启用加密
        return False