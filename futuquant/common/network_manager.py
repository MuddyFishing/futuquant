import errno
import datetime
import threading
from time import sleep
from futuquant.common.utils import *
from futuquant.quote.quote_query import parse_head
from .err import Err
from .utils import ProtoInfo
from .ft_logger import make_log_msg
if IS_PY2:
    import selectors2 as selectors
else:
    import selectors

class ConnStatus:
    Start = 0
    Connecting = 1
    Connected = 2
    Closed = 3

class Connection:
    def __init__(self, conn_id, sock, addr, handler):
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
        self.req_dict = {}  # ProtoInfo -> req time

    @property
    def conn_id(self):
        return self._conn_id

    @property
    def peer_addr(self):
        return self._peer_addr

    def fileno(self):
        return self.sock.fileno


def is_socket_exception_wouldblock(e):
    has_errno = False
    if IS_PY2:
        if isinstance(e, IOError):
            has_errno = True
    else:
        if isinstance(e, OSError):
            has_errno = True

    if has_errno:
        if e.errno == errno.EWOULDBLOCK or e.errno == errno.EAGAIN or e.errno == errno.EINPROGRESS:
            return True
    return False

class NetManager:
    _default_inst = None

    @classmethod
    def default(cls):
        if cls._default_inst is None:
            cls._default_inst = NetManager()
        return cls._default_inst

    def __init__(self):
        self._selector = selectors.DefaultSelector()
        self._is_polling = False
        self._next_conn_id = 1
        self._lock = threading.RLock()
        self._sync_req_timeout = 10
        self._thread = None
        self._use_count = 0
        self._owner_pid = 0
        self._connecting_sock_dict = {}  # sock -> conn_time
        now = datetime.now()
        self._last_activate_time = now
        self._last_check_req_time = now

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
            self._selector.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, conn)

            try:
                sock.connect(addr)
            except Exception as e:
                if not is_socket_exception_wouldblock(e):
                    self.close(conn.conn_id)
                    return RET_ERROR, str(e), 0
        return RET_OK, '', conn.conn_id

    def poll(self):
        with self._lock:
            if len(self._selector.get_map()) == 0:
                return

            self._is_polling = True

            now = datetime.now()
            events = self._selector.select(0)
            for key, evt_mask in events:
                conn = key.data
                if evt_mask & selectors.EVENT_WRITE != 0:
                    self._on_write(conn)

                if evt_mask & selectors.EVENT_READ != 0:
                    self._on_read(conn)

                if conn.sync_req_data is not None and conn.sync_rsp_data is None:
                    elapsed_time = datetime.now() - conn.start_time
                    if elapsed_time.total_seconds() >= self._sync_req_timeout:
                        conn.sync_rsp_data = (RET_ERROR, Err.Timeout.text, None)
                        conn.sync_req_evt.set()

            activate_elapsed_time = now - self._last_activate_time
            check_req_elapsed_time = now - self._last_check_req_time
            is_activate = activate_elapsed_time.total_seconds() >= 0.05
            is_check_req = check_req_elapsed_time.total_seconds() >= 0.1

            if is_activate or is_check_req:
                for sock, key in self._selector.get_map().items():
                    conn = key.data
                    if conn.status == ConnStatus.Connecting:
                        if is_activate:
                            self._check_connect_timeout(conn, now)
                    elif conn.status == ConnStatus.Connected:
                        if is_activate:
                            conn.handler.on_activate(conn.conn_id, now)
                        if is_check_req:
                            self._check_req(conn, now)

            if is_activate:
                self._last_activate_time = now
            if is_check_req:
                self._last_check_req_time = now

            self._is_polling = False

    def _check_connect_timeout(self, conn, now):
        time_delta = now - conn.start_time
        if conn.timeout is not None and conn.timeout > 0 and time_delta.total_seconds() >= conn.timeout:
            self._on_connect_timeout(conn)

    def _check_req(self, conn, now):
        """

        :param conn:
        :type conn: Connection
        :param now:
        :type now: datetime
        :return:
        """
        req_dict = dict(conn.req_dict.items())
        for proto_info, req_time in req_dict.items():  # type: ProtoInfo, datetime
            elapsed_time = now - req_time
            if elapsed_time.total_seconds() >= self._sync_req_timeout:
                self._on_packet(conn, proto_info._asdict(), Err.Timeout.code, Err.Timeout.text, None)

    def _thread_func(self):
        while True:
            with self._lock:
                if self.is_alive():
                    self.poll()
                else:
                    self._close_all()
                    self._thread = None
                    self._selector.close()
                    self._next_conn_id = 1
                    self._is_polling = False
                    break
            time.sleep(0.001)

    def start(self):
        """
        Should be called from main thread
        :return:
        """
        while True:
            with self._lock:
                if self._owner_pid != os.getpid():
                    self._use_count = 0

                if not self.is_alive():
                    if self._thread is None:
                        break
                else:
                    break
            sleep(0.01)

        with self._lock:
            self._use_count += 1
            if self._thread is None:
                self._owner_pid = os.getpid()
                self._thread = threading.Thread(target=self._thread_func)
                self._thread.start()

    def stop(self):
        with self._lock:
            self._use_count = max(self._use_count - 1, 0)

        while True:
            with self._lock:
                if not self.is_alive():
                    if self._thread is None:
                        break
                else:
                    break
            sleep(0.01)

    def is_alive(self):
        with self._lock:
            return self._use_count > 0

    def send(self, conn_id, proto_info, data):
        """

        :param conn_id:
        :param proto_info:
        :type proto_info: ProtoInfo
        :param data:
        :return:
        """
        logger.debug('Send: conn_id={}; proto_id={}; serial_no={}; total_len={};'.format(conn_id, proto_info.proto_id,
                                                                                         proto_info.serial_no,
                                                                                         len(data)))
        now = datetime.now()
        ret_code = RET_OK
        msg = ''
        with self._lock:
            conn = self._get_conn(conn_id)  # type: Connection
            if not conn:
                ret_code, msg = RET_ERROR, Err.ConnectionLost.text
            if conn.status != ConnStatus.Connected:
                ret_code, msg = RET_ERROR, Err.NotConnected.text

            if ret_code != RET_OK:
                logger.warning(make_log_msg('Send fail', proto_id=proto_info.proto_id, serial_no=proto_info.serial_no,
                                            conn_id=conn_id, msg=msg))
                return ret_code, msg

            conn.req_dict[proto_info] = now
            size = 0
            try:
                if len(conn.writebuf) > 0:
                    conn.writebuf.extend(data)
                else:
                    size = conn.sock.send(data)
                    # logger.debug('send: total_len={}; sent_len={};'.format(len(data), size))
                    # logger.debug(data[:size])
            except Exception as e:
                if is_socket_exception_wouldblock(e):
                    pass
                else:
                    conn.writebuf.extend(data)
                    self._watch_write(conn, True)
                    ret_code, msg = RET_ERROR, e.strerror

            if size > 0 and size < len(data):
                conn.writebuf.extend(data[size:])
                self._watch_write(conn, True)

            if ret_code != RET_OK:
                logger.warning(make_log_msg('Send error', conn_id=conn_id, msg=msg))
                return ret_code, msg

        return RET_OK, ''


    def close(self, conn_id):
        with self._lock:
            conn = self._get_conn(conn_id)
            if not conn:
                return
            if conn.sock is None:
                return
            self._watch_read(conn, False)
            self._watch_write(conn, False)
            conn.sock.close()
            conn.sock = None
            conn.status = ConnStatus.Closed
            if conn.sync_req_data is not None:
                conn.sync_req_evt.set()

    def _watch_read(self, conn, is_watch):
        try:
            sel_key = self._selector.get_key(conn.sock)
        except KeyError:
            return

        if is_watch:
            new_event = sel_key.events | selectors.EVENT_READ
        else:
            new_event = sel_key.events & (~selectors.EVENT_READ)

        if new_event != 0:
            self._selector.modify(conn.sock, new_event, conn)
        else:
            self._selector.unregister(conn.sock)

    def _watch_write(self, conn, is_watch):
        try:
            sel_key = self._selector.get_key(conn.sock)
        except KeyError:
            return

        if is_watch:
            new_event = sel_key.events | selectors.EVENT_WRITE
        else:
            new_event = sel_key.events & (~selectors.EVENT_WRITE)

        if new_event != 0:
            self._selector.modify(conn.sock, new_event, conn)
        else:
            self._selector.unregister(conn.sock)

    def _close_all(self):
        for sock, sel_key in self._selector.get_map().items():
            self._selector.unregister(sock)
            sock.close()

    def sync_query(self, conn_id, req_str):
        head_dict = self._parse_req_head(req_str)
        proto_info = ProtoInfo(head_dict['proto_id'], head_dict['serial_no'])
        while True:
            with self._lock:
                conn = self._get_conn(conn_id)
                if not conn:
                    return RET_ERROR, Err.ConnectionLost.text, None
                if conn.sync_req_data is None and conn.status == ConnStatus.Connected:
                    conn.sync_req_data = (head_dict, req_str)
                    conn.sync_rsp_data = None
                    conn.start_time = datetime.now()
                    sync_req_evt = conn.sync_req_evt
                    self.send(conn_id, proto_info, req_str)
                    break
            sleep(0)

        sync_req_evt.wait()
        sync_req_evt.clear()

        with self._lock:
            rsp = conn.sync_rsp_data
            conn.sync_req_data = None
            conn.sync_rsp_data = None
        if rsp is not None:
            return rsp
        else:
            return RET_ERROR, Err.ConnectionLost.text, None

    def _parse_req_head(self, req_str):
        head_len = get_message_head_len()
        req_head_dict = parse_head(req_str[:head_len])
        return req_head_dict

    def _get_conn(self, conn_id):
        for sock, sel_key in self._selector.get_map().items():
            conn = sel_key.data
            if conn.conn_id == conn_id:
                return conn
        return None

    def _on_read(self, conn):
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
            except Exception as e:
                if is_socket_exception_wouldblock(e):
                    break
                else:
                    err = str(e)
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
            self._on_packet(conn, head_dict, Err.Ok.code, '', rsp_body)

        if is_closed:
            self.close(conn.conn_id)
            conn.handler.on_closed(conn.conn_id)
        elif err:
            self.close(conn.conn_id)
            conn.handler.on_error(conn.conn_id, err)

    def _on_write(self, conn):
        if conn.status == ConnStatus.Closed:
            return
        elif conn.status == ConnStatus.Connecting:
            err = conn.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            self._watch_write(conn, False)
            if err != 0:
                conn.handler.on_error(conn.conn_id, errno.errorcode[err])
            else:
                conn.status = ConnStatus.Connected
                conn.handler.on_connected(conn.conn_id)
            return

        err = None

        size = 0
        try:
            if len(conn.writebuf) > 0:
                size = conn.sock.send(conn.writebuf)
                # logger.debug('send: total_len={}; sent_len={};'.format(len(conn.writebuf), size))
                # logger.debug(conn.writebuf[:size])
        except Exception as e:
            if not is_socket_exception_wouldblock(e):
                err = str(e)

        if size > 0:
            del conn.writebuf[:size]

        if len(conn.writebuf) == 0:
            self._watch_write(conn, False)

        if err:
            self.close(conn.conn_id)
            conn.handler.on_error(conn.conn_id, err)

    def _on_connect_timeout(self, conn):
        conn.handler.on_connect_timeout(conn.conn_id)

    def _on_packet(self, conn, head_dict, err_code, msg, rsp_body_data):
        """

        :param conn:
        :type conn: Connection
        :param head_dict:
        :param err_code:
        :param msg:
        :param rsp_body_data:
        :return:
        """
        proto_info = ProtoInfo(head_dict['proto_id'], head_dict['serial_no'])
        rsp_pb = None
        if err_code == Err.Ok.code:
            ret_decrypt, msg_decrypt, rsp_body = decrypt_rsp_body(rsp_body_data, head_dict, conn.opend_conn_id)
            if ret_decrypt == RET_OK:
                rsp_pb = binary2pb(rsp_body, head_dict['proto_id'], head_dict['proto_fmt_type'])
            else:
                err_code = Err.PacketDataErr.code
                msg = msg_decrypt
                rsp_pb = None

        log_msg = 'Recv: conn_id={}; proto_id={}; serial_no={}; data_len={}; msg={};'.format(conn.conn_id,
                                                                                             proto_info.proto_id,
                                                                                             proto_info.serial_no,
                                                                                             len(rsp_body_data) if rsp_body_data else 0,
                                                                                             msg)
        if err_code == Err.Ok.code:
            logger.debug(log_msg)
        else:
            logger.warning(log_msg)

        ret_code = RET_OK if err_code == Err.Ok.code else RET_ERROR
        is_sync_rsp = False
        if conn.sync_req_data is not None:
            sync_req_head = conn.sync_req_data[0]
            if head_dict['proto_id'] == sync_req_head['proto_id'] and head_dict['serial_no'] == sync_req_head['serial_no']:
                conn.sync_rsp_data = (ret_code, msg, rsp_pb)
                conn.sync_req_evt.set()
                is_sync_rsp = True

        conn.req_dict.pop(proto_info, None)
        if not is_sync_rsp:
            conn.handler.on_packet(conn.conn_id, proto_info, ret_code, msg, rsp_pb)

    @staticmethod
    def extract_rsp_pb(opend_conn_id, head_dict, rsp_body):
        ret, msg, rsp = decrypt_rsp_body(rsp_body, head_dict, opend_conn_id)
        if ret == RET_OK:
            rsp_pb = binary2pb(rsp_body, head_dict['proto_id'], head_dict['proto_fmt_type'])
        else:
            rsp_pb = None
        return ret, msg, rsp_pb

    def set_conn_info(self, conn_id, info):
        with self._lock:
            conn = self._get_conn(conn_id)
            if conn is not None:
                conn.opend_conn_id = info.get('conn_id', conn.opend_conn_id)
                conn.keep_alive_interval = info.get('keep_alive_interval', conn.keep_alive_interval)
            else:
                return RET_ERROR, Err.ConnectionLost.text
        return RET_OK, ''
