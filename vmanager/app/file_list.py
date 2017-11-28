"""
This module provides a window for selecting from a list of files.
This file list window returns a list of files selected when Select Button is hit and destroy itself.
"""


from ..ui import create_frame, create_ms_listbox, create_button, create_label
from ..ui import create_ret_window
from ..ui import bind_click
from ..ui import show_info, show_error, show_warning

from .text import get_text, LIST_OF_FILE, SELECT, CANCEL, CANCELLED, DONE

from .dynamic_listbox import DynamicListBox

from ..vmsheder import list_apk

import logging
from ..debug import logging_default_configure

logger = logging.getLogger(__name__)
logging_default_configure(logger)


TITLE = get_text(LIST_OF_FILE)


def file_list_window(vm_id='6666'):
    """
    A window ready to use.
    """
    window = create_ret_window(TITLE)
    view = file_list_view(window, vm_id)
    view.controller = Controller(view.listbox, view.select_button, view.cancel_button, view, window)

    return window


def build_list_view(master, vm_id):
    """
    A frame can be plug into a window.
    """
    raise NotImplementedError('file list frame can\'t be plug into other window.')


def file_list_view(master, vm_id):
    """ The V in the MVC model.
    This view provides a listbox to show a list of file available for selection.
    A select button, a cancel button.
    """
    view = create_frame(master)

    # the top sub-frame for listbox
    master = create_frame(view)
    create_label(master, text=vm_id)
    view.listbox = create_ms_listbox(master)

    # the bottom sub-frame for buttons
    master = create_frame(view)
    view.select_button = create_button(master, left=True, text=get_text(SELECT))
    view.cancel_button = create_button(master, left=True, text=get_text(CANCEL))

    return view


def create_file_listbox(listbox):
    """ The M in the MVC model.
    A list box for displaying a list of file names, get the files selected.
    @param ls: the function used to get a list of filenames to display.
    """
    update = list_apk
    file_listbox = DynamicListBox(update, listbox)

    return file_listbox


class Controller(object):
    """The C in the MVC model.
    This is responsible for giving the view a title indicating that which vm this file list is for.
    And configuration of the buttons.
    """
    def __init__(self, listbox, select_button, cancel_button, view=None, window=None):
        """
        @param window, the parent of popup message. so the popup appears at the right place.
        """
        self._model = create_file_listbox(listbox)

        self._view = view
        self._window = window

        bind_click(select_button, self._select)
        bind_click(cancel_button, self._cancel)

        self.refresh_file_list(False)
    
    def _select(self):
        if not self._model.selections:
            selection = b''
        else:
            selection = b'\n'.join(self._model.selections)
        logger.debug('Selected apk files: %s' % selection)
        self._window.ret(selection)

    def _cancel(self):
        """
        Return '' cause the return value has to be a bytes type var.
        """
        logger.debug('Canceled.')
        self._window.ret(b'')
    
    def refresh_file_list(self, popup=True):
        self._model.update()

        if popup:
            show_info(get_text(DONE), self._view)