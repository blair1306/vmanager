#
# Socket io module
#

import socket


def write_sock_exactly(sock, buffer, length):
    assert type(sock) is socket.socket

    return sock.sendall(buffer, length)


def read_sock_exactly(sock, length):
    assert type(sock) is socket.socket

    buffer = ''
    while len(buffer) < length:
        bytes = sock.recv(length - len(buffer))
        buffer += bytes

    return buffer
