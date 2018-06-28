import socket
import select
import errno
import datetime
import threading
from struct import pack
from time import sleep
from futuquant.common.utils import *
from futuquant.quote.quote_query import parse_head
from .err import Err

class ConnStatus:
    Start = 0
    Connecting = 1
    Connected = 2
    Closed = 3

class SocketEvent:
    NoEvent = 0
    Read = 1 << 1
    Write = 1 << 2

class Connection:
    def __init__(self, conn_id: int, sock: socket.socket, addr, handler):
        self._conn_id = conn_id
        self.opend_conn_id = 0
        self.sock = sock
        self.handler = handler
        self._peer_addr = addr
        self.status = ConnStatus.Start
        self.keep_alive_interval = 10
        self.last_keep_alive_time = datetime.now()
        self.timeout = None
        self.start_time = None
        self.readbuf = bytearray()
        self.writebuf = bytearray()
        self.sync_req_data = None   # internal use
        self.sync_rsp_data = None   # internal use
        self.sync_req_evt = threading.Event()     # internal use
        self.sync_req_sent = False
        self.socket_event = SocketEvent.NoEvent

    @property
    def conn_id(self):
        return self._conn_id

    @property
    def peer_addr(self):
        return self._peer_addr

    @property
    def fileno(self):
        return self.sock.fileno


class NetManager:
    _default_inst = None

    @classmethod
    def default(cls):
        if cls._default_inst is None:
            cls._default_inst = NetManager()
        return cls._default_inst

    def __init__(self):
        self._rlist = []
        self._wlist = []
        self._elist = []
        self._closing_list = []
        self._is_polling = False
        self._next_conn_id = 1
        self._lock = threading.RLock()
        self._sync_req_timeout = 5
        self._stop = False
        self._thread = None
        self._use_count = 0
        self._owner_pid = 0

    def connect(self, addr, handler, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)
        with self._lock:
            conn = Connection(self._next_conn_id, sock, addr, handler)
            conn.status = ConnStatus.Connecting
            conn.start_time = datetime.now()
            conn.timeout = timeout
            sock.setblocking(False)
            self._next_conn_id += 1
            self._rlist.append(conn)
            self._wlist.append(conn)
            try:
                sock.connect(addr)
            except BlockingIOError:
                pass
            except Exception as e:
                return RET_ERROR, str(e), 0
        return RET_OK, '', conn.conn_id

    def sync_connect(self, addr, handler, timeout):
        with self._lock:
            ret, msg, conn_id = self.connect(addr, handler, timeout)
            conn = self._get_conn(conn_id)
        if ret != RET_OK:
            return ret, msg, 0
        start_time = datetime.now()
        while True:
            with self._lock:
                if conn.status == ConnStatus.Connected:
                    return RET_OK, '', conn_id
                else:
                    time_elapsed = datetime.now() - start_time
                    if time_elapsed.seconds >= timeout:
                        return RET_ERROR, Err.Timeout.text, 0
            sleep(0.05)

    def poll(self):
        with self._lock:
            for conn in self._closing_list:
                self.close(conn.conn_id)
            self._closing_list.clear()

            self._is_polling = True
            rlist = None
            wlist = None
            if len(self._rlist) > 0 or len(self._wlist) > 0:
                rlist, wlist, _ = select.select(self._rlist, self._wlist, self._elist, 0)

            if rlist is not None:
                for conn in rlist:
                    conn.socket_event |= SocketEvent.Read
            if wlist is not None:
                for conn in wlist:
                    conn.socket_event |= SocketEvent.Write

            now = datetime.now()
            for conn in self._rlist:    # type: Connection
                if conn.socket_event & SocketEvent.Read != 0:
                    self._on_read(conn)
                if conn.socket_event & SocketEvent.Write != 0:
                    self._on_write(conn)
                if conn.status == ConnStatus.Connecting:
                    time_delta = now - conn.start_time
                    if conn.timeout is not None and conn.timeout > 0 and time_delta.seconds >= conn.timeout:
                        self._on_connect_timeout(conn)
                # if conn.sync_req_data is not None and conn.status == ConnStatus.Connected:
                #     ret, msg = self.send(conn.conn_id, conn.sync_req_data[1])
                #     if ret != RET_OK:
                #         conn.sync_rsp_data = (ret, msg, None)
                #         conn.sync_req_evt.set()
                #         logger.debug('event set')
                conn.handler.on_activate(conn.conn_id, now)
                conn.socket_event = SocketEvent.NoEvent

            self._is_polling = False

    def _thread_func(self):
        while True:
            start_time = datetime.now()
            with self._lock:
                if self._stop:
                    self._close_all()
                    break
                self.poll()
            end_time = datetime.now()
            elapsed_msec = (end_time - start_time).total_seconds() * 1000000
            sleep_time = max(20 * 1000 - elapsed_msec, 0)
            sleep(sleep_time / 1000000)

    def start(self):
        """
        Should be called from main thread
        :return:
        """
        if self._owner_pid != os.getpid():
            self._stop = True
            self._use_count = 0
            while self._thread and self._thread.is_alive():
                sleep(0.01)
            self._close_all()
            self._thread = None
            self._rlist.clear()
            self._wlist.clear()
            self._owner_pid = os.getpid()
            self._closing_list.clear()
            self._next_conn_id = 1
            self._lock = threading.RLock()
            self._is_polling = False

        self._stop = False
        self._use_count += 1
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._thread_func)
        self._thread.start()

    def stop(self):
        with self._lock:
            self._use_count -= 1
            if self._use_count <= 0:
                self._use_count = 0
                self._stop = True

    def send(self, conn_id, data):
        with self._lock:
            conn = self._get_conn(conn_id)
            if not conn:
                return RET_ERROR, Err.ConnectionLost.text
            try:
                size = 0
                if len(conn.writebuf) > 0:
                    conn.writebuf.extend(data)
                else:
                    size = conn.sock.send(data)
                    # logger.debug('send: total_len={}; sent_len={};'.format(len(data), size))
                    # logger.debug(data[:size])
            except socket.error as e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    pass
                else:
                    return RET_ERROR, e.strerror

            if size > 0 and size < len(data):
                conn.writebuf.extend(data[size:])
                self._watch_write(conn, True)
        return RET_OK, ''

    def close(self, conn_id):
        with self._lock:
            conn = self._get_conn(conn_id)
            if not conn:
                return
            if conn.sock is None:
                return
            if self._is_polling:
                self._closing_list.append(conn)
            else:
                self._watch_read(conn, False)
                self._watch_write(conn, False)
                conn.sock.close()
                conn.sock = None
                conn.status = ConnStatus.Closed
                if conn.sync_req_data is not None:
                    conn.sync_req_evt.set()

    def _watch_read(self, conn, is_watch):
        self._watch(conn, self._rlist, is_watch)

    def _watch_write(self, conn, is_watch):
        self._watch(conn, self._wlist, is_watch)

    def _watch(self, conn, watch_list, is_watch):
        if is_watch:
            if conn not in watch_list:
                watch_list.append(conn)
        else:
            try:
                watch_list.remove(conn)
            except ValueError:
                pass

    def _close_all(self):
        conn_list = self._rlist.copy()
        for conn in conn_list:
            self.close(conn.conn_id)

    def sync_query(self, conn_id, req_str):
        head_dict = self._parse_req_head(req_str)
        while True:
            with self._lock:
                conn = self._get_conn(conn_id)
                if not conn:
                    return RET_ERROR, Err.ConnectionLost.text, None
                if conn.sync_req_data is None and conn.status == ConnStatus.Connected:
                    conn.sync_req_data = (head_dict, req_str)
                    sync_req_evt = conn.sync_req_evt
                    self.send(conn_id, req_str)
                    break
            sleep(0.01)

        is_timeout = not sync_req_evt.wait(self._sync_req_timeout)
        sync_req_evt.clear()
        rsp = None
        with self._lock:
            rsp = conn.sync_rsp_data
            conn.sync_req_data = None
            conn.sync_rsp_data = None
        if rsp is not None:
            if rsp[0] == RET_OK:
                return RET_OK, '', rsp[2]
            else:
                return RET_ERROR, rsp[1], rsp[2]
        elif is_timeout:
            return RET_ERROR, Err.Timeout.text, None
        else:
            return RET_ERROR, Err.ConnectionLost.text, None

    def _parse_req_head(self, req_str):
        head_len = get_message_head_len()
        req_head_dict = parse_head(req_str[:head_len])
        return req_head_dict

    def _get_conn(self, conn_id) -> Connection:
        return next((conn for conn in self._rlist if conn.conn_id == conn_id), None)

    def _on_read(self, conn: Connection):
        if conn.status == ConnStatus.Closed:
            return
        err = None
        is_closed = False
        while True:
            try:
                data = conn.sock.recv(1024 * 1024)
                if data == b'':
                    is_closed = True
                    break
                else:
                    conn.readbuf.extend(data)
            except socket.error as e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    break
                else:
                    err = e
                    break

        while len(conn.readbuf) > 0:
            head_len = get_message_head_len()
            if len(conn.readbuf) < head_len:
                break
            head_dict = parse_head(conn.readbuf[:head_len])
            body_len = head_dict['body_len']
            if len(conn.readbuf) < head_len + body_len:
                break

            rsp_body = conn.readbuf[head_len:head_len+body_len]
            del conn.readbuf[:head_len+body_len]
            ret_decrypt, msg_decrypt, rsp_body = decrypt_rsp_body(rsp_body, head_dict, conn.opend_conn_id)
            if ret_decrypt == RET_OK:
                rsp_pb = binary2pb(rsp_body, head_dict['proto_id'], head_dict['proto_fmt_type'])
            else:
                rsp_pb = None

            is_sync_rsp = False
            if conn.sync_req_data is not None:
                sync_req_head = conn.sync_req_data[0]
                if head_dict['proto_id'] == sync_req_head['proto_id'] and head_dict['serial_no'] == sync_req_head['serial_no']:
                    conn.sync_rsp_data = (ret_decrypt, msg_decrypt, rsp_pb)
                    conn.sync_req_evt.set()
                    is_sync_rsp = True

            if not is_sync_rsp:
                conn.handler.on_packet(conn.conn_id, head_dict['proto_id'], ret_decrypt, msg_decrypt, rsp_pb)

        if is_closed:
            conn.handler.on_closed(conn.conn_id)
        if err:
            conn.handler.on_error(conn.conn_id, err)

    def _on_write(self, conn: Connection):
        if conn.status == ConnStatus.Closed:
            return
        elif conn.status == ConnStatus.Connecting:
            conn.status = ConnStatus.Connected
            self._watch_write(conn, False)
            conn.handler.on_connected(conn.conn_id)
            return

        err = None

        size = 0
        try:
            if len(conn.writebuf) > 0:
                size = conn.sock.send(conn.writebuf)
                # logger.debug('send: total_len={}; sent_len={};'.format(len(conn.writebuf), size))
                # logger.debug(conn.writebuf[:size])
        except socket.error as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                err = e

        if size > 0:
            del conn.writebuf[:size]

        if len(conn.writebuf) == 0:
            self._watch_write(conn, False)

        if err:
            conn.handler.on_error(conn.conn_id, err)

    def _on_connect_timeout(self, conn: Connection):
        conn.handler.on_connect_timeout(conn.conn_id)

    @staticmethod
    def extract_rsp_pb(opend_conn_id, head_dict, rsp_body):
        ret, msg, rsp = decrypt_rsp_body(rsp_body, head_dict, opend_conn_id)
        if ret == RET_OK:
            rsp_pb = binary2pb(rsp_body, head_dict['proto_id'], head_dict['proto_fmt_type'])
        else:
            rsp_pb = None
        return ret, msg, rsp_pb

    def set_conn_info(self, conn_id, info:dict):
        with self._lock:
            conn = self._get_conn(conn_id)
            if conn is not None:
                conn.opend_conn_id = info.get('conn_id', conn.opend_conn_id)
                conn.keep_alive_interval = info.get('keep_alive_interval', conn.keep_alive_interval)
            else:
                return RET_ERROR, Err.ConnectionLost.text
        return RET_OK, ''
