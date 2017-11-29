from ..ui import mainloop, show_error
from .device_info import device_info_window
from ..vmsheder import set_host_n_port, VmshederException
from .. import vmsheder

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)

try:
    from . import config
except ImportError:
    logger.fatal('Configuration file not found!')
    exit()


def main():
    server_host = config.server_host
    server_port = config.server_port

    try:
        vmsheder.init(server_host, server_port)
    except VmshederException as e:
        show_error(str(e))
        logger.fatal('server_host: %s, server_port: %s' % (server_host, server_port))
        exit()

    window = device_info_window()
    mainloop()