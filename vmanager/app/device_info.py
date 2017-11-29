"""
This module provides the device management window.
"""

from ..ui import *

from ..text import get_text, set_ch, set_en, set_lan, get_lan
from ..text import LIST_OF_DEVICES, PLEASE_SELECT_A_DEVICE, \
                  REFRESH, REBOOT_DEVICE, SELECT
from ..text import DEVICE_ID, RESOLUTION, RAM_SIZE_IN_GB, STATUS
from ..text import get_text, DONE
from ..text import DEVICE_ADMINISTRATION, DOUBLE_CLICK_ON_DEVICE_LIST

from ..debug import set_trace, logging_default_configure

from ..ui import bind_double_click, bind_click
from ..ui import show_info, show_warning, show_error
from ..ui import autoresize
from ..ui import create_window

from .packages import packages_window

from ..vmsheder import devices, get_status, VMStatus
from ..vmsheder import get_resolution, get_RAM
from ..vmsheder import VmshederServerInternalError, VmshederServerRefused
from .vmsheder_exception_handler import catch_display_vmsheder_exception

import logging
# from logging.config import fileConfig

from .. import TESTING

# fileConfig('logging_config.ini')

logger = logging.getLogger(__name__)

logging_default_configure(logger)


TITLE = get_text(DEVICE_ADMINISTRATION)


def device_info_window():
    """
    A ready to use window
    """
    window = create_window(TITLE)
    build_device_info_frame(window)

    return window


def build_device_info_frame(master):
    """
    Helper function to create a pre-configured frame ready to use.
    Get device info frame.
    """
    view = device_info_view(master)
    view.controller = Controller(view.listbox,
            view.refresh_button, view.reboot_button, view.select_button, view)

    return view


def device_info_view(master):
    """
    Create the device info view.
    which has a listbox slot, a select button slot, a refresh button slot and
    a reboot button slot to be binded by other part of the code.
    """
    view = create_frame(master)

    # The top sub-frame of the whole frame view.
    master = create_frame(view)

    create_label(master, anchor=None, text=get_text(LIST_OF_DEVICES))

    # Just to give a little extra space between the title and the listbox.
    create_label(master)
    create_label(master, text=get_text(DOUBLE_CLICK_ON_DEVICE_LIST))

    view.listbox = create_listbox(master)
    autoresize(view.listbox, "width")

    # The bottom sub-frame of the whole frame view.
    master = create_frame(view)

    view.select_button = create_button(master, left=True, text=get_text(SELECT))
    view.refresh_button = create_button(master, left=True, text=get_text(REFRESH))
    view.reboot_button = create_button(master, left=True, text=get_text(REBOOT_DEVICE))

    return view


def get_device_info(vm_id):
    """
    Get the device info of a given vm_id.
    Return the DeviceInfo object of the given vm_id.
    """
    if TESTING:
        return DeviceInfo(vm_id)

    # Get the real info through vmsheder.
    status, resolution, ram_gb = get_status(vm_id), get_resolution(vm_id), get_RAM(vm_id)
    
    return DeviceInfo(vm_id, resolution, ram_gb, status)


def get_all_device_infos():
    """
    Get the list of device info of all vms on this machine.
    """
    device_id_list = devices() if not TESTING else ['5555', '5557']
    all_device_info_list = []

    for _id in device_id_list:
        device_info = DeviceInfo(_id)
        all_device_info_list.append(device_info)
    
    return all_device_info_list


class DeviceInfo(object):
    """
    info of a virtual device such as it's screen resolution, RAM size etc.
    id, status, resolution and RAM can be accessed by accesing it's member variables,
    i.e. device_info.id, device_info.status, device_info.resolution and device_info.RAM etc.
    """
    def __init__(self, _id='6666', _resolution="0x0", _RAM_GB=0, _status=VMStatus()):
        """
        @param id: the id of vm.
        """
        self._id = _id
        self._resolution = _resolution
        self._RAM_GB = _RAM_GB
        self._status = _status

    def __repr__(self):
        return '[%s: %s] (%s: %s) (%s: %s) (%s: %s GB)' % (
                get_text(DEVICE_ID), self._id,
                get_text(STATUS), self._status,
                get_text(RESOLUTION), self._resolution,
                get_text(RAM_SIZE_IN_GB), self._RAM_GB,
                )
    
    def __len__(self):
        return len(repr(self))

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @property
    def resolution(self):
        return self._resolution

    @property
    def RAM(self):
        """
        return the device's RAM in GBs
        """
        return self._RAM_GB


class DeviceListBox(object):
    """
    The actual model of this gui.
    which provides the following functions. Update the vm id currently under selection.
    Update the device info list of vms curently connected to this pc.
    """
    def __init__(self, listbox):
        """
        @param listbox is the gui listbox used to display data.
        """
        # The listbox data model that is used to show the gui interface.
        self._listbox = listbox

        # The actual list of DeviceInfo.
        self._device_info_list = None

    def update_device_info_list(self):
        # update the connected devices list.
        self._device_info_list = get_all_device_infos()

        # Update the listbox options.
        options = [repr(device_info) for device_info in self._device_info_list]
        self._listbox.update_options(options)

    def get_id(self):
        """
        Get the id of the device currently under selection.
        return None if no device is under selection or no device is in
        the list.
        """
        indexes = self._listbox.get_selected_index_list()

        if not indexes:
            id = None
        else:
            index = indexes[0]
            id = self._device_info_list[index].id

        logger.debug("vm_id under current selection: %s" % id)

        return id

    def set_id(self, id):
        # Invalid to set id.
        raise NotImplementedError()

    id = property(get_id, set_id)

    def __len__(self):
        """
        how many device info are in this.
        """
        return len(self._device_info_list)

    def select_default(self):
        """
        Select the first one if there is one.
        """
        return self._listbox.select_default()


class Controller(object):
    """
    Provide three functionalities.
    refresh, reboot, and select a device.
    """
    def __init__(self, listbox,
                 refresh_button, reboot_button, select_button, window=None):
        """
        @param device_listbox is the listbox that is going to show info about
        the devices detected for further operations.
        @param refresh_button, reboot_button, select_button are the buttons
        that will be binded with their respective functionalities.
        @param window: use as parent of popup messaegs.
        """
        self._model = DeviceListBox(listbox)

        self._window = window

        # bind refresh button to it's handler
        bind_click(refresh_button, self.refresh_device_list)

        bind_click(reboot_button, self.reboot_device)
        bind_click(select_button, self.select_device)

        # bind the device listbox to select so when the listbox gets
        # a double click that coresponding device gets selected.
        bind_double_click(listbox, self.select_device)

        # Don't want a pop up when the app is under initialzation.
        self.refresh_device_list(False)

    def refresh_device_list(self, popup=True):
        self._refresh_device_list()

        # Select the default one (the first one if there is one)
        self._model.select_default()

        # Show a pop up message indicating that refresh is done.
        if popup:
            show_info(get_text(DONE), parent=self._window)
    
    @catch_display_vmsheder_exception
    def _refresh_device_list(self):
        self._model.update_device_info_list()

    def reboot_device(self):
        logger.debug("device selected: %s" % self.selected_id)
        show_info(get_text(DONE), parent=self._window)

    def select_device(self, event=None):
        """
        Select a device and create a new window for package management.
        @param event is a callback convention.
        """
        logger.debug("event=%s" % repr(event))
        logger.debug("device selected: %s" % self.selected_id)

        packages_window(self.selected_id)

    @property
    def selected_id(self):
        """
        Get the id of virtual device currently under selection.
        """
        return self._model.id