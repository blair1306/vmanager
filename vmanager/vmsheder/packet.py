# the protocol used to communicate between this program as the client side and a remote host as the server side running
# the vmsheder server.
from __future__ import absolute_import

from ..tnt import pythree, is_bytes_str

from struct import pack, unpack, calcsize
from socket import htons, ntohs

from ..io import read_sock_exactly, write_sock_exactly


# TODO: figure out if this is the right way.
network_byte_order = '!'


class PacketException(Exception):
    pass


class HeaderException(PacketException):
    pass


class WrongHeaderType(HeaderException):
    pass


class DataException(PacketException):
    pass


class WrongDataLength(DataException):
    pass


def create_packet(type, data):
    # TODO: will using this more generic one be better?
    n_bytes = len(data)
    header = Header(type, n_bytes)
    data = Data(data)

    return Packet(header, data)


"""These create_* methods are handy methods used to create packets of respective types."""


def create_status(vm_id):
    assert is_bytes_str(vm_id)

    n_bytes = len(vm_id)
    header = Header(Header.TYPE_STATUS, n_bytes)
    data = Data(vm_id)

    return Packet(header, data)


def create_status_all():
    n_bytes = 0
    header = Header(Header.TYPE_STATUS_ALL, n_bytes)
    data = Data(b"")

    return Packet(header, data)


def create_devices():
    header = Header(Header.TYPE_DEVICES, 0)
    data = Data(b"")

    return Packet(header, data)


def create_restart(vm_id):
    assert is_bytes_str(vm_id)

    n_bytes = len(vm_id)
    header = Header(Header.TYPE_RESTART, n_bytes)
    data = Data(vm_id)

    return Packet(header, data)


def create_install(vm_id, apk):
    assert is_bytes_str(vm_id) and is_bytes_str(apk)

    s = vm_id + b" " + apk
    
    n_bytes =len(s)
    header = Header(Header.TYPE_INSTALL, n_bytes)
    data = Data(s)

    return Packet(header, data)


def create_install_all(apk):
    assert is_bytes_str(apk)

    n_bytes = len(apk)
    header = Header(Header.TYPE_INSTALL_ALL, n_bytes)
    data = Data(apk)

    return Packet(header, data)


def create_uninstall(vm_id, package):
    assert is_bytes_str(vm_id) and is_bytes_str(package)

    s = vm_id + b" " + package
    n_bytes = len(s)
    header = Header(Header.TYPE_UNINSTALL, n_bytes)
    data = Data(s)

    return Packet(header, data)


def create_uninstall_all(package):
    assert is_bytes_str(package)

    n_bytes = len(package)
    header = Header(Header.TYPE_UNINSTALL_ALL, n_bytes)
    data = Data(package)

    return Packet(header, data)


def create_cmd(vm_id, cmd):
    assert is_bytes_str(vm_id) and is_bytes_str(cmd)

    data = vm_id + b" " + cmd

    n_bytes = len(data)
    header = Header(Header.TYPE_SYS_CMD, n_bytes)
    data = Data(data)

    

    return Packet(header, data)


def send_packet(sock, packet):
    """Send a header and it's data both at once."""
    return write_sock_exactly(sock, packet.pack(), len(packet))


def get_data(packets):
    """Reads and returns the data from a list of packets."""
    data = b""
    for packet in packets:
        data += packet.data.pack()
    return data


def read_packets(sock):
    """Reads packets until a packet indicating that all packets are sent by peer(by TYPE_DONE).
    The last packet that indicates a complete sent is discarded.
    Return a list of packets received.
    """
    packets = []
    while True:
        packet = read_packet(sock)
        if packet.header.type is Header.TYPE_DONE:
            break
        packets.append(packet)
    return packets


def read_packet(sock):
    """Reads a packet from socket. This will read the header first to determine the length of the data follows the
    header, then reads the data too and return them both."""
    header = _read_header(sock)
    n_bytes = header.n_bytes
    data = _read_data(sock, n_bytes)

    return Packet(header, data)


def _read_header(sock):
    """Reads a header from sockfd and unpack and return it."""
    b_header = read_sock_exactly(sock, Header.SIZE)       # this is packed, which needs unpacking.
    header = Header()
    header.unpack(b_header)

    return header


def _read_data(sock, n_bytes):
    """Reads data of length length and unpack and return it."""
    buffer = read_sock_exactly(sock, n_bytes)
    data = Data(buffer)

    return data


def check_header(packets, header_type):
    """Check if all headers in a list of packets is of type header_type, Raise if they dont' match."""
    for packet in packets:
        if packet.header.type != header_type:
            raise WrongHeaderType


class Packet(object):
    def __init__(self, header, data):
        self.header = header
        self.data = data

    def __repr__(self):
        return self.header.__repr__() + ", " + self.data.__repr__()

    def __len__(self):
        return len(self.header) + len(self.data)

    def pack(self):
        return self.header.pack() + self.data.pack()


class Header(object):
    """
    The header consists of a 2 bytes long type filed and a 2 byte long length field.
    """
    # H is a format specifier which is unsigned short (2 bytes long)
    FORMAT = "HH"
    # a header is always itself of a fixed size
    SIZE = calcsize(FORMAT)

    TYPE_NONE    = 0
    TYPE_DONE    = 1
    TYPE_SYS_CMD = 2
    TYPE_STATUS  = 3
    TYPE_STATUS_ALL = 4
    TYPE_RESTART = 5
    TYPE_RESTART_ALL = 6
    TYPE_DEVICES = 7
    TYPE_INSTALL = 8
    TYPE_INSTALL_ALL = 9
    TYPE_UNINSTALL = 10
    TYPE_UNINSTALL_ALL = 11

    TYPES = range(TYPE_UNINSTALL_ALL+1)

    def __init__(self, type=TYPE_NONE, n_bytes=0):
        assert type in Header.TYPES
        self.__init(type, n_bytes)

    def __init(self, type, n_bytes):
        self._format = Header.FORMAT
        self.type = type
        # explicit convert to bytes in python2, for in python3 this has to be done by myself.
        self.n_bytes = n_bytes

    def __repr__(self):
        type = {
            Header.TYPE_NONE: "none",
            Header.TYPE_STATUS: "status",
            Header.TYPE_RESTART: "restart",
            Header.TYPE_DEVICES: "devices"
        }.get(self.type, "unknown")

        return "header: type (%s), length (%s)" % (type, self.n_bytes)

    def __len__(self):
        return Header.SIZE      # the len of header is always 4

    def pack(self):
        """Pack header before it can be sent over socket."""
        return pack(network_byte_order + self._format, self.type, self.n_bytes)

    # Unpack the binary header data received from the socket and modify it's own type and length accordingly.
    def unpack(self, b_header):
        type, n_bytes = unpack(network_byte_order + self._format, b_header)
        self.__init(type, n_bytes)


class Data(object):
    """
    The actual data following a header of the type and length specified in the header.
    """
    FORMAT = "%ds"

    def __init__(self, data=''):
        self.__init(data)

    def __init(self, data):
        self._format = Data.FORMAT % len(data)
        self.data = bytes(data)

    def __len__(self):
        return calcsize(self._format)

    def __repr__(self):
        return "data: content (%s)," % self.data

    def pack(self):
        # Do nothing just return the data to be sent.
        return pack(self._format, self.data)
