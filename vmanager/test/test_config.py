import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


from vmanager.config import config_reader


def test_read():
    PORT = 'vmsheder.port'
    HOST = 'vmsheder.host'
    vmsheder_host = config_reader.get(HOST)
    vmsheder_port = config_reader.get(PORT)

    print('%s: %s, %s: %s' % (HOST, vmsheder_host, PORT, vmsheder_port))


if __name__ == '__main__':
    test_read()