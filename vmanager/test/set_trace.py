import sys

try:
    from pudb import set_trace as _set_trace
except ImportError:
    from pdb import set_trace as _set_trace


def set_trace():
    if b"debug" in  sys.argv:
        _set_trace()
    
