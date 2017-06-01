import pathlib
import contextlib

from pathlib import Path

from .common import BBBlueError


class PwmError(BBBlueError):
    pass


class ChipNotFoundError(PwmError):
    pass


class ChannelNotFoundError(PwmError):
    pass


NS = 1000000000

SEARCH_PATH = "/sys/devices/platform/ocp/"
SEARCH_GLOB = "*pwm*/*pwm/pwm/pwmchip?"


def get_pwm_chip(chip_num, freq=25000):
    search_path = Path(SEARCH_PATH)
    pwm_paths = list(search_path.glob(SEARCH_GLOB))
    for pwm_path in pwm_paths:
        if pwm_path.name[-1] == str(chip_num):
            return PwmChip(pwm_path, freq)

    raise ChipNotFoundError("Could not find pwm chip " + str(chip_num))


class PwmChip:

    def __init__(self, base_path, freq=25000):
        self.base_path = base_path

        self.export_path =  base_path / "export"
        self.unexport_path = base_path / "unexport"

        self.channels = []

        for idx in  range(2):
            self.channels.append(self._init_channel(idx))

        self.set_freq(freq)

    def _init_channel(self, channel_num):
        channel_name = "pwm{}".format(channel_num)
        pwm_path = self.base_path / channel_name

        if not pwm_path.is_dir():
            with open(self.export_path, "w") as export:
                print(str(channel_num))
                export.write(str(channel_num))
            if not pwm_path.is_dir():
                raise

        return PwmChannel(pwm_path)


    def set_freq(self, hz):

        with open(self.unexport_path, "w") as unexport_fd:
            unexport_fd.write("1")

        self.channels[0].enable = False
        self.channels[0].duty = 0

        with open(self.channels[0].period_path, "w") as period_fd:
            period_fd.write(str(int(NS/hz)))

        with open(self.export_path, "w") as export_fd:
            export_fd.write("1")

        self.channels[1].enable = False
        self.channels[1].duty = 0

        with open(self.channels[1].period_path, "w") as period_fd:
            period_fd.write(str(int(NS/hz)))

        for channel in self.channels:
            channel.enable = True


class PwmChannel:

    def __init__(self, base_path):
        self.base_path = base_path
        self.enable_path = base_path / "enable"
        self.period_path = base_path / "period"
        self.duty_path = base_path / "duty_cycle"
        self.polarity_path = base_path / "polarity"

        with open(self.period_path, "r") as period_fd:
            self.period_ns = int(period_fd.read(128))

    @property
    def enable(self):
        with open(self.enable_path, "r") as enable_fd:
            enable_str = enable_fd.read(128)

        if enable_str == '1\n':
            return True
        return False

    @enable.setter
    def enable(self, value):
        with open(self.enable_path, "w") as enable_fd:
            if value:
                enable_fd.write("1")
                with open(self.period_path, "r") as period_fd:
                    self.period_ns = int(period_fd.read(128))
            else:
                enable_fd.write("0")

    @property
    def duty(self):
        with open(self.duty_path, "r") as duty_fd:
            duty = duty_fd.read(128)

        return int(duty) / self.period_ns

    @duty.setter
    def duty(self, value):
        if not 0 <= value <= 1.0:
            raise PwmError("Invalid duty setting")

        with open(self.duty_path, "w") as duty_fd:
            duty_ns = int(self.period_ns * value)
            duty_fd.write(str(duty_ns))


