from collections import namedtuple

from enum import Enum

from . import pwm
from . import gpio


MOTOR_STBY = 20

MotorPins = namedtuple("MotorPins", ['a', 'b', 'pwm_chip', 'pwm_channel'])

MOTOR_PINS = [MotorPins(64, 31, 2, 0), MotorPins(48, 10, 2, 1)]

class Speed(Enum):
    BRAKE = 1
    FREEWHEEL = 2


def enable_motors():
    enable_pin = gpio.Pin(MOTOR_STBY)
    enable_pin.high = True


def disable_motors():
    enable_pin = gpio.Pin(MOTOR_STBY)
    enable_pin.low = True


def get_motor(idx):
    idx -= 1
    pins = MOTOR_PINS[idx]

    dir_a = gpio.Pin(pins.a)
    dir_b = gpio.Pin(pins.b)

    pwm_chip = pwm.get_pwm_chip(pins.pwm_chip)
    pwm_channel = pwm_chip.channels[pins.pwm_channel]

    return Motor(dir_a, dir_b, pwm_channel)


class Motor:

    def __init__(self, dir_a, dir_b, pwm_channel):
        self.dir_a = dir_a
        self.dir_b = dir_b
        self.pwm = pwm_channel

        self.dir_a.low = True
        self.dir_b.low = True
        self.pwm.duty = 0

    @property
    def speed(self):
        if self.dir_a.high and self.dir_b.low:
            return self.pwm.duty
        elif self.dir_a.low and self.dir_b.high:
            return -self.pwm.duty
        elif self.dir_a.low and self.dir_b.low:
            return Speed.FREEWHEEL
        else:
            return Speed.BRAKE

    @speed.setter
    def speed(self, value):
        if isinstance(value, Speed):
            if value == Speed.FREEWHEEL:
                self.dir_a.low = True
                self.dir_b.low = True
            else:
                self.dir_a.high = True
                self.dir_b.high = True
            self.pwm.duty = 0
            return

        if value >= 0:
            self.dir_a.high = True
            self.dir_b.low = True
        else:
            self.dir_a.low = True
            self.dir_b.high = True

        self.pwm.duty = abs(value)





