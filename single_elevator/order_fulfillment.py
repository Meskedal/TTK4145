#!/usr/bin/env python


__author__      = "gitgudd"



from ctypes import *
import os
from LocalIP import *
import json

os.system("gcc -c -fPIC single_elevator/main.c -o single_elevator/main.o")
os.system("gcc -c -fPIC single_elevator/driver/elevator_hardware.c -o single_elevator/driver/elevator_hardware.o")
os.system("gcc -c -fPIC single_elevator/fsm.c -o single_elevator/fsm.o")
os.system("gcc -c -fPIC single_elevator/timer.c -o single_elevator/timer.o")
os.system("gcc -c -fPIC single_elevator/elevator.c -o single_elevator/elevator.o")
os.system("gcc -c -fPIC single_elevator/requests.c -o single_elevator/requests.o")
os.system("gcc -shared -Wl,-soname,single_elevator/pymain.so -o single_elevator/pymain.so  single_elevator/main.o single_elevator/driver/elevator_hardware.o single_elevator/fsm.o single_elevator/timer.o single_elevator/elevator.o single_elevator/requests.o -lc")


N_FLOORS = 4
N_BUTTONS = 3

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2


class Elevator:
	def __init__(self, c, trueElevator):
		if(trueElevator):
			self.c = c
			self.behaviour = c.fsm_get_e_behaviour()
			self.floor = c.fsm_get_e_floor()
			self.dirn = c.fsm_get_e_dirn()
			self.requests = get_requests(c)
			self.id = local_ip()
		else:
			self.c = None
			self.behaviour = None
			self.floor = None
			self.dirn = None
			self.requests = None
			self.id = None

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

	def worldview_to_elevator(self, elevator_dict):
		self.behaviour = elevator_dict["behaviour"]
		self.floor = elevator_dict["floor"]
		self.dirn = elevator_dict["dirn"]
		self.requests = elevator_dict["requests"]
		



def get_requests(c):
	ELEVATOR_REQUESTS = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
	for f in range(0,N_FLOORS):
		for b in range(0,N_BUTTONS):
			ELEVATOR_REQUESTS[f][b] = c.fsm_get_e_request(c_int(f),c_int(b))
	return ELEVATOR_REQUESTS

def c_main(c_main_run_event, elevator_queue, local_orders_queue, print_lock):
	c = cdll.LoadLibrary('./single_elevator/pymain.so')

	print("Started")
	inputPollRate_ms = 25

	c.elevator_hardware_init()  
	
	if(c.elevator_hardware_get_floor_sensor_signal() == -1):
		c.fsm_onInitBetweenFloors()
	elevator = Elevator(c,True)

	while(c_main_run_event.is_set()):
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
		#print(elevator_to_dict(elevator))
		if(elevator_queue.empty()):
			elevator_queue.put(elevator_to_dict(elevator))
		else:
			elevator_queue.get() #may get concurrency erros, maybe use task done/join
			elevator_queue.put(elevator_to_dict(elevator))
		#print_lock.acquire()
		#print(elevator_to_json(elevator))
		#print_lock.release()
		c.usleep(inputPollRate_ms*1000)

def elevator_to_dict(elevator):
	eks = {}
	eks[elevator.id] = {}
	eks[elevator.id]["behaviour"] = elevator.behaviour
	eks[elevator.id]["floor"] = elevator.floor
	eks[elevator.id]["dirn"] = elevator.dirn
	eks[elevator.id]["requests"] = elevator.requests
	return eks

def worldview(Peers):

	e = elevator()
	return e

#main()