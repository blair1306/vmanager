from .compat import tk, ttk


class Frame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        borderwidth = 3

        if "borderwidth" in kwargs:
            borderwidth = kwargs["borderwidth"]
            del kwargs["borderwidth"]

        # ttk.Frame.__init__(self, master, borderwidth=borderwidth, padx=padx, pady=pady, *args, **kwargs)
        ttk.Frame.__init__(self, master, borderwidth=borderwidth, *args, **kwargs)

        self.pack()


class FrameLeft(Frame):
    def __init__(self, master, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.pack(side=tk.LEFT)


class ListBox(tk.Listbox):
    """
    A Box shaped ui element contains a list of selectable items.
    a single-element listbox contains only one item.
    a multiple-element listbox contains one or more than one items.
    """
    SINGLE = tk.SINGLE
    MULTIPLE = tk.MULTIPLE

    END = tk.END

    def __init__(self, master, selectmode, *args, **kwargs):
        tk.Listbox.__init__(self, master, selectmode=selectmode, *args, **kwargs)
        self._selectmode = selectmode

    def update_options(self, options):
        self._delete_all_options()
        self._append_options(options)

    def get_selections(self):
        """
        return a list of currently selected options.
        """
        indices = self.curselection()
        if not indices:
            return []

        selections = [self.get(i) for i in indices]

        return selections

    def get_selection(self):
        # return None if no item is in the list or is under selection.
        assert self._selectmode is ListBox.SINGLE

        selections = self.get_selections()

        if not selections:
            return None

        return selections[0]

    def select_default(self):
        """
        select the default item, which is the firsssst item.
        """
        self.select_set(0)

    def _append_options(self, options):
        if not options:
            return

        for option in options:
            self.insert(ListBox.END, option)

    def _delete_all_options(self):
        self.delete(0, ListBox.END)


class Toplevel(tk.Toplevel):
    def __init__(self, master=None, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
