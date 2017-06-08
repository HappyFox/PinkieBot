import i2c

from enum import Enum

IMU_ADDR = 0x68
IMU_BUS = 2


class AccelDef(Enum):
    """ From Register map, p14"""

    CONFIG_ADDR = 28
    CONFIG_2_ADDR = 29

    FS_2G = 0b00 << 3
    FS_4G = 0b01 << 3
    FS_8G = 0b10 << 3
    FS_16G = 0b11 << 3

    FS_TO_MS = {}
    FS_TO_MS[FS_2G] = 9.80665 * 2.0 / 32768.0
    FS_TO_MS[FS_4G] = 9.80665 * 4.0 / 32768.0
    FS_TO_MS[FS_8G] = 9.80665 * 8.0 / 32768.0
    FS_TO_MS[FS_16G] = 9.80665 * 16.0 / 32768.0

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



class GyroDef(Enum):
    """ From Register map, p14"""

    CONFIG_ADDR = 27
    ADDR = 29

    FS_250_DPS = 0b00 << 3
    FS_500_DPS = 0b01 << 3
    FS_1000_DPS = 0b10 << 3
    FS_2000_DPS = 0b11 << 3

    FS_TO_DEG = {}
    FS_TO_DEG[FS_250_DPS] = 250.0 / 32768.0
    FS_TO_DEG[FS_500_DPS] = 500.0 / 32768.0
    FS_TO_DEG[FS_1000_DPS] = 1000.0 / 32768.0
    FS_TO_DEG[FS_2000_DPS] = 2000.0 / 32768.0

    DLPF_OFF = 1
    DLPF_184 = 1
    DLPF_92 = 2
    DLPF_41 = 3
    DLPF_20 = 4
    DLPF_10 = 5
    DLPF_5 = 6

    FCHOICE_B_DLPF_EN = 0x00
    FCHOICE_B_DLPF_DISABLE = 0x01



class Accelerometer:

    def __init__(self, i2c_dev):
        self.i2c = i2c_dev

        self.scale = AccelDef.FS_2G
        self._to_ms = 0.0

        self.dlpf = AccelDef.DLPF_92

    def initialize(self):
        self._to_ms = AccelDef.FS_TO_MS.value[self.scale.value]
        self.i2c[AccelDef.CONFIG_ADDR] = self.scale

        dlpf = AccelDef.FCHOICE_1KHZ.value | AccelDef.BIT_FIFO_SIZE_1024
        dlpf |= self.dlpf.value
        self.i2c[AccelDef.CONFIG_2_ADDR] = dlpf


class Gyro:

    def __init__(self, i2c_dev):
        self.i2c = i2c_dev

        self.scale = GyroDef.FS_1000_DPS
        self._to_deg= 0.0

        self.dlpf = GyroDef.DLPF_92

    def initialize(self):
        self._to_deg = GyroDef.FS_TO_DEG.value[self.scale]
        gyro_config = GyroDef.FCHOICE_B_DLPF_EN.value | self.scale.value
        self.i2c[ImuDef.CONFIG_ADDR] = gyro_config

        dlpf = ImuDef.FIFO_MODE_REPLACE_OLD
        dlpf |= self.dlpf.value
        self.i2c[ImuDef.CONFIG_ADDR] = dlpf


class SampleErrorRate(Exception):
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

    def __init__(self, i2c_dev):
        self.i2c = i2c_dev

        self.dmp_sample_rate = 100
        self.imu_orient = ImuDef.ORIENTATION_Z_UP

        self.accel = Accelerometer(i2c_dev)
        self.gyro = Gyro(i2c_dev)

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



