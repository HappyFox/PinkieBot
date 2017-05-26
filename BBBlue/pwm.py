import pathlib

from pathlib import Path


class ChipNotFoundError(Exception):
    pass

def get_pwm_chip(chip_num):
    search_path = Path("/sys/devices/platform/ocp/")
    pwm_paths = list(search_path.glob("*pwm*/*pwm/pwm/pwmchip?"))
    for pwm_path in pwm_paths:
        if pwm_path.name[-1] == str(chip_num):
            return PwmChip(pwm_path)

    raise ChipNotFoundError("Could not find pwm chip " + str(chip_num))


class PwmChip:

    def __init__(self, base_path):
        self.base_path = base_path
        self.enable_path = base_path / "enable"
