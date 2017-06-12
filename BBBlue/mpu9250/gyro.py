import struct


from ..common import NotInitializedError


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

    OUT_START = 0x43


class Gyro:

    def __init__(self, i2c_dev):
        self.i2c = i2c_dev

        self.scale = GyroDef.FS_1000_DPS
        self._to_deg= 0.0

        self.dlpf = GyroDef.DLPF_92

        self.initialized = False

    def initialize(self):
        self._to_deg = GyroDef.FS_TO_DEG.value[self.scale.value]
        gyro_config = GyroDef.FCHOICE_B_DLPF_EN.value | self.scale.value
        self.i2c[GyroDef.CONFIG_ADDR] = gyro_config

        dlpf = ImuDef.FIFO_MODE_REPLACE_OLD.value
        dlpf |= self.dlpf.value
        self.i2c[ImuDef.CONFIG_ADDR] = dlpf

        self.initialized = True

    def read_deg(self):
        if not self.initialized:
            raise NotInitializedError()

        out = self.i2c.read(GyroDef.OUT_START, 6)
        dat = struct.unpack(">hhh", out)
        dat = [x * self._to_deg for x in dat]
        return dat

