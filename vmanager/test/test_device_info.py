import sys
import os
import pytest
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from vmanager.ui import *
from vmanager.app.device_info import device_info_view
from vmanager.app.device_info import DeviceInfo, DeviceListBox
from vmanager.app.device_info import Controller
from vmanager.app.device_info import build_device_info_frame
from vmanager.debug import set_trace


def test_view():
    app = App()

    f = device_info_view(app)

    app.run()


def test_model():
    device = DeviceInfo('5554')
    assert device.id == '5554'

    with pytest.raises(AttributeError):
        device.id = '5555'

    device1 = copy.copy(device)
    device2 = copy.copy(device)


def test_controller():
    device_info_list = Controller._get_device_info_list()
    print(device_info_list)


def test_build():
    app = App()
    app.set_title('VManager')
    # set_trace()
    frame = build_device_info_frame(app)
    app.run()


def main_test():
    test_build()


if __name__ == '__main__':
    main_test()