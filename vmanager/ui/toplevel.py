from .compat import tk


class Toplevel(tk.Toplevel):
    def __init__(self, master=None, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
