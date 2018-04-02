# -*- coding: utf-8 -*-
from threading import RLock

class SafeTradeSubscribeList:
    def __init__(self):
        self._list_sub = []
        self._lock = RLock()

    def add_val(self, orderid, envtype):
        self._lock.acquire()
        self._list_sub.append((str(orderid), int(envtype)))
        self._lock.release()

    def has_val(self, orderid, envtype):
        ret_val = False
        self._lock.acquire()
        if (str(orderid), int(envtype)) in self._list_sub:
            ret_val = True
        self._lock.release()
        return ret_val

    def del_val(self, orderid, envtype):
        self._lock.acquire()
        key = (str(orderid), int(envtype))
        if key in self._list_sub:
            self._list_sub.remove(key)
        self._lock.release()

    def copy(self):
        list_ret = None
        self._lock.acquire()
        list_ret = [i for i in self._list_sub]
        self._lock.release()
        return list_ret