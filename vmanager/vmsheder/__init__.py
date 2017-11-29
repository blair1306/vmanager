from .api import init

from .api import get_host_n_port, set_host_n_port

from .api import VMStatus
from .api import get_status, get_status_all
from .api import devices
from .api import request_restart
from .api import install, install_all
from .api import uninstall, uninstall_all
from .api import cmd
from .api import get_resolution, get_RAM
from .api import list_installed_packages
from .api import list_apk

from .exceptions import VmshederServerRefused, VmshederServerInternalError, VmshederException