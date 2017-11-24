"""
This module provides a window that is used to manage all packages installed on a vm.
"""

from ..ui import create_frame, create_label, create_button, create_entry
from ..ui import create_listbox, create_ms_listbox, create_scrollbar, create_toplevel
from ..ui import bind_click, set_text
from ..ui import show_info, show_warning, show_error, autoresize
from ..ui import create_window

from .text import get_text
from .text import INSTALL, UNINSTALL, REFRESH, DEVICE_SELECTED, DONE, PLEASE_SELECT_AT_LEAST_ONE_PACKAGE_TO_UNINSTALL

from ..vmsheder import list_installed_packages

import logging
from ..debug import logging_default_configure


logger = logging.getLogger(__name__)
logging_default_configure(logger)


TITLE = 'Package Management'


def packages_window(vm_id='6666'):
    """
    A ready to use window.
    """
    window = create_window(TITLE)
    build_packages_frame(window, vm_id)

    return window


def build_packages_frame(master, vm_id='6666'):
    """
    Return a ready to use frame with everythng pre-configured.
    @param vm_id: the vm_id whose packages this frame is going to manage.
    """
    view = packages_view(master)
    view.controller = Controller(vm_id, view.title, view.listbox,
                            view.install_button, view.uninstall_button, view.refresh_button, view)
    return view


def packages_view(master):
    """ The V in the MVC.
    The view that provides a listbox for showing packages installed on a given vm, and buttons
    for installing new packages, uninstalling selected packages, refreshing the installed packages list,
    and a search box for searching a specific package or a bunch packages that match the search phrase.
    """
    view = create_frame(master)

    # The top sub-frame of the whole frame for displaying the packages installed on a vm.
    master = create_frame(view)

    # This is the title that shows "Package Management for vm_id", and will be later configured.
    view.title = create_label(master)

    view.listbox = create_ms_listbox(master)
    autoresize(view.listbox, "width")

    # The bottom sub-frame for buttons.
    master = create_frame(view)

    view.install_button = create_button(master, text=get_text(INSTALL), left=True)
    view.uninstall_button = create_button(master, text=get_text(UNINSTALL), left=True)
    view.refresh_button = create_button(master, text=get_text(REFRESH), left=True)

    return view


class PackageListBox(object):
    """ The M in the MVC.
    This is a listbox that is used to show packages installed in a given vm.
    which provides Update the list of packages installed, get a list of packages
    currently selected.
    """
    def __init__(self, vm_id, listbox):
        self._vm_id = vm_id
        self._listbox = listbox

        self._package_list = None
    
    def update_package_list(self):
        """
        Update the package list of currently installed packages on self._vm_id.
        """
        self._package_list = list_installed_packages(self._vm_id)
        # Update the actual gui listbox.
        self._listbox.update_options(self._package_list)
    
    def get_selected_packages(self):
        """
        Get a list of currelty selected packages.
        """
        index_list = self._listbox.get_selected_index_list()
        package_list = [self._package_list[index] for index in index_list]

        return package_list


class Controller(object):
    """ The C in the MVC model.
    This is responsible for giving the view a title (the text indicates that what vm this package management window is for)
    , in the form of "Package Management for %s" % vm_id.
    Also needs to configure the buttons in the view.
    """
    def __init__(self, _vm_id, title, _listbox, install_button, uninstall_button, refresh_button, window=None):
        """
        @param _vm_id: id of the vm whose packages are to be managed.
        @param title: the title to be configured.
        """
        # Set the text for the title.
        set_text(title, "%s: %s" % (get_text(DEVICE_SELECTED), _vm_id))

        self._model = PackageListBox(_vm_id, _listbox)

        # Some gui show popup relative to it's parent and if it's parent isn't specified, it will show
        # popup relative to the root of the gui which is annoying, cause it's easily overlooked.
        # To solve this, we provide the parent manually.
        self._window = window

        # Configure the buttons.
        bind_click(install_button, self.install_packages)
        bind_click(uninstall_button, self.uninstall_packages)
        bind_click(refresh_button, self.refresh_package_list)

        self.refresh_package_list(False)
    
    def install_packages(self):
        """
        Opens a new window to let user to select from a list of packages to install.
        """
        logger.debug('')

        show_info(get_text(DONE), parent=self._window)
        
        # Refresh the list to see the effect.
        self.refresh_package_list(False)
    
    def uninstall_packages(self):
        """
        Uninstall the packages under selection.
        """
        uninstall_list = self._model.get_selected_packages()
        if not uninstall_list:
            show_warning(get_text(PLEASE_SELECT_AT_LEAST_ONE_PACKAGE_TO_UNINSTALL), parent=self._window)
            return

        logger.debug("Packages to uninstall: %s" % uninstall_list)

        show_info(get_text(DONE), parent=self._window)

        # Refresh the list to see the effect.
        self.refresh_package_list(False)
    
    # TODO: figure this out.
    @staticmethod
    def refresh_when_done(func):
        """
        Decorator for refreshing the installed list when an action to the list is done.
        """
        def wrapper():
            func()
            self.refresh_package_list(False)
        return wrapper

    def refresh_package_list(self, popup=True):
        """
        Refresh the list of currently installed packages.
        """
        self._model.update_package_list()

        if popup:
            show_info(get_text(DONE), parent=self._window)