"""This module provides a easy-to-use interface to read from a configuration file.
This configuration reader will read from a file named config.ini in the current directory.
"""


from .compat import builtin_str, is_py2, is_py3
import os
import logging
from .debug import logging_default_configure

if is_py2:
    from ConfigParser import SafeConfigParser
elif is_py3:
    from configparser import SafeConfigParser

logger = logging.getLogger(__name__)
logging_default_configure(logger)


CONFIG_FILE = 'config.ini'
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), CONFIG_FILE)


class ConfigReader(object):
    """A basic configuration file reader
    """
    def __init__(self, config_file):
        self._configparser = SafeConfigParser()
        self._configparser.read(config_file)
    
    def get(self, name):
        """Get an option of a section.
        @param name: in the format of 'section_name.option_name'.
        Seperated by a single dot(.)
        """
        return self._get(name, None)

    def get_int(self, name):
        """Get an option of a section as an int.
        """
        return self._get(name, int)

    def get_boolean(self, name):
        """Get an option of a section as a boolean.
        """
        return self._get(name, bool)
    
    def _get(self, name, type):
        assert isinstance(name, builtin_str)
        assert name.count('.') == 1
        section, option = name.split('.')

        if type is None:
            r = self._configparser.get(section, option)
        elif type is int:
            r = self._configparser.getint(section, option)
        elif type is bool:
            r = self._configparser.getboolean(section, option)
        else:
            raise NotImplementedError('get option of type other than int isn\'t implmented')

        logger.debug(
            'read from %s: section: %s, option: %s, value: %s'
            % (CONFIG_FILE_PATH, section, option, r)
        )
        return r


config_reader = ConfigReader(CONFIG_FILE_PATH)