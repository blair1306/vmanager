# the protocol used to communicate between this program as the client side and a remote host as the server side running
# the vmsheder server.


from struct import pack, unpack, calcsize
from socket import htons, ntohs

from sio import read_sock_exactly, write_sock_exactly


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
    assert type(vm_id) is str

    n_bytes = len(vm_id)
    header = Header(Header.TYPE_STATUS, n_bytes)
    data = Data(vm_id)

    return Packet(header, data)


def create_devices():
    header = Header(Header.TYPE_DEVICES, 0)
    data = Data("")

    return Packet(header, data)


def create_restart(vm_id):
    assert type(vm_id) is str

    n_bytes = len(vm_id)
    header = Header(Header.TYPE_RESTART, n_bytes)
    data = Data(vm_id)

    return Packet(header, data)


def send_packet(sock, packet):
    """Send a header and it's data both at once."""
    return write_sock_exactly(sock, packet.pack(), len(packet))


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


def check_header(packet, header_type):
    """Check if the header in packet is of type header_type, Raise if they dont' match."""
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
    TYPE_STATUS  = 3
    TYPE_RESTART = 4
    TYPE_DEVICES = 5
    TYPE_COUNT   = 6

    def __init__(self, type=TYPE_NONE, n_bytes=0):
        """type_or_bytes is whether the type or the whole thing in bytes depending on whether restore is True."""
        self.__init(type, n_bytes)

    def __init(self, type, n_bytes):
        self._format = Header.FORMAT
        self.type = type
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
        self.data = data

    def __len__(self):
        return calcsize(self._format)

    def __repr__(self):
        return "data: content (%s)," % self.data

    def pack(self):
        # Do nothing just return the data to be sent.
        return self.data
