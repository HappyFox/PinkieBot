import struct
import time



from enum import IntFlag

import i2c

from BBBlue.common import BBBlueError, NotInitializedError

from .accelerometer import Accelerometer
from .gyro import Gyro

ADDR = 0x68


class SampleErrorRate(BBBlueError):
    pass


class InvalidIdError(BBBlueError):
    pass


class DmpOverFlowError(BBBlueError):
    pass


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

class FifoDef(IntFlag):

    PRGM_START_H = 0x70
    BANK_SIZE    = 256
    BANK_SEL     = 0x6D
    MEM_R_W      = 0x6F


class CONFIG(IntFlag):
    ADDR = 0x1A

    FIFO_DROP = 0x40


class PWR_MGMT_1(IntFlag):
    ADDR = 0x6B

    H_RESET = 0x80
    SLEEP = 0x40
    CYCLE = 0x20
    GYRO_STANDBY = 0x10
    PD_PTAT = 0x08
    CLKSEL_INTERNAL = 0
    CLKSEL_AUTO = 1
    CLKSEL_STOP = 7


class PWR_MGMT_2(IntFlag):
    ADDR = 0x6C


class USER_CTRL(IntFlag):
    ADDR = 0xA6

    I2C_MST_EN = 0x20

class INT_ENABLE(IntFlag):
    ADDR = 0x38

    RAW_RDY_EN = 0x01


class INT_PIN(IntFlag):
    ADDR = 0x37

    ACTL_ACTIVE_LOW = 0x01<<7
    OPEN_DRAIN = 0x01<<6
    LATCH_INT_EN = 0x01<<5
    INT_ANYRD_CLEAR = 0x01<<4
    ACTL_FSYNC_ACTIVE_LOW = 0x01<<3
    FSYNC_INT_MODE_EN = 0x01<<2
    BYPASS_EN = 0x01<<1



class Mpu9250:

    def __init__(self, i2c_dev, sleep):
        self.i2c = i2c_dev
        self.sleep = sleep

        self.dmp_sample_rate = 100
        self.imu_orient = ImuDef.ORIENTATION_Z_UP

        self.accel = Accelerometer(self.i2c)
        self.gyro = Gyro(self.i2c)

    def reset(self):
        self.i2c[ImuDef.PWR_MGMT_1_ADDR] = ImuDef.H_RESET

        self.sleep(100)

        who_am_i = self.i2c[ImuDef.WHO_AM_I_ADDR]

        if who_am_i != ImuDef.WHO_AM_I.value:
            raise InvalidIdError()

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

    def calibrate(self):
        self.reset()

        self.i2c[PWR_MGMT_1] = PWR_MGMT_1.CLKSEL_AUTO
        self.i2c[PWR_MGMT_2] = 0  # Clear everythin

        self.sleep(200)

        self.i2c[INT_ENABLE] = 0  # Clear all interupts
        self.i2c[I





    def bypass(self, bypass):
        user_reg = self.i2c[USER_CTRL]

        if bypass:
            user_reg = user_reg | USER_CTRL.I2C_MST_EN
        else:
            mask = 255 - USER_CTRL.I2C_MST_EN
            user_reg = user_reg & mask

        self.i2c[USER_CTRL] = user_reg

        self.sleep(3)

        int_pin = INT_PIN.LATCH_INT_EN
        int_pin |= INT_PIN.INT_ANYRD_CLEAR
        int_pin |= INT_PIN.ACTL_ACTIVE_LOW

        if bypass:
            int_pin |= INT_PIN.BYPASS_EN

        self.i2c[INT_PIN] = int_pin

    def mpu_write(self, addr, buff):
        bank = addr >> 8
        mem_start = addr && 0xFF

        if (len(buff) + mem_start) > FifoDef.BANK_SIZE:
            raise DmpOverFlowError()




