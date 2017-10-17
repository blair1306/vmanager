from __future__ import absolute_import

# Get info about the status of a virtual machine running in the remote server

import socket

from .packet import create_status, create_status_all, create_devices, create_restart, create_install, create_install_all
from .packet import create_uninstall, create_uninstall_all, create_cmd
from .packet import send_packet, read_packets, get_data
from .packet import check_header
from .packet import Header


host = "192.168.31.188"
port = 5895


def get_host_n_port():
    """Get the current host and port in use."""
    return host, port


def set_host_n_port(_host, _port):
    # TODO: assertions
    global host
    global port

    host = _host
    port = _port


class VMShederException(Exception):
    pass


class VMNotFound(VMShederException):
    pass


class VMIsAlive(VMShederException):
    """Raise when try to restart a vm that's alive."""
    pass


class VMStatus(object):
    ALIVE = 0
    FBV_IS_DEAD = 1
    DEAD  = 2


def _connect():
    """Connect to the vmsheder host and return the socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)     # 5 secs
    address = (host, port)

    sock.connect(address)

    return sock


def _send_and_read_finally_close(sock, packet):
    """Send a packet to a socket and read packets from the socket."""
    try:
        send_packet(sock, packet)
        packets = read_packets(sock)
    finally:
        sock.close()

    return packets


def get_status(vm_id):
    """use to emulate command of this FORMAT: vmsheler status 5554
    where "5554" is the vm_id.
    vm_id being the string representation of the interget.
    """
    packet = create_status(vm_id)
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_STATUS)

    # reason=OK indicates that the device is alive.

    data = get_data(packets)
    if b"reason=OK" in data:
        if b"fbv_alived=true" in data:
            status = VMStatus.ALIVE
        else:
            status = VMStatus.FBV_IS_DEAD
    else:
        status = VMStatus.DEAD

    return status


def get_status_all():
    packet = create_status_all()
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_STATUS_ALL)

    data = get_data(packets)

    return data


def devices():
    """Get the device list currently running on the host."""
    packet = create_devices()
    sock = _connect()

    packets = _send_and_read_finally_close(sock, packet)

    check_header(packets, Header.TYPE_DEVICES)
    data = get_data(packets)

    return data


def request_restart(vm_id):
    """
    Send a request to restart a vm with id of vm_id.
    return True on success
    """
    packet = create_restart(vm_id)
    sock = _connect()

    send_packet(sock, packet)
    # TODO: for now this doesn't work.
    #packet = read_packet(sock)

    sock.close()

    #check_header(packet, Header.TYPE_RESTART)

    #return packet.data


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