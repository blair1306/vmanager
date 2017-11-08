try:
    import pudb as dbg
except ImportError:
    import pdb as dbg


def set_trace(on=True):
    if on:
        dbg.set_trace()
