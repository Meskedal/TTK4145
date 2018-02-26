#!/usr/bin/env python


__author__      = "gitgudd"



from ctypes import *
import os

os.system("gcc -c -fPIC main.c -o main.o")
os.system("gcc -c -fPIC driver/elevator_hardware.c -o driver/elevator_hardware.o")
os.system("gcc -c -fPIC fsm.c -o fsm.o")
os.system("gcc -c -fPIC timer.c -o timer.o")
os.system("gcc -c -fPIC elevator.c -o elevator.o")
os.system("gcc -c -fPIC requests.c -o requests.o")
os.system("gcc -shared -Wl,-soname,pymain.so -o pymain.so  main.o driver/elevator_hardware.o fsm.o timer.o elevator.o requests.o -lc")


N_FLOORS = 4
N_BUTTONS = 3

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2


class Elevator:
	def __init__(self, c):
		self.c = c
		self.behaviour = c.fsm_get_e_behaviour()
		self.floor = c.fsm_get_e_floor()
		self.dirn = c.fsm_get_e_dirn()
		self.requests = get_requests(c)

	def update(self):
		self.behaviour = self.c.fsm_get_e_behaviour()
		self.floor = self.c.fsm_get_e_floor()
		self.dirn = self.c.fsm_get_e_dirn()
		self.requests = get_requests(self.c)

	def print_status(self):
		behaviour = "Behaviour: %d\n" % self.behaviour
		floor = "Floor: %d\n" % self.floor
		dirn = "Dirn: %d" % self.dirn
		print(behaviour + floor + dirn)
		print(self.requests)
		print("")

def get_requests(c):
	ELEVATOR_REQUESTS = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
	for f in range(0,N_FLOORS):
		for b in range(0,N_BUTTONS):
			ELEVATOR_REQUESTS[f][b] = c.fsm_get_e_request(c_int(f),c_int(b))
	return ELEVATOR_REQUESTS

def c_main():
	c = cdll.LoadLibrary('./pymain.so')

	print("Started")
	inputPollRate_ms = 25

	c.elevator_hardware_init()  
	
	if(c.elevator_hardware_get_floor_sensor_signal() == -1):
		c.fsm_onInitBetweenFloors()
	elevator = Elevator(c)

	while(1):
		prev = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
		for f in range (0, N_FLOORS):
			for b in range (0, N_BUTTONS):
				v = c.elevator_hardware_get_button_signal(b, f)
				if(v  and  v != prev[f][b]):
					c.fsm_onRequestButtonPress(f, b)
				prev[f][b] = v
				
		f = c.elevator_hardware_get_floor_sensor_signal()
		
		if (f != -1 and f != prev):
			c.fsm_onFloorArrival(f)
		prev = f

		if(c.timer_timedOut()):
			c.fsm_onDoorTimeout()
			c.timer_stop()

		elevator.update()
		elevator.print_status()
		c.usleep(inputPollRate_ms*1000)

#main()