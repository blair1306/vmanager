#
# Socket io module
#
from __future__ import absolute_import

import socket


def write_sock_exactly(sock, buffer, length):
    assert type(sock) is socket.socket

    s = buffer
    while length > 0:
        sent = sock.send(s)
        length -= sent
        s = s[length: ]


def read_sock_exactly(sock, length):
    assert type(sock) is socket.socket

    buffer = b''
    while len(buffer) < length:
        bytes = sock.recv(length - len(buffer))
        buffer += bytes

    return buffer
