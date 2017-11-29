"""
Exceptions vmsheder module raise.
"""
from ..text import get_text, UNABLE_TO_CONNECT_TO, CHECK_CONNECTION, SERVER_ADDRESS
from ..text import ERROR_MESSAGE, SERVER_ERROR

from .common import SERVER_NAME

class VmshederException(Exception):
    """ The base exception of vmsheder exceptions.
    """
    pass


# TODO: is this useless?
class VmshederServerNotFound(VmshederException):
    """ Raise when vmsheder server is not found.
    """
    pass


class VmshederServerInternalError(VmshederException):
    """ Raise when there receive error from vmsheder server.
    mismatched header/body etc received from vmsheder server etc.
    """
    def __str__(self):
        return "%s %s" % (SERVER_NAME, get_text(SERVER_ERROR))


class VmshederServerRefused(VmshederException):
    """ Raise when connection to vmsheder server gets refused.
    """
    def __str__(self):
        return "%s %s, %s" % (
            get_text(UNABLE_TO_CONNECT_TO), SERVER_NAME, get_text(CHECK_CONNECTION)
        )
