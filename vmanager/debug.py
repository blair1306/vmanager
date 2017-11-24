import sys
import logging

try:
    import pudb as dbg
except ImportError:
    import pdb as dbg


def set_trace(on=True):
    if on:
        dbg.set_trace()


def logging_default_configure(logger):
    """
    Configure a logger with default configuration.
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(filename)s:%(lineno)s %(funcName)-20s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)