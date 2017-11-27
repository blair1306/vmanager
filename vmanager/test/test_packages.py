
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from vmanager.ui import *
from vmanager.app.packages import packages_view#, PackageListBox, build_packages_frame
from vmanager.app.packages import packages_window


def test_packages_view():
    app = App()
    app.set_title('Test Packages View')
    view = packages_view(app)

    app.run()


def test_packages_listbox():
    app = App()
    app.set_title('Test Package Listbox')

    listbox = create_listbox(app)

    package_listbox = PackageListBox('5554', listbox)

    app.run()


def test_packages_window():
    window = packages_window()

    mainloop()



if __name__ == '__main__':
    test_packages_window()
