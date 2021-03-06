import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from vmanager.ui import *
from vmanager.test.set_trace import set_trace


def main():
    set_trace()

    app = App()
    frame = create_frame(app)
    frame1 = create_frame(app)
    listbox = create_listbox(app)
    button = create_button(frame)
    toplevel = create_toplevel()
    message = create_message(master=None, text="hello")

    entry = create_entry(frame)
    scrollbar = create_scrollbar(frame1)
    label = create_label(frame1)

    app.run()

def test_custom_listbox():
    app = App()
    frame = create_frame(app)
    
    listbox = create_listbox(frame)
    options = ['5554', '5555']
    listbox.update_options(options)

    app.run()


def test_listbox():
    app = App()
    frame = create_frame(app)

    import Tkinter
    listbox = Tkinter.Listbox(frame)
    listbox.pack()

    options = ['one', 'two', 'three']
    for option in options:
        listbox.insert(Tkinter.END, option)

    app.run()


if __name__ == '__main__':
    main()
