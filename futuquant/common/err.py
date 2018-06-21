from collections import namedtuple

_ErrField = namedtuple('_ErrField', ('code', 'text'))


class Err:
    Ok = _ErrField(0, 'Ok')
    ConnectionLost = _ErrField(1, 'Connection lost')
    Timeout = _ErrField(2, 'Timeout')
