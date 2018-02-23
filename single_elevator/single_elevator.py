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

#os.system("gcc -c -fPIC main.c -o main.o")
#os.system("gcc -c -fPIC driver/io.c -o driver/io.o")
os.system("gcc -c -fPIC elevator_io_device.c -o elevator_io_device.o")
#os.system("gcc -c -fPIC driver/elevator_hardware.c -o driver/elevator_hardware.o")
#os.system("gcc -c -fPIC fsm.c -o fsm.o")
#os.system("gcc -c -fPIC timer.c -o timer.o")
#os.system("gcc -c -fPIC elevator.c -o elevator.o")
#os.system("gcc -c -fPIC requests.c -o requests.o")
#os.system("gcc -c -fPIC elevator_io_device.c -o elevator_io_device.o")

#os.system("gcc -shared -Wl,-soname,pymain.so -o pymain.so  main.o driver/elevator_hardware.o fsm.o timer.o elevator.o requests.o elevator_io_device.o driver/io.o -lc")

#main = cdll.LoadLibrary('./pymain.so')

#main.main()

