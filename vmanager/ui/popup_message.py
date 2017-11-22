from .compat import MessageBox


def show_info(message, *args, **kwargs):
    """
    Show a pop-up message.
    """
    MessageBox.showinfo(message=message, *args, **kwargs)


def show_warning(message, *args, **kwargs):
    """
    Show a pop-up warning message.
    """
    MessageBox.showwarning(message=message, *args, **kwargs)


def show_error(message, *args, **kwargs):
    """
    Show a pop-up error message.
    """
    MessageBox.showerror(message=message, *args, **kwargs)
