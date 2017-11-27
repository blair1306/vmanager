import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from vmanager.app.file_list import file_list_window

from vmanager.ui import mainloop, create_window


def test_window():
    main_window = create_window('main window')
    window = file_list_window()
    print('return value:\n%s' % window.get())

    mainloop()


if __name__ == '__main__':
    test_window()
