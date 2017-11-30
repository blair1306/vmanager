from ..ui import mainloop, show_error
from .device_info import device_info_window
from ..vmsheder import VmshederException
from .. import vmsheder

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)

from ..config import config_reader
from .. import text


def main():
    server_host = config_reader.get('vmsheder.host')
    server_port = config_reader.get_int('vmsheder.port')

    # default setting is Chinese.
    use_chinese = config_reader.get_boolean('language.chinese')
    text.init(use_chinese)

    try:
        vmsheder.init(server_host, server_port)
    except VmshederException as e:
        show_error(str(e))
        logger.fatal(vmsheder.get_info())
        exit()

    window = device_info_window()
    mainloop()