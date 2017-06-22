import struct

from enum import IntFlag


MAG_ADDR = 0x0C


class MagAddr(IntFlag):

    ADDR = 0x0C
    AK8963 = 0x00   # should return 0x48
    INFO = 0x01
    ST1 = 0x02      # data ready status

    OUT_START = 0x03
    OUT_LEN = 0x06
    XOUT_L = 0x03   # data
    XOUT_H = 0x04
    YOUT_L = 0x05
    YOUT_H = 0x06
    ZOUT_L = 0x07
    ZOUT_H = 0x08
    ST2 = 0x09
    CNTL = 0x0A     # main mode control register
    ASTC = 0x0C     # Self test control
    I2CDIS = 0x0F   # I2C disable
    SENSE_START = 0x10
    SENSE_LEN = 0x03
    ASAX = 0x10     # x-axis sensitivity adjustment value
    ASAY = 0x11     # y-axis sensitivity adjustment value
    ASAZ = 0x12     # z-axis sensitivity adjustment value


class CNTL(IntFlag):

    POWER_DN = 0x00     # power down magnetometer
    SINGLE_MES = 0x01   # powers down after 1 measurement
    CONT_MES_1 = 0x02   # 8hz continuous self-sampling
    CONT_MES_2 = 0x06   # 100hz continuous self-sampling
    EXT_TRIG = 0x04     # external trigger mode
    SELF_TEST = 0x08    # self test mode
    FUSE_ROM = 0x0F     # ROM read only mode
    MSCALE_16 = 0x01<<4
    MSCALE_14 = 0x00


class ST1(IntFlag):

    DATA_READY = 0x01


class Magnetometer:

    _X = 0
    _Y = 1
    _Z = 2

    def __init__(self, i2c_dev, ms_sleep):
        self.i2c = i2c_dev
        self.ms_sleep = ms_sleep
        self.adjust = None
        self.last_result = [0,0,0]

    def initialize(self):
        self.i2c[MagAddr.CNTL] = CNTL.POWER_DN
        self.ms_sleep(1)
        self.i2c[MagAddr.CNTL] = CNTL.FUSE_ROM
        self.ms_sleep(1)

        buff = self.i2c.read(MagAddr.SENSE_START, MagAddr.SENSE_LEN)

        # From the AK8963 datasheet p 32
        adj = lambda x: (x - 128)*0.5/128.0 + 1

        self.adjust = [adj(x) for x in struct.unpack("BBB", buff)]

        self.i2c[MagAddr.CNTL] = CNTL.POWER_DN
        self.ms_sleep(1)

        self.i2c[MagAddr.CNTL] = CNTL.MSCALE_16 | CNTL.CONT_MES_2

        # TODO: Add calabration loading

    def data_ready(self):
        return self.i2c[MagAddr.ST1] & ST1.DATA_READY



