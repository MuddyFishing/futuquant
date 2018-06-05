# -*- coding: utf-8 -*-

class RspHandlerBase(object):
    """callback function base class"""

    def __init__(self):
        pass

    def on_recv_rsp(self, rsp_pb):
        """receive response callback function"""
        return 0, None


