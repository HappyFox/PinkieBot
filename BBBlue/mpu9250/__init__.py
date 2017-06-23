import struct
import time

import i2c

from enum import IntFlag

from ..common import BBBlueError, NotInitializedError

from .accelerometer import Accelerometer
from .gyro import Gyro
from .magnetometer import Magnetometer, MAG_ADDR

IMU_ADDR = 0x68
IMU_BUS = 2


class SampleErrorRate(BBBlueError):
    pass


def msleep(msec):
    time.sleep(msec * 0.001)


def build_imu(mag=True, sleep = msleep):
    bus = i2c.I2cBus(IMU_BUS)

    mpu = MPU9250(bus[IMU_ADDR], sleep)

    if mag:
        mag = Magnetometer(bus[MAG_ADDR], sleep)
        mpu.mag = mag

    return mpu


class ImuDef(IntFlag):

    PWR_MGMT_1_ADDR = 107
    H_RESET = 0x01 << 7

    USER_CTRL_ADDR = 0xA6

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


class USER_CTRL(IntFlag):
    ADDR = 0xA6
    I2C_MST_EN = 1<<5


class INT_PIN(IntFlag):
    ADDR = 0x37

    ACTL_ACTIVE_LOW = 0x01<<7
    OPEN_DRAIN = 0x01<<6
    LATCH_INT_EN = 0x01<<5
    INT_ANYRD_CLEAR = 0x01<<4
    ACTL_FSYNC_ACTIVE_LOW = 0x01<<3
    FSYNC_INT_MODE_EN = 0x01<<2
    BYPASS_EN = 0x01<<1


class MPU9250:

    def __init__(self, i2c_dev, sleep=msleep):
        self.i2c = i2c_dev
        self.sleep = sleep

        self.dmp_sample_rate = 100
        self.imu_orient = ImuDef.ORIENTATION_Z_UP

        self.accel = Accelerometer(self.i2c)
        self.gyro = Gyro(self.i2c)
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

    def bypass(self, bypass):
        user_reg = self.i2c[USER_CTRL.ADDR]

        if bypass:
            user_reg = user_reg | USER_CTRL.I2C_MST_EN
        else:
            mask = 255 - USER_CTRL.I2C_MST_EN
            user_reg = user_reg & mask

        self.i2c[USER_CTRL.ADDR] = user_reg

        self.sleep(3)

        int_pin = INT_PIN.LATCH_INT_EN
        int_pin |= INT_PIN.INT_ANYRD_CLEAR
        int_pin |= INT_PIN.ACTL_ACTIVE_LOW

        if bypass:
            int_pin |= INT_PIN.BYPASS_EN

        self.i2c[INT_PIN.ADDR] = int_pin

