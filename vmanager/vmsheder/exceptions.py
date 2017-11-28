"""
Exceptions vmsheder module raise.
"""


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
    pass


class VmshederServerRefused(VmshederException):
    """ Raise when connection to vmsheder server gets refused.
    """
    pass