#!/bin/bash
#
# Place in /usr/local/bin/set-gpio-permissions.sh
#
# This file will change the user, group and permissions in both the
# /sys/devices/virtual/gpio and /sys/class/gpio path directories. In particular,
# it will add a `gpio` group to these files. By adding your user to this
# group, you will have access to those pin files.
#
# DO NOT change the order of the commands below, they are optimized so that
# commonly created files and directories are changed first.
#

#chown -R :gpio /sys/devices/virtual/gpio
chown -R -H :gpio /sys/class/gpio/*
chown -R -H :gpio /sys/class/gpio/*


find /sys/class/gpio/gpio*/ -type d -exec chmod 2775 {} \;
find /sys/class/gpio/gpio*/ -name "direction" -exec chmod 0660 {} \;
find /sys/class/gpio/gpio*/ -name "edge" -exec chmod 0660 {} \;
find /sys/class/gpio/gpio*/ -name "value" -exec chmod 0660 {} \;
find /sys/class/gpio/gpio*/ -name "active_low" -exec chmod 0660 {} \;
find /sys/class/gpio/gpio*/ -name "uevent" -exec chmod 0660 {} \;

chmod 0220 /sys/class/gpio/export
chmod 0220 /sys/class/gpio/unexport


chown -R -H  :gpio /sys/devices/platform/ocp/*pwm*/*pwm/pwm/*

find /sys/devices/platform/ocp/*pwm*/*pwm/ -name "export" -exec chmod 0220 {} \;
find /sys/devices/platform/ocp/*pwm*/*pwm/ -name "unexport" -exec chmod 0220 {} \;

find /sys/devices/platform/ocp/*pwm*/*pwm/pwm/ -type d -exec chmod 2775 {} \;
find /sys/devices/platform/ocp/*pwm*/*pwm/pwm/ -name "duty_cycle" -exec chmod 0660 {} \;
find /sys/devices/platform/ocp/*pwm*/*pwm/pwm/ -name "enable" -exec chmod 0660 {} \;
find /sys/devices/platform/ocp/*pwm*/*pwm/pwm/ -name "period" -exec chmod 0660 {} \;
find /sys/devices/platform/ocp/*pwm*/*pwm/pwm/ -name "polarity" -exec chmod 0660 {} \;


#find /sys/devices/virtual/gpio -name "autosuspend_delay_ms" -exec chmod 0660 {} \;
#find /sys/devices/virtual/gpio -name "control" -exec chmod 0660 {} \;

# Additional code for getting AIN pins set up
#ain_activator=/sys/devices/bone_capemgr.*
#chown -R :gpio $ain_activator/
#chmod -R 2775 $ain_activator/

# Uncomment to have the AIN pins activated by default on boot
# echo cape-bone-iio > $ain_activator/slots
