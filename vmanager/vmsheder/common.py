""" Some global stuff shared among vmsheder module.
"""


SERVER_NAME = 'Vmsheder'

# Default host and port
g_host = '192.168.31.188'
g_port = 5895


def set_host_n_port(_host, _port):
    # TODO: assertions
    if _host is None or _port is None:
        return

    global g_host
    global g_port

    g_host = _host
    g_port = _port


def get_info():
    """ Get diagnostic infos of vmsheder.
    Useful when there's an error.
    """
    return 'Vmsheder host: %s, port: %s' % (g_host, g_port)