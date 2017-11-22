from ..ui import *
from .text import get_text, set_ch, set_en, set_lan, get_lan
from .text import LIST_OF_DEVICES, PLEASE_SELECT_A_DEVICE, \
                  REFRESH, REBOOT_DEVICE, SELECT
from .text import DEVICE_ID, RESOLUTION, RAM_SIZE_IN_GB, STATUS
from .text import get_text, DONE

from ..debug import set_trace
from ..ui import bind_double_click, bind_click
from ..ui import show_info, show_warning, show_error

from ..vmsheder import devices, get_status, VMStatus
from ..vmsheder import get_resolution, get_RAM

import logging
from logging.config import fileConfig

# fileConfig('logging_config.ini')

logger = logging.getLogger(__name__)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(filename)s:%(lineno)s %(funcName)-20s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# globbal toggle for testing-related stuff.
testing = True


def build_device_info_frame(root):
    """
    Helper function to create a pre-configured frame ready to use.
    Get device info frame.
    """
    view = device_info_view(root)
    view.controller = Controller(view.listbox,
            view.refresh_button, view.reboot_button, view.select_button)

    return view


def device_info_view(master):
    """
    Create the device info view.
    which has a listbox slot, a select button slot, a refresh button slot and
    a reboot button slot to be binded by other part of the code.
    """
    view = create_frame(master)

    # The left sub-frame of the whole frame view.
    master = create_frame(view)
    view.title = create_label(master)

    # Just to give a little extra space between the title and the rest of the frame.
    create_label(master)

    create_label(master, anchor=None, text=get_text(LIST_OF_DEVICES))
    view.listbox = create_listbox(master)

    master = create_frame(view)

    view.select_button = create_button(master, left=True, text=get_text(SELECT))
    view.refresh_button = create_button(master, left=True, text=get_text(REFRESH))
    view.reboot_button = create_button(master, left=True, text=get_text(REBOOT_DEVICE))

    return view


class DeviceInfo(object):
    """
    info of a virtual device such as it's screen resolution, RAM size etc.
    """
    def __init__(self, _id):
        """
        @param id: the id of vm.
        """
        self._id = _id
        self._res = "0x0"
        self._RAM_GB = 0
        self._status = VMStatus()

        self.init()

    def init(self):
        """
        Get the real info about this device's status through vmsheder.
        """
        if testing:
            # For testing when vmsheder server isn't available.
            get_status = lambda vm_id: VMStatus()
            get_resolution = lambda vm_id: "0x0"
            get_RAM = lambda vm_id: 0

        self._res = get_resolution(self._id)
        self._RAM_GB = get_RAM(self._id)
        self._status = get_status(self._id)

    def __repr__(self):
        return '[%s: %s] (%s: %s) (%s: %sGB) (%s: %s)' % (
                get_text(DEVICE_ID), self._id,
                get_text(RESOLUTION), self._res,
                get_text(RAM_SIZE_IN_GB), self._RAM_GB,
                get_text(STATUS), self._status
                )

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        return self._status

    @property
    def ram(self):
        """
        return the device's RAM in GBs
        """
        return self._RAM_GB


class DeviceListBox(object):
    """
    The actual model of this gui.
    Which has a reference to an actual gui listbox that is used to display the list of vms.
    """
    def __init__(self, listbox):
        """
        @param listbox is the gui listbox used to display data.
        """
        # The listbox data model that is used to show the gui interface.
        self._listbox = listbox

        logger.debug(
            "self._listbox is listbox: %s" % (id(listbox) == id(self._listbox))
        )
        
        # The actual list of DeviceInfo.
        self._device_list = None

    def update_device_list(self):
        # update the connected devices list.
        self._device_list = DeviceListBox._get_device_info_list()

        # Update the listbox options.
        options = [repr(device_info) for device_info in self._device_list]
        self._listbox.update_options(options)

        # Select the default one (the first one if there is one)
        self._listbox.select_default()

    def get_id(self):
        """
        Get the id of the device currently under selection.
        return None if no device is under selection or no device is in
        the list.
        """
        index = self._listbox.get_selection()

        if index is None:
            id = None
        else:
            id = self._device_list[index].id

        return id

    def set_id(self, id):
        # Invalid to set id.
        raise NotImplementedError()

    id = property(get_id, set_id)

    @staticmethod
    def _get_device_info_list():
        """
        Get a list of DeviceInfo 
        """
        logger.debug("")
        
        device_info_list = []

        if testing:
            devices = lambda: ['5554', '5556']

        for device_id in devices():
            device_info = DeviceInfo(device_id)
            device_info_list.append(device_info)
        
        return device_info_list


class Controller(object):
    """
    Provide three functionalities.
    refresh, reboot, and select a device.
    """
    def __init__(self, listbox,
                 refresh_button, reboot_button, select_button):
        """
        @param device_listbox is the listbox that is going to show info about
        the devices detected for further operations.
        @param refresh_button, reboot_button, select_button are the buttons
        that will be binded with their respective functionalities.
        """
        self._model = DeviceListBox(listbox)

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
        # Show a pop up message indicating that refresh is done.
        self._model.update_device_list()

        if popup:
            show_info(get_text(DONE))

    def reboot_device(self):
        show_info(get_text(DONE))

    def select_device(self, event=None):
        """
        Select a device and create a new window for package management.
        @param event is a callback convention.
        """
        logger.debug("event=%s" % repr(event))

        show_info(get_text(DONE))

    def _selected_id(self):
        """
        Get the id of virtual device currently under selection.
        """
        return self._model.id