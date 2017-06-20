import struct

from enum import IntFlag


MAG_ADDR = 0x0C


class MagAddr(IntFlag):

    ADDR = 0x0C
    AK8963 = 0x00   # should return 0x48
    INFO = 0x01
    ST1 = 0x02      # data ready status
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
    SENS_START = 0x10
    SENS_LEN = 0x03
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


class Magnetometer:

    def __init__(self, i2c_dev, sleep):
        self.i2c = i2c_dev
        self.sleep = sleep

    def initialize(self):
        self.i2c[MagAddr.CNTL] = CNTL.POWER_DN
        self.sleep(1)
        self.i2c[MagAddr.CNTL] = CNTL.FUSE_ROM
        self.sleep(1)

        buff = self.i2c.read(MagAddr.SENSE_START, MagAddr.SENSE_LEN)



