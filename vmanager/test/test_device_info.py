import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from vmanager.ui import *
from vmanager.app.device_info_views import device_info_view
from vmanager.app.device_info_models import DeviceInfo


def test_view():
    app = App()

    f = device_info_view(app)

    app.run()


def test_model():
    device = DeviceInfo('5554', '600x800', '1', 'alive')
    print device
    device.id = '5555'
    print device


def main():
    test_model()


if __name__ == '__main__':
    main()
