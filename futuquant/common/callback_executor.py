# -*- coding: utf-8 -*-

import threading
import queue
from collections import namedtuple

CallbackItem = namedtuple('CallbackItem', ['ctx', 'proto_id', 'rsp_pb'])

class CallbackExecutor:
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    @property
    def queue(self):
        return self._queue

    def run(self):
        while True:
            w = self._queue.get()
            if w is None:
                break

            ctx, proto_id, rsp_pb = w
            ctx.packet_callback(proto_id, rsp_pb)


callback_executor = CallbackExecutor()