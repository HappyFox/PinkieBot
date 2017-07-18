import time

import i2c

#import BBBlue.imu.mpu9250 as mpu9250
#import BBBlue.imu.magnetometer as mag

from BBBlue.imu import mpu9250
from BBBlue.imu import ak8963c

from BBBlue.imu.mpu9250 import Mpu9250
from BBBlue.imu.ak8963c import Ak8963c


IMU_BUS = 2


def msleep(msec):
    time.sleep(msec * 0.001)


def build_imu(sleep = msleep):
    bus = i2c.I2cBus(IMU_BUS)

    mpu = Mpu9250(bus[mpu9250.ADDR], sleep)

    mag = Ak8963c(bus[ak8963c.ADDR], sleep)

    imu = Imu(mpu, mag)

    return imu


class Imu:

    def __init__(self, mpu, mag):
        self.mpu = mpu
        self.mag = mag

    def initialize(self):
        self.mpu.reset()

        self.mpu.bypass(True)
        self.mag.reset()
        self.mpu.bypass(False)

