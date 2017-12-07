""" This module provides a interface which abstracts away details of the GUI system
underneath, so different GUI systems such as tkinter, qt etc. can be used without
changing the bulk of the program.
"""

from .adapter import create_frame, create_button, create_label, create_message, \
        create_listbox, create_ms_listbox, create_entry, create_toplevel, create_scrollbar
from .adapter import bind_double_click, bind_click, resize, set_text, autoresize
from .popup_message import show_info, show_warning, show_error, ask_ok_cancel
from .window import create_window, mainloop, create_ret_window


__all__ = ["create_frame", "create_button", "create_label", "create_message",
        "create_listbox", "create_ms_listbox", "create_entry", "create_toplevel", "create_scrollbar",
        "bind_double_click", "bind_click", "resize", "set_text", "autoresize",
        "show_info", "show_warning", "show_error", "ask_ok_cancel",
        "create_window", "mainloop", "create_ret_window"
        ]
