#!/usr/bin/env python


__author__      = "gitgudd"

from ctypes import cdll
import os

os.system("gcc -c -fPIC elevator_hardware.c -o elevator_hardware.o")
os.system("gcc -shared -Wl,-soname,IOdriver.so -o IOdriver.so  elevator_hardware.o")

elev = cdll.LoadLibrary('./IOdriver.so')


elev.elevator_hardware_init()


elev.elevator_hardware_set_motor_direction(DIRN_UP)


while(True):
	elev.elevator_hardware_set_motor_direction(DIRN_DOWN)
	while(elev.elevator_hardware_get_floor_sensor_signal() != 0):
		pass

	elev.elevator_hardware_set_motor_direction(DIRN_UP)

	while(elev.elevator_hardware_get_floor_sensor_signal() != 3):
		pass
