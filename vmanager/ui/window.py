# This module provides a window abstraction over tkinter's gui system.
# Just call create_window() whereever needed. and mainloop() at the end of the program.

from .compat import tk, ttk, tkFont
from . import create_toplevel


# There can only be one main window, but there can be many other windows.
_main_window = None


def create_window(title=''):
    """
    Create a new window.
    """
    global _main_window

    if not _main_window:
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

    # There is a main_window already, just create a toplevel as a window.
    new_window = create_toplevel(title=title)
    new_window.resizable(False, False)

    return new_window


def mainloop():
    """
    Start the mainloop.
    """
    if not _main_window:
        raise RuntimeError('Create At Least One Window Before Calling This.')
    
    _main_window.mainloop()