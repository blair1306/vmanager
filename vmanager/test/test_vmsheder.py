from __future__ import absolute_import

import sys
import os
# so we can use without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from vmanager.vmsheder import *
from vmanager.compat import bytes
from vmanager.test.set_trace import set_trace

cool_apk = b"/home/jon/Downloads/com.coolapk.market-7.9.7-1708181.apk"
cool_package = b"com.coolapk.market"


def test(func, arg=[]):
    print(b"")
    print(func.__name__)
    if arg:
        if isinstance(arg, str):
            print(func(arg))
        elif type(arg) is list:
            print(func(*arg))
    else:
        print(func())
    print(b"")


def main():
    set_trace()
    test(get_status, [b"5554"])

    test(get_status_all)

    test(devices)

    test(request_restart, [b"5554"])

    test(install, [b"5554", cool_apk])

    test(install_all, cool_apk)

    test(get_status_all)

    test(uninstall, [b"5554", cool_package])

    test(uninstall_all, cool_package)

    test(cmd, [b"5554", b"ls"])


if __name__ == "__main__":
   main()
