import struct
import time

import i2c

from enum import IntFlag

from ..common import BBBlueError, NotInitializedError

from .accelerometer import Accelerometer
from .gyro import Gyro

IMU_ADDR = 0x68
IMU_BUS = 2


class SampleErrorRate(BBBlueError):
    pass


def msleep(msec):
    time.sleep(msec * 0.001)


def build_imu(mag=True, sleep = msleep):
    bus = i2c.I2cBus(IMU_BUS)

    mpu = mpu9250(bus[IMU_ADDR], sleep)

    if mag:
        mag = Magnetometer(bus[MAG_ADDR], sleep)
        mpu.mag = mag

    return mpu



class ImuDef(IntFlag):

    PWR_MGMT_1_ADDR = 107
    H_RESET = 0x01 << 7

    USER_CTRL_ADDR = 0xA6
    I2C_MST_EN = 1<<5

    ORIENTATION_Z_UP = 136
    ORIENTATION_Z_DOWN = 396
    ORIENTATION_X_UP = 14
    ORIENTATION_X_DOWN = 266
    ORIENTATION_Y_UP = 112
    ORIENTATION_Y_DOWN = 336
    ORIENTATION_X_FORWARD = 133
    ORIENTATION_X_BACK = 161

    DMP_MAX_RATE = 200
    DMP_MIN_RATE = 4

    WHO_AM_I_ADDR = 0x75
    WHO_AM_I = 0x71

    SMPLRT_DIV = 26

    CONFIG_ADDR = 0x1A
    FIFO_MODE_REPLACE_OLD = 0x00


class MPU9250:

    def __init__(self, i2c_bus, sleep=msleep):
        self.i2c = i2c_bus[IMU_ADDR]
        self.sleep = sleep


        self.dmp_sample_rate = 100
        self.imu_orient = ImuDef.ORIENTATION_Z_UP

        self.accel = Accelerometer(self.i2c, sleep)
        self.gyro = Gyro(self.i2c, sleep)
        self.mag = None

    def reset(self):
        self.i2c[ImuDef.PWR_MGMT_1_ADDR] = ImuDef.H_RESET
        self.i2c[ImuDef.PWR_MGMT_1_ADDR] = 0

        who_am_i = self.i2c[ImuDef.WHO_AM_I_ADDR]

        if who_am_i != ImuDef.WHO_AM_I.value:
            raise Exception()  # TODO: add proper exception

    def initialize(self):
        self.reset()

        if not (ImuDef.DMP_MIN_RATE <= self.dmp_sample_rate <=
                ImuDef.DMP_MAX_RATE):
            err_str = "Invalid sample rate of {}".format(self.dmp_sample_rate)
            raise SampleRateError(err_str)

        if (ImuDef.DMP_MAX_RATE % self.dmp_sample_rate) != 0:
            err_str = "Invalid sample rate of {}".format(self.dmp_sample_rate)
            raise SampleRateError(err_str)

        self.i2c[ImuDef.SMPLRT_DIV] = 0

    @property
    def bypass(self):
        user_reg = self.i2c[ImuDef.USER_CTRL_ADDR]

        return bool(user_reg & ImuDef.I2C_MST_EN)

    @bypass.setter
    def bypass(self, value):
        user_reg = self.i2c[ImuDef.USER_CTRL_ADDR]

        if value:
            user_reg = user_reg | ImuDef.I2C_MST_EN
        else:
            mask = 255 - ImuDef.I2C_MST_EN
            user_reg = user_reg & mask

        self.i2c[ImuDef.USER_CTRL_ADDR] = user_reg

