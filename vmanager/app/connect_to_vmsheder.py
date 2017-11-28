""" This module provides a window to specify the hostname and port of vmsheder.
"""


from ..ui import create_window, create_frame, create_button, create_entry, create_label
from ..ui import bind_click
from .text import get_text, SERVER_ADDRESS, PORT, SELECT

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)


def connect_to_vmsheder_window():
    window = create_window()
    connect_to_vmsheder_view(window)

    return window


def connect_to_vmsheder_view(master):
    """The V in the MVC model.
    """
    view = create_frame(master)

    # the address part
    master = create_frame(view)

    addr = create_frame(master, left=True)
    create_label(addr, text=get_text(SERVER_ADDRESS))
    view.server_address = create_entry(addr)

    port = create_frame(master, left=True)
    create_label(port, text=get_text(PORT))
    view.port = create_entry(port)

    # the button part
    master = create_frame(view)
    view.select_button = create_button(master, text=get_text(SELECT))


class Controller(object):
    """ The C in the MVC model.
    This class is responsible for configuring the buttons of the view,
    Get the default server address and port and display them.
    Get user input if any and try to connect to vmsheder server with
    the given address or the default one if none is provided.
    """
    def __init__(self, view):
        # the view must have a select_button attribute in order to get
        # configured correctly.
        if not hasattr(view, 'select_button'):
            logger.fatal('no select button to be configured.')
        else:
            bind_click(view.select_button, self.on_select)
        
        
    
    def on_select(self):
        # TODO
        pass