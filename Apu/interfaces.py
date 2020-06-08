import socket
import fcntl
import struct
import array
import sys

def all_interfaces():
    is_64bits = sys.maxsize > 2**32
    struct_size = 40 if is_64bits else 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    max_possible = 8 # initial value
    while True:
        _bytes = max_possible * struct_size
        names = array.array('B')
        for i in range(0, _bytes):
            names.append(0)
        outbytes = struct.unpack('iL', fcntl.ioctl(
            s.fileno(),
            0x8912,  # SIOCGIFCONF
            struct.pack('iL', _bytes, names.buffer_info()[0])
        ))[0]
        if outbytes == _bytes:
            max_possible *= 2
        else:
            break
    namestr = names.tostring()
    ifaces = []
    for i in range(0, outbytes, struct_size):
        iface_name = bytes.decode(namestr[i:i+16]).split('\0', 1)[0]
        iface_addr = socket.inet_ntoa(namestr[i+20:i+24])
        ifaces.append((iface_name, iface_addr))

    return ifaces