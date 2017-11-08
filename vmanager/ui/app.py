from .compat import tk, tkFont, ttk
from ..debug import set_trace


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.resizable(False, False)

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=13)

        # TODO: here I use // to achieve compatibility between python2 and python3. Is there a better way?
        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) // 3
        y = (self.winfo_screenheight() - self.winfo_reqheight()) // 3

        set_trace(False)

        # reposition the window.
        self.geometry("+{}+{}".format(x, y))

        self.style =ttk.Style()
        self.style.theme_use('classic')


    def set_title(self, title):
        self.title(title)

    def run(self):
        self.mainloop()

