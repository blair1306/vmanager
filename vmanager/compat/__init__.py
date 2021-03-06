"""Major python2 python3 compatibility stuff.
"""

import sys

_ver = sys.version_info

is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)


# Conform the differences between python2 and python3 str and bytes and other things.

if is_py2:
    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)
    integer_types = (int, long)


if is_py3:
    builtin_str = str
    bytes = bytes
    str = str
    basestring = (str, bytes)
    numeric_types = (int, float)
    integer_types = (int,)
