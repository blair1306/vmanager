from .compat import tk, tkFont, ttk


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.resizable(False, False)

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=13)

        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 3
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 3

        # reposition the window.
        self.geometry("+{}+{}".format(x, y))

        self.style =ttk.Style()
        self.style.theme_use('classic')


    def set_title(self, title):
        self.title(title)

    def run(self):
        self.mainloop()
