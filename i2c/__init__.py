import fcntl
import posix
import struct

from enum import Enum
from fcntl import ioctl

# from i2c-dev.h
I2C_SLAVE = 0x0703

class NotSupportedError(Exception):
    pass

class I2cBus(dict):

    def __init__(self, bus):
        if isinstance(bus, Enum):
            bus = bus.value
        self.bus = bus
        self.file_path = "/dev/i2c-%d" % self.bus

        #TODO: verify that we can open the file here, so we fail early.

        dict.__init__(self)

    def __getitem__(self, key):
        if isinstance(key, Enum):
            key = key.value

        if key in self:
            return dict.__getitem__(self, key)
        else:
            device = I2cDevice(self.file_path, key)
            dict.__setitem__(self, key, device)
            return device

    def __setitem___(self, key):
        raise NotSupportedError()


class I2cDevice(object):

    def __init__(self, file_path, addr):
        self.fd = posix.open(file_path, posix.O_RDWR)

        if ioctl(self.fd, I2C_SLAVE, addr) != 0:
            raise Exception() #TODO: add more exceptions.

    def __getitem__(self, key):
        ret_val = self.read(key, 1)
        return struct.unpack("B", ret_val)[0]

    def __setitem__(self, key, value):
        self.write(key, value)

    def read(self, addr, _len):
        if isinstance(addr, Enum):
            addr = addr.value

        addr = struct.pack('B', addr)
        if posix.write(self.fd, addr) != 1:
            raise Exception()

        return posix.read(self.fd, _len)

    def write(self, addr, value):
        if isinstance(addr, Enum):
            addr = addr.value
        if isinstance(value, Enum):
            value = value.value

        msg = struct.pack('B', addr)

        if isinstance(value, bytes):
            msg += value
        else:
            msg += struct.pack("B" * len(value), * value)

        if posix.write(self.fd, msg) != len(msg):
            raise Exception()

    def __del__(self):
        try:
            posix.close(self.fd)
        except AttributeError:
            pass #Do nothing in this case.

