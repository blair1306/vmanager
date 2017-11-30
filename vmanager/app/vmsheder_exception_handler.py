""" This module provides some vmsheder specific exceptions handler.
"""
from ..vmsheder import VmshederServerRefused, VmshederServerInternalError, VmshederException
from ..vmsheder import get_info
from ..ui import show_error
from ..text import get_text, UNABLE_TO_CONNECT_TO, CHECK_CONNECTION, SERVER_ADDRESS
from ..text import ERROR_MESSAGE, SERVER_ERROR

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)


def catch_display_vmsheder_exception(func):
    """Catch and Display a vmsheder exception as a popup error message.
    This function is designed to work with those controllers defined in this module.
    @param func: func that might raise vmsheder exceptions to be handled.
    @param window: will be used as the parent of the popup if provided.
    """
    def wrapper(self=None, *args, **wargs):
        if self:
            if hasattr(self, '_window'):
                window = self._window
            elif hasattr(self, '_view'):
                window = self._view
        else:
            window = None
            logger.warn('window not supplied.')

        try:
            func(self)
        except VmshederException as e:
            logger.fatal(get_info())
            show_error(str(e), window)
            exit()

    return wrapper