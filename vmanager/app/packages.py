"""
This module provides a window that is used to manage the packages installed on a vm.
"""

import logging

from ..ui import create_frame, create_label, create_button, create_entry
from ..ui import create_listbox, create_ms_listbox, create_scrollbar, create_toplevel
from ..ui import bind_click, set_text
from ..ui import show_info, show_warning, show_error, autoresize, ask_ok_cancel
from ..ui import create_window

from ..text import get_text
from ..text import INSTALL, UNINSTALL, REFRESH, DEVICE_SELECTED, DONE, PLEASE_SELECT_AT_LEAST_ONE_PACKAGE
from ..text import INSTALL_THESE_PACKAGES, CANCELLED, UNINSTALL_THESE_PACKAGES
from ..text import PACKAGE_MANAGEMENT

from ..vmsheder import list_installed_packages, install

from ..debug import logging_default_configure

from .dynamic_listbox import DynamicListBox

from .file_list import file_list_window


logger = logging.getLogger(__name__)
logging_default_configure(logger)


TITLE = get_text(PACKAGE_MANAGEMENT)


def packages_window(vm_id='6666'):
    """
    A ready to use window.
    @param vm_id
    """
    window = create_window(TITLE)
    build_packages_frame(window, vm_id)

    return window


def build_packages_frame(master, vm_id, *args, **kwargs):
    """
    Return a ready to use frame with everythng pre-configured.
    @param vm_id: the vm_id whose packages this frame is going to manage.
    """
    view = packages_view(master, vm_id, *args, **kwargs)
    view.controller = Controller(view.listbox,
                            view.install_button, view.uninstall_button, view.refresh_button, view, vm_id)
    return view


def packages_view(master, vm_id, *args, **kwargs):
    """ The V in the MVC.
    The view that provides a listbox for showing packages installed on a given vm, and buttons
    for installing new packages, uninstalling selected packages, refreshing the installed packages list,
    and a search box for searching a specific package or a bunch packages that match the search phrase.
    """
    view = create_frame(master)

    # The top sub-frame of the whole frame for displaying the packages installed on a vm.
    master = create_frame(view)

    # This is the title that shows "Device Selected: vm_id", and will be later configured.
    view.title = create_label(master, text="%s: %s" % (get_text(DEVICE_SELECTED), vm_id))

    view.listbox = create_ms_listbox(master)
    autoresize(view.listbox, "width")

    # The bottom sub-frame for buttons.
    master = create_frame(view)

    view.install_button = create_button(master, text=get_text(INSTALL), left=True)
    view.uninstall_button = create_button(master, text=get_text(UNINSTALL), left=True)
    view.refresh_button = create_button(master, text=get_text(REFRESH), left=True)

    return view


def create_package_listbox(vm_id, listbox):
    """ The M in the MVC.
    This is a listbox that is used to show packages installed in a given vm.
    which provides Update the list of packages installed, get a list of packages
    currently selected.
    """
    logger.debug('vm_id: %s' % vm_id)

    def update_func():
        return list_installed_packages(vm_id)
    
    package_listbox = DynamicListBox(update_func, listbox)

    return package_listbox


class Controller(object):
    """ The C in the MVC model.
    This is responsible for giving the view a title (the text indicates that what vm this package management window is for)
    , in the form of "Package Management for %s" % vm_id.
    Also needs to configure the buttons in the view.
    """
    def __init__(self, _listbox, install_button, uninstall_button, refresh_button, window=None, vm_id='6666'):
        """
        @param _vm_id: id of the vm whose packages are to be managed.
        @param title: the title to be configured.
        """
        self._vm_id = vm_id

        self._model = create_package_listbox(vm_id, _listbox)

        # Some gui show popup relative to it's parent and if it's parent isn't specified, it will show
        # popup relative to the root of the gui which is annoying, cause it's easily overlooked.
        # To solve this, we provide the parent manually.
        self._window = window

        # Configure the buttons.
        bind_click(install_button, self.install_packages)
        bind_click(uninstall_button, self.uninstall_packages)
        bind_click(refresh_button, self.refresh_package_list)

        self.refresh_package_list(False)
    
    def refresh_when_done(func):
        """
        Decorator for refreshing the installed list when an action to the list is done.
        """
        def wrapper(self):
            func(self)
            self.refresh_package_list(False)
        return wrapper

    @refresh_when_done
    def install_packages(self):
        """
        Opens a new window to let user to select from a list of packages to install.
        """
        selected_apk_files = file_list_window(self._vm_id).get()
        logger.debug('Selected apk files:\n%s' % selected_apk_files)

        if not selected_apk_files:
            show_info(get_text(PLEASE_SELECT_AT_LEAST_ONE_PACKAGE), parent=self._window)
            return

        if ask_ok_cancel('%s?: %s' % (get_text(INSTALL_THESE_PACKAGES), selected_apk_files), parent=self._window):
            # TODO: change _window to _view wherever possible.
            install(self._vm_id, selected_apk_files)
            show_info(get_text(DONE), parent=self._window)
        else:
            show_info(get_text(CANCELLED), parent=self._window)

        
    @refresh_when_done
    def uninstall_packages(self):
        """
        Uninstall the packages under selection.
        """
        uninstall_list = self._model.selections
        if not uninstall_list:
            show_warning(get_text(PLEASE_SELECT_AT_LEAST_ONE_PACKAGE), parent=self._window)
            return

        logger.debug("Packages to uninstall: %s" % uninstall_list)

        if ask_ok_cancel('%s?: %s' % (get_text(UNINSTALL_THESE_PACKAGES), uninstall_list), parent=self._window):
            show_info(get_text(DONE), parent=self._window)
        else:
            show_info(get_text(CANCELLED), parent=self._window)


    def refresh_package_list(self, popup=True):
        """
        Refresh the list of currently installed packages.
        """
        logger.debug('')

        self._model.update()

        if popup:
            show_info(get_text(DONE), parent=self._window)