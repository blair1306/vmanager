from ..ui import *
from .text import get_text, set_ch
from .text import LIST_OF_DEVICES, PLEASE_SELECT_A_DEVICE, \
                  REFRESH, REBOOT_DEVICE


def device_info_view(master):
    view = create_frame(master)

    # The left sub-frame of the whole frame view.
    master = create_frame(view)
    view.title = create_label(master)

    # Just to give a little extra space between the title and the rest of the frame.
    create_label(master)

    view.banner = create_label(master, anchor=None, text=get_text(LIST_OF_DEVICES))
    view.device_listbox = create_listbox(master)

    master = create_frame(view)

    view.select_button = create_button(master, left=True, text=get_text(PLEASE_SELECT_A_DEVICE))
    view.refresh_button = create_button(master, left=True, text=get_text(REFRESH))
    view.reboot_button = create_button(master, left=True, text=get_text(REBOOT_DEVICE))

    return view

