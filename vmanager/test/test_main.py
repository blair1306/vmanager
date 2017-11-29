import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


from vmanager.app import main


def test_main():
    main()


if __name__ == '__main__':
    test_main()