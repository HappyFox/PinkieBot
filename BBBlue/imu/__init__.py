import time

import i2c

#import BBBlue.imu.mpu9250 as mpu9250
#import BBBlue.imu.magnetometer as mag

from BBBlue.imu import mpu9250
from BBBlue.imu import magnetometer

from BBBlue.imu.mpu9250 import Mpu9250
from BBBlue.imu.magnetometer import Magnetometer


IMU_BUS = 2


def msleep(msec):
    time.sleep(msec * 0.001)


def build_imu(sleep = msleep):
    bus = i2c.I2cBus(IMU_BUS)

    mpu = Mpu9250(bus[mpu9250.ADDR], sleep)

    _mag = Magnetometer(bus[mag.ADDR], sleep)

    imu = Imu(mpu, _mag)

    return imu


class Imu:

    def __init__(self, mpu, mag):
        self.mpu = mpu
        self.mag = mag

    def initialize(self):
        pass

