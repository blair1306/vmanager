"""
This module provides the api for use outside of this module.

"""


from __future__ import absolute_import

# Get info about the status of a virtual machine running in the remote server

import socket
import re
import errno

from .packet import create_status, create_status_all, create_devices
from .packet import create_restart, create_install, create_install_all
from .packet import create_uninstall, create_uninstall_all, create_cmd
from .packet import create_list_apk, create_list_installed_packages
from .packet import send_packet, read_packets, get_data
from .packet import check_header
from .packet import Header

from .exceptions import VmshederServerNotFound, VmshederServerInternalError, VmshederServerRefused
from .common import set_host_n_port
from .common import g_host, g_port      # TODO: this is a structural problem of this module


def init(_host=None, _port=None):
    """ Init the vmsheder module. Use the default ones if no arguments is supplied.
    Raise exceptions if init fails.
    """
    set_host_n_port(_host, _port)
    get_status_all()


class VMStatus(object):
    ALIVE = 0
    FBV_IS_DEAD = 1
    DEAD = 2

    def __init__(self, _status=None):
        if not _status:
            _status = VMStatus.DEAD

        assert VMStatus.ALIVE <= _status <= VMStatus.DEAD
        self._status = _status
    
    @staticmethod
    def alive():
        return VMStatus(VMStatus.ALIVE)

    @staticmethod
    def is_alive(vmstatus):
        return vmstatus.status == VMStatus.ALIVE

    @staticmethod
    def fbv_is_dead():
        return VMStatus(VMStatus.FBV_IS_DEAD)

    @staticmethod
    def is_fbv_is_dead(vmstatus):
        return vmstatus.status == VMStatus.FBV_IS_DEAD

    @staticmethod
    def dead():
        return VMStatus(VMStatus.DEAD)

    @staticmethod
    def is_dead(vmstatus):
        return vmstatus.status == VMStatus.DEAD

    def __repr__(self):
        return {
            VMStatus.ALIVE: "Alive",
            VMStatus.FBV_IS_DEAD: "fbv is dead",
            VMStatus.DEAD: "Dead"
            }.get(self._status)
    
    @property
    def status(self):
        return self._status


def _connect():
    """Connect to the vmsheder host and return the socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)     # 5 secs
    address = (g_host, g_port)

    try:
        sock.connect(address)
    except socket.error as serror:
        if serror.errno == errno.ECONNREFUSED:
            raise VmshederServerRefused('Connection Refused.')
        else:
            raise serror    # Not of our interest.

    return sock


def _send_and_read_finally_close(sock, packet):
    """Send a packet to a socket and read packets from the socket."""
    try:
        send_packet(sock, packet)
        packets = read_packets(sock)
    except socket.error as serror:
        if serror.errno == errno.ECONNABORTED or serror.errno == errno.ECONNRESET:
            raise VmshederServerInternalError('Connection corrupted.')
        else:
            raise serror

    finally:
        sock.close()

    return packets


def get_status(vm_id):
    """ Get status of vm_id, return ALIVE or DEAD or FBV_IS_DEAD.
    """
    reason, _, fbv_connected, _ = get_detailed_status(vm_id)
    if reason == "OK":
        if fbv_connected:
            status = VMStatus(VMStatus.ALIVE)
        else:
            status = VMStatus(VMStatus.FBV_IS_DEAD)
    else:
        status = VMStatus(VMStatus.DEAD)

    return status


def get_detailed_status(vm_id):
    """ Get the detailed status of the device specified by the vm_id.
    Return
    @reason: the reason of the last action taken on this vm associated with this vm_id.
    @state: the state the vm is in
    @fbv_connected: True if fbv is connected False if otherwise.
    @app_connected: True if app is connected False if otherwise.
    """
    packet = create_status(vm_id)
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_STATUS)

    # reason=OK indicates that the device is alive.

    data = get_data(packets)

    pattern = r"vm_id=(\d+)&reason=(\w+)&state=(\w+)&fbv_connected=(\w+)&app_connected=(\w+)"

    _id, reason, state, _fbv_connected, _app_connected = re.match(pattern, data).groups()
    assert _id == vm_id

    fbv_connected = _is_true(_fbv_connected)
    app_connected = _is_true(_app_connected)

    return reason, state, fbv_connected, app_connected


def _is_true(true_or_false):
    """ Return True if true_or_false is "true",
    False if true_or_false is "false"
    """
    TRUE_AND_FALSE = ("true", "false")
    assert true_or_false in TRUE_AND_FALSE

    return true_or_false is TRUE_AND_FALSE[0]


def get_status_all():
    packet = create_status_all()
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_STATUS_ALL)

    data = get_data(packets)

    return data


def devices():
    """Get the device list currently running on the g_host."""
    packet = create_devices()
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_DEVICES)
    data = get_data(packets)

    devices = data.split()

    return devices


def request_restart(vm_id):
    """
    Send a request to restart a vm with id of vm_id.
    return True on success
    """
    packet = create_restart(vm_id)
    sock = _connect()

    send_packet(sock, packet)
    # TODO: for now this doesn't work.
    # packet = read_packet(sock)

    sock.close()

    # check_header(packet, Header.TYPE_RESTART)

    # return packet.data


def install(vm_id, apk):
    """Install the apk on the specified vm."""
    packet = create_install(vm_id, apk)
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_INSTALL)
    data = get_data(packets)

    return data


def install_all(apk):
    """Installs apk on all available vms."""
    packet = create_install_all(apk)
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_INSTALL_ALL)
    data = get_data(packets)

    return data


def uninstall(vm_id, apk):
    """Uninstall apk on a specific vm."""
    packet = create_uninstall(vm_id, apk)
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_UNINSTALL)
    data = get_data(packets)

    return data


def uninstall_all(apk):
    """Uninstall apk on all vms."""
    packet = create_uninstall_all(apk)
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_UNINSTALL_ALL)
    data = get_data(packets)

    return data


def cmd(vm_id, cmd):
    """Run a command on a vm."""
    packet = create_cmd(vm_id, cmd)
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_SYS_CMD)
    data = get_data(packets)

    return data


def get_resolution(vm_id):
    """
    Get the resolution of this vm. "900x600", etc.
    """
    # TODO: Implement the *real* stuff.
    return "900x600"


def get_RAM(vm_id):
    """
    Get the total RAM of this vm in GB. "2GB", etc.
    """
    # TODO: Implement the *real* stuff
    return "2GB"


def list_installed_packages(vm_id,  third_party=True):
    """
    List the packages installed on this vm.
    @param third_party: third party packages only, which excludes pre-installed system packages etc.
    """
    # TODO: Implement third_party related stuff.
    packet = create_list_installed_packages(vm_id)

    sock = _connect()
    packets = _send_and_read_finally_close(sock, packet)
    data = get_data(packets)

    installed_packages = data.splitlines()

    return installed_packages


def list_apk():
    """
    list the apk files on the server that is to be installed.
    """
    packet= create_list_apk()

    sock = _connect()
    packets = _send_and_read_finally_close(sock, packet)

    data = get_data(packets)

    apk_list = data.splitlines()        # TODO: 2017.11.30.

    return apk_list