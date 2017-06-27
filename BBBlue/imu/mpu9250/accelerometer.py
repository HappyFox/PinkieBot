import struct

from enum import IntFlag

from BBBlue.common import NotInitializedError


class AccelDef(IntFlag):
    """ From Register map, p14"""

    CONFIG_ADDR = 28
    CONFIG_2_ADDR = 29

    FS_2G = 0b00 << 3
    FS_4G = 0b01 << 3
    FS_8G = 0b10 << 3
    FS_16G = 0b11 << 3


    DLPF_OFF = 7
    DLPF_184 = 1
    DLPF_92 = 2
    DLPF_41 = 3
    DLPF_20 = 4
    DLPF_10 = 5
    DLPF_5 = 6

    FCHOICE_1KHZ = 0x00 << 3
    FCHOICE_4KHZ = 0x01 << 3

    BIT_FIFO_SIZE_1024 = 0x40
    BIT_FIFO_SIZE_2048 = 0x80
    BIT_FIFO_SIZE_4096 = 0xC0

    OUT_START = 0x3B


class Accelerometer:

    FS_TO_MS = {}
    FS_TO_MS[AccelDef.FS_2G] = 9.80665 * 2.0 / 32768.0
    FS_TO_MS[AccelDef.FS_4G] = 9.80665 * 4.0 / 32768.0
    FS_TO_MS[AccelDef.FS_8G] = 9.80665 * 8.0 / 32768.0
    FS_TO_MS[AccelDef.FS_16G] = 9.80665 * 16.0 / 32768.0

    def __init__(self, i2c_dev):
        self.i2c = i2c_dev

        self.scale = AccelDef.FS_2G
        self._to_ms = 0.0

        self.dlpf = AccelDef.DLPF_92

        self.initialized = False

    def initialize(self):
        import pdb;pdb.set_trace()
        self._to_ms = self.FS_TO_MS[self.scale]
        self.i2c[AccelDef.CONFIG_ADDR] = self.scale

        dlpf = AccelDef.FCHOICE_1KHZ | AccelDef.BIT_FIFO_SIZE_1024
        dlpf |= self.dlpf
        self.i2c[AccelDef.CONFIG_2_ADDR] = dlpf

        self.initialized = True

    def read_ms(self):
        if not self.initialized:
            raise NotInitializedError()

        out = self.i2c.read(AccelDef.OUT_START, 6)
        dat = struct.unpack(">hhh", out)
        dat = [x * self._to_ms for x in dat]
        return dat

