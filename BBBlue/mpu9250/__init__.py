import struct

import i2c

from enum import Enum

from ..common import BBBlueError, NotInitializedError

from accelerometer import Accelerometer
from gyro import Gyro

IMU_ADDR = 0x68
IMU_BUS = 2


class SampleErrorRate(BBBlueError):
    pass


class ImuDef(Enum):

    PWR_MGMT_1 = 107
    H_RESET = 0x01 << 7

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

    def __init__(self, i2c_bus):
        self.i2c = i2c_bus[IMU_ADDR]


        self.dmp_sample_rate = 100
        self.imu_orient = ImuDef.ORIENTATION_Z_UP

        self.accel = Accelerometer(i2c_dev)
        self.gyro = Gyro(i2c_dev)
        #sefl.magno = Magnetometer

    def reset(self):
        self.i2c[ImuDef.PWR_MGMT_1] = ImuDef.H_RESET
        self.i2c[ImuDef.PWR_MGMT_1] = 0

        who_am_i = self.i2c[ImuDef.WHO_AM_I_ADDR]

        if who_am_i != ImuDef.WHO_AM_I.value:
            raise Exception()  # TODO: add proper exception



    def initialize(self):
        self.reset()

        if not (ImuDef.DMP_MIN_RATE <= self.dmp_sample_rate <=
                ImuDef.DMP_MAX_RATE):
            err_str = "Invalid sample rate of {}".format(self.dmp_sample_rate)
            raise SampleRateError(err_str)

        if (ImuDef.DMP_MAX_RATE % self.dmp_samepl_rate) != 0:
            err_str = "Invalid sample rate of {}".format(self.dmp_sample_rate)
            raise SampleRateError(err_str)

        self.i2c[ImuDef.SMPLRT_DIV] = 0



