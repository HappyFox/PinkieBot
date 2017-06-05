import i2c

from enum import Enum

IMU_ADDR = 0x68
IMU_BUS = 2


class AccelConfig(Enum):
    """ From Register map, p14"""

    ADDR = 28

    FS_2G = 0b00 << 3
    FS_4G = 0b01 << 3
    FS_8G = 0b10 << 3
    FS_16G = 0b11 << 3


class GyroConfig(Enum):
    """ From Register map, p14"""

    ADDR = 29

    FS_250_DPS = 0b00 << 3
    FS_500_DPS = 0b01 << 3
    FS_1000_DPS = 0b10 << 3
    FS_2000_DPS = 0b11 << 3


class Accelerometer:

    def __init__(self, i2c_dev):
        self.i2c_dev = i2c_dev

        self.scale = AccelConfig.FS_2G


class Gyro:

    def __init__(self, i2c_dev):
        self.i2c_dev = i2c_dev

        self.scale = GyroConfig.GyroConfig.FS_1000_DPS



class MPU9250:

    def __init__(self, i2c_dev):
        self.i2c = i2c_dev

        self.accel = Accelerometer(i2c_dev)
        self.gyro = Gyro(i2c_dev)


    def initialize(self):
        pass

