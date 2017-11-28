from ..ui import mainloop
from .device_info import device_info_window
from ..vmsheder import set_host_n_port

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)


def main():
    init()

    window = device_info_window()
    mainloop()


def init():
    """ Load and set vmsheder server address and port from config.py
    """
    try:
        from . import config
        server_host = config.server_host
        server_port = config.server_port
        
        logger.debug('read from config.py, server_host: %s, server_port: %s'
            % (server_host, server_port))
        set_host_n_port(config.server_host, config.server_port)

    except ImportError:
        logger.fatal('No configuartion file')