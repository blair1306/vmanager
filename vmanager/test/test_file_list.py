import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from vmanager.app.file_list import file_list_window

from vmanager.ui import mainloop


def test_view():
    window = file_list_window()

    mainloop()


if __name__ == '__main__':
    test_view()