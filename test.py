import sys
from vmsheder import get_status, devices, request_restart

from pudb import set_trace


def test(func, arg=None):
    print ""
    print func.__name__
    if arg:
        print func(arg)
    else:
        print func()
    print ""


def main():
    test(get_status, "5554")

    test(devices)

    test(request_restart, "5554")


if __name__ == "__main__":
    if "debug" in sys.argv:
        set_trace()
    main()
