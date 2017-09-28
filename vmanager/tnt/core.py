### tnt stands for two and three.
### python2 and python3 compatibility functions.
### Include this in the top of every file.
from __future__ import absolute_import, division, print_function, unicode_literals

from os.path import abspath, dirname, join
import sys


module_root = join(abspath(__file__), r"..")
sys.path.append(module_root)


def pythree():
    """Returns true if runs with a python3 interpreter.
    The interpreter should be at least 3.5 or 2.7 and higher.
    """
    if sys.version_info >= (3, 5):
            return True
    elif sys.version_info >= (2, 7):
        return False
    else:
        raise


def is_bytes_str(s):
    if pythree():
        if isinstance(s, bytes):
            return True
        else:
            return False
    else:
        # python2
        if isinstance(s, str):
            return True
        else:
            return False

