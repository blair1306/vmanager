""" This module provides some vmsheder specific exceptions handler.
"""
from ..vmsheder import VmshederServerRefused, VmshederServerInternalError
from ..ui import show_error
from .text import get_text, UNABLE_TO_CONNECT_TO, CHECK_CONNECTION, SERVER_ADDRESS
from .text import ERROR_MESSAGE, SERVER_ERROR

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)


def catch_display_vmsheder_exception(func):
    """Catch and Display a vmsheder exception as a popup error message.
    @param func: func that might raise vmsheder exceptions to be handled.
    @param window: will be used as the parent of the popup if provided.
    """
    def wrapper(self=None, *args, **wargs):
        if self and hasattr(self, '_window'):
            window = self._window
        else:
            window = None
            logger.warn('window not supplied.')

        try:
            func(self)
        except VmshederServerRefused as e:
            message = "%s Vmsheder %s, %s. %s: %s" % \
                (
                    get_text(UNABLE_TO_CONNECT_TO), get_text(SERVER_ADDRESS), get_text(CHECK_CONNECTION),
                    (get_text(ERROR_MESSAGE)), repr(e)
                )
            show_error(message, parent=window)
        except VmshederServerInternalError as e:
            message = "Vmsheder %s. %s: %s" % \
                (
                    get_text(SERVER_ERROR), get_text(ERROR_MESSAGE), repr(e)
                )

    return wrapper