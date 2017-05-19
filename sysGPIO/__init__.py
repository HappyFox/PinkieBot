import os

from enum import Enum


class GpioError(Exception):
    pass


class ExportError(GpioError):
    pass


class InvalidPinError(GpioError):
    pass


class DirectionError(GpioError):
    pass


class Direction(Enum):
    IN = 1
    OUT = 2


class Pin(object):

    _OUT_STR = "out\n"
    _IN_STR = "in\n"

    base_path = "/sys/class/gpio/"
    export_path = base_path + "export"
    unexport_path = base_path + "unexport"

    def __init__(self, pin):
        self.pin = pin
        self.dir_path = self.base_path + "gpio{}".format(pin)
        self.value_path = self.dir_path + "/value"
        self.direction_path = self.dir_path + "/direction"

        if not os.path.isdir(self.dir_path):
            print(self.export_path)
            with open(self.export_path, "w") as export:
                export.write(str(pin))
            if not os.path.isdir(self.dir_path):
                raise ExportError("Can not export pin " + str(pin))

    def _get_value(self):
        with open(self.value_path, 'r') as value:
            state = value.read()
        return bool(int(state))

    def _set_value(self, state):
        write_val = '0'
        if state:
            write_val = '1'

        with open(self.value_path, 'w') as value:
            value.write(write_val)

    @property
    def direction(self):
        with open(self.direction_path, 'r') as direction:
            dir_val = direction.read()

        if dir_val == self._IN_STR:
            return Direction.IN
        elif dir_val == self._OUT_STR:
            return Direction.OUT
        else:
            raise DirectionError("Got value : " + dir_val)

    @direction.setter
    def direction(self, value):
        if not isinstance(value, Direction):
            raise DirectionError("Can't set non-direction value")

        dir_val = self._IN_STR
        if value == Direction.OUT:
            dir_val = self._OUT_STR

        with open(self.direction_path, 'w') as direction:
            direction.write(dir_val)

    @property
    def high(self):
        return self._get_value()

    @high.setter
    def high(self, value):
        self._set_value(value)

    @property
    def low(self):
        return not self._get_value()

    @low.setter
    def low(self, value):
        self._set_value(not value)


