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

os.system("gcc -c -fPIC main.c -o main.o")
os.system("gcc -shared -Wl,-soname,main.so -o main.so  main.o")

main = cdll.LoadLibrary('./main.so')

main.main();

