#!/usr/bin/env python


__author__      = "gitgudd"



from ctypes import *
from network import *
import os, json

os.system("gcc -c -fPIC C_interface/main.c -o C_interface/main.o")
os.system("gcc -c -fPIC C_interface/driver/elevator_hardware.c -o C_interface/driver/elevator_hardware.o")
os.system("gcc -c -fPIC C_interface/fsm.c -o C_interface/fsm.o")
os.system("gcc -c -fPIC C_interface/timer.c -o C_interface/timer.o")
os.system("gcc -c -fPIC C_interface/elevator.c -o C_interface/elevator.o")
os.system("gcc -c -fPIC C_interface/requests.c -o C_interface/requests.o")
os.system("gcc -shared -Wl,-soname,C_interface/pymain.so -o C_interface/pymain.so  C_interface/main.o C_interface/driver/elevator_hardware.o C_interface/fsm.o C_interface/timer.o C_interface/elevator.o C_interface/requests.o -lc")


N_FLOORS = 4
N_BUTTONS = 3

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2


class Elevator:
	def __init__(self, c, true_elevator):
		if(true_elevator):
			self.c = c
			self.behaviour = c.fsm_get_e_behaviour()
			self.floor = c.fsm_get_e_floor()
			self.dirn = c.fsm_get_e_dirn()
			self.requests = get_requests(c)
			self.id = network_local_ip()
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

	def worldview_to_elevator(self, worldview, id):
		self.behaviour = worldview['elevators'][id]["behaviour"]
		self.floor = worldview['elevators'][id]["floor"]
		self.dirn = worldview['elevators'][id]["dirn"]
		self.requests = worldview['elevators'][id]["requests"]
		self.id = id




def get_requests(c):
	ELEVATOR_REQUESTS = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
	for f in range(0,N_FLOORS):
		for b in range(0,N_BUTTONS):
			ELEVATOR_REQUESTS[f][b] = c.fsm_get_e_request(c_int(f),c_int(b))
	return ELEVATOR_REQUESTS

def c_main(c_main_run_event, elevator_queue, local_orders_queue, hall_order_pos_queue, print_lock):
	c = cdll.LoadLibrary('./C_interface/pymain.so')


	#print("Started")
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
					if(b != 2):
						hallorder_update(hall_order_pos_queue,f,b, 1)
					else:
						c.fsm_onRequestButtonPress(f, b)
				prev[f][b] = v

		f = c.elevator_hardware_get_floor_sensor_signal()
		#print(elevator.floor)
		if (f != -1 and f != prev):
			if(c.fsm_onFloorArrival(f)):
				for b in range (0, N_BUTTONS-1):
					hallorder_update(hall_order_pos_queue, f, b, 0)


		if(not local_orders_queue.empty()):
			local_orders = local_orders_queue.get()

			should_take_order(local_orders, elevator)

		prev = f


		if(c.timer_timedOut()):
			c.fsm_onDoorTimeout()
			c.timer_stop()
		elevator.update()

		if(elevator_queue.empty()):
			elevator_queue.put(elevator_to_dict(elevator))
		else:
			elevator_queue.get() #may get concurrency erros, maybe use task done/join
			elevator_queue.put(elevator_to_dict(elevator))

		c.usleep(inputPollRate_ms*1000)
		#print(elevator.floor)

def elevator_to_dict(elevator):
	eks = {}
	eks[elevator.id] = {}
	eks[elevator.id]["behaviour"] = elevator.behaviour
	eks[elevator.id]["floor"] = elevator.floor
	eks[elevator.id]["dirn"] = elevator.dirn
	eks[elevator.id]["requests"] = elevator.requests
	return eks

def should_take_order(worldview_local_orders, elevator): #Needs a queue from main to c_main function
	#print(worldview_local_orders)
	for f in range (0, N_FLOORS):
		for b in range (0, N_BUTTONS-1):
			if(worldview_local_orders[f][b] == 1 and elevator.requests[f][b] == 0):
				elevator.c.fsm_onRequestButtonPress(f, b)
			elif(worldview_local_orders[f][b] == 0 and elevator.requests[f][b] == 1):
				elevator.c.fsm_clear_floor(f)
				#print("order eceiv3ed")
			else:
				pass
	#print("after")
	#print elevator.requests

def hallorder_update(hall_order_pos_queue, floor, button, status):
	order = [floor, button, status]
	hall_order_pos_queue.put(order)

#main()
