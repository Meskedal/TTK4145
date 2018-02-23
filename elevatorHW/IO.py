#!/usr/bin/env python


__author__      = "gitgudd"


#Number of floors. Hardware-dependent, do not modify.
N_FLOORS = 4

# Number of buttons (and corresponding lamps) on a per-floor basis
N_BUTTONS = 3

DIRN_DOWN = -1
DIRN_STOP = 0
DIRN_UP = 1

BUTTON_CALL_UP = 0
BUTTON_CALL_DOWN = 1
BUTTON_COMMAND = 2

from ctypes import cdll
import os

os.system("gcc -c -fPIC elevator_hardware.c -o elevator_hardware.o")
os.system("gcc -c -fPIC test.c -o test.o")
os.system("gcc -shared -Wl,-soname,IOdriver.so -o IOdriver.so  elevator_hardware.o test.o -lc")
#os.system("gcc -L/home/student/Desktop/TTK4145/elevatorHW -Wall -o test test.c -l")

elev = cdll.LoadLibrary('./IOdriver.so')
value = elev.foo()
print(value)

elev.elevator_hardware_init()

while(True):
	elev.elevator_hardware_set_motor_direction(DIRN_UP)
	while(elev.elevator_hardware_get_floor_sensor_signal() != 3):
		#print elev.elevator_hardware_get_floor_sensor_signal()
		pass

	elev.elevator_hardware_set_motor_direction(DIRN_DOWN)

	while(elev.elevator_hardware_get_floor_sensor_signal() != 0):
		pass
