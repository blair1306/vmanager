# Get info about the status of a virtual machine running in the remote server

import socket

from vmsheder_packet import create_status, create_devices, create_restart
from vmsheder_packet import send_packet, read_packet
from vmsheder_packet import check_header
from vmsheder_packet import Header


HOST = "localhost"
PORT = 5895


class VMShederException(Exception):
    pass


class VMNotFound(VMShederException):
    pass


class VMIsAlive(VMShederException):
    """Raise when try to restart a vm that's alive."""
    pass


class VMStatus(object):
    ALIVE = 0
    DEAD  = 1


def _connect():
    """Connect to the vmsheder host and return the socket"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)     # 5 secs
    address = (HOST, PORT)

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

    packet = read_packet(sock)
    sock.close()

    check_header(packet, Header.TYPE_STATUS)

    return packet.data


def devices():
    """Get the device list currently running on the host."""
    packet = create_devices()
    sock = _connect()

    send_packet(sock, packet)
    packet = read_packet(sock)

    sock.close()

    check_header(packet, Header.TYPE_DEVICES)

    return packet.data


def request_restart(vm_id):
    """
    Send a request to restart a vm with id of vm_id.
    return True on success
    """
    packet = create_restart(vm_id)
    sock = _connect()

    send_packet(sock, packet)
    packet = read_packet(sock)

    sock.close()

    check_header(packet, Header.TYPE_RESTART)

    return packet.data
