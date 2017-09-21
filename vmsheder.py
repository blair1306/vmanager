# Get info about the status of a virtual machine running in the remote server

import socket

from vmsheder_packet import create_status, create_devices, create_restart
from vmsheder_packet import send_packet, read_packets, get_data
from vmsheder_packet import check_header
from vmsheder_packet import Header


host = "localhost"
port = 5895


def get_host_n_port():
    """Get the current host and port in use."""
    return host, port


def set_host_n_port(_host, _port):
    assert _host and type(_host) is str
    assert type(_host) is int and _port > 0

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


def get_status(vm_id):
    """use to emulate command of this FORMAT: vmsheler status 5554
    where "5554" is the vm_id.
    vm_id being the string representation of the interget.
    """
    packet = create_status(vm_id)
    sock = _connect()
    send_packet(sock, packet)

    packets = read_packets(sock)
    sock.close()

    check_header(packets, Header.TYPE_STATUS)

    # reason=OK indicates that the device is alive.

    data = get_data(packets)
    if "reason=OK" in data:
        if "fbv_alived=true" in data:
            status = VMStatus.ALIVE
        else:
            status = VMStatus.FBV_IS_DEAD
    else:
        status = VMStatus.DEAD

    return status


def devices():
    """Get the device list currently running on the host."""
    packet = create_devices()
    sock = _connect()

    send_packet(sock, packet)
    packets = read_packets(sock)

    sock.close()

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
