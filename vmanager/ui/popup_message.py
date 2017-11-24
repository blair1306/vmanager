from .compat import MessageBox

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)


def show_info(message, parent=None, **kwargs):
    """
    Show a pop-up message.
    @param parent: the parent of the message, the center of where the message will be.
    """
    logger.debug('The parent is: %s' % parent)
    MessageBox.showinfo(message=message, parent=parent, **kwargs)


def show_warning(message, parent=None, **kwargs):
    """
    Show a pop-up warning message.
    """
    MessageBox.showwarning(message=message, parent=parent, **kwargs)


def show_error(message, parent=None, **kwargs):
    """
    Show a pop-up error message.
    """
    MessageBox.showerror(message=message, parent=parent, **kwargs)
