from .text import get_text
from .text import DEVICE_ID, RESOLUTION, RAM_SIZE_IN_GB, STATUS


class DeviceInfo(object):
    """
    info of a virtual device such as it's screen resolution, RAM size etc.
    """
    def __init__(self, _id, res, RAM_GB, status):
        self._id = _id
        self._res = res
        self._RAM_GB = RAM_GB
        self._status = status

    def __repr__(self):
        return '[%s: %s] (%s: %s) (%s: %s) (%s: %s)' % (
                get_text(DEVICE_ID), self._id,
                get_text(RESOLUTION), self._res,
                get_text(RAM_SIZE_IN_GB), self._RAM_GB, 
                get_text(STATUS), self._status
                )

    def _set_id(self, _id):
        self._id = _id

    def _get_id(self):
        return self._id

    id = property(_get_id, _set_id)


class DeviceList(object):
    def __init__():
        pass

