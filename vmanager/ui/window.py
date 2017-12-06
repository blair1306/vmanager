"""This module provides a window abstraction over tkinter's window system.
just call create_window() whereever needed. and mainloop() at the end of the program.
"""

from .compat import tk, ttk, tkFont
from ..compat import bytes
from . import create_toplevel
from .widgets import Toplevel

from logging import getLogger
from ..debug import logging_default_configure

logger = getLogger(__name__)
logging_default_configure(logger)


# There can only be one main window, but there can be many other windows.
_main_window = None


def create_window(title=''):
    """
    Create a new window.
    """
    global _main_window

    if not _main_window:
        _main_window = _create_root(title)
        return _main_window
    
    return create_toplevel(title=title)


def create_ret_window(title=''):
    """
    Create a special kind of window that can return values when it's destroyed.
    """
    return RetToplevel(title)


class RetToplevel(Toplevel):
    """
    Toplevel that can return string value after it's being destroyed.
    """
    def __init__(self, title, master=None, *args, **kwargs):
        Toplevel.__init__(self, master, *args, **kwargs)
        # Normal string wouldn't survive after this toplevel is destroyed.
        self.ret_var = tk.StringVar()
    
    def ret(self, value):
        """
        Return a string value to a nother window that calls get on this window.
        """
        assert isinstance(value, bytes)
        logger.debug('return: %s' % value)
        self.ret_var.set(value)
        self.destroy()
    
    def get(self):
        """
        Get the returned string value.
        This will block until self.ret gets called by itself.
        """
        logger.debug('waiting...')
        self.wait_window()
        logger.debug('done waiting.')
        return self.ret_var.get()
        

def _create_root(title):
    """
    Create the root window.
    """
    # The first window, which is the main window.
    _main_window = tk.Tk()

    _main_window.title(title)

    # Not resizable
    _main_window.resizable(False, False)

    default_font = tkFont.nametofont('TkDefaultFont')
    default_font.configure(size=13)

    # TODO: here I use // to achieve compatibility between python2 and python3.
    # Is there a better way?
    x = (_main_window.winfo_screenwidth() - _main_window.winfo_reqwidth()) // 3
    y = (_main_window.winfo_screenheight() - _main_window.winfo_reqheight()) // 3

    # reposition the window. So that it appears at a little left and up to the center of the screen.
    # 1 / 3 to the left and 1 / 3 to the top to be exact.
    _main_window.geometry("+{}+{}".format(x, y))

    # Use ttk to beautify the window.
    _main_window.style =ttk.Style()
    _main_window.style.theme_use('classic')

    return _main_window


def mainloop():
    """
    Start the mainloop.
    """
    if not _main_window:
        raise RuntimeError('Create At Least One Window Before Calling This.')
    
    _main_window.mainloop()