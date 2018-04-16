#!/usr/bin/env python


__author__      = "gitgudd"


from copy import deepcopy
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

## Global variables ##

N_FLOORS = 4
N_BUTTONS = 3

B_HallUp = 0
B_HallDown = 1
B_Cab = 2

D_Up = 1
D_Down = -1
D_Stop = 0

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2

SET = 1
CLEAR = 0

UP = 0
DOWN = 1
BOTH = 2
NOONE = 3

class Elevator:
	def __init__(self, c_library):
		if(c_library):
			self.c_library = c_library
			self.behaviour = c_library.fsm_get_e_behaviour()
			self.floor = c_library.fsm_get_e_floor()
			self.dirn = c_library.fsm_get_e_dirn()
			self.requests = self.get_requests()
			self.hardware_failure = False
			self.prev_time = None
		else:
			self.c_library = None
			self.behaviour = None
			self.floor = None
			self.dirn = None
			self.requests = None
			self.id = None


	def update(self):
		self.behaviour = self.c_library.fsm_get_e_behaviour()
		self.floor = self.c_library.fsm_get_e_floor()
		self.dirn = self.c_library.fsm_get_e_dirn()
		self.requests = self.get_requests()

	def get_requests(self):
		requests = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
		for floor in range(0,N_FLOORS):
			for button in range(0,N_BUTTONS):
				requests[floor][button] = self.c_library.fsm_get_e_request(c_int(floor),c_int(button))
		return requests

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

	def elevator_to_dict(self):
		elev = {}
		elev["behaviour"] = self.behaviour
		elev["floor"] = self.floor
		elev["dirn"] = self.dirn
		elev["requests"] = self.requests
		elev["hardware_failure"] = self.hardware_failure
		return elev

	def elevator_failure(self):
		current_time = time()
		if self.behaviour == EB_Moving and self.prev_time:
			if current_time - self.prev_time > 20:
				self.hardware_failure = True
		else:
			self.prev_time = current_time


class Fulfiller:
	def __init__(self, order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue):
		self.c_library = None
		self.initialize()
		self.elevator = Elevator(self.c_library)
		self.elevator_queue = elevator_queue
		self.local_orders_queue = local_orders_queue
		self.hall_order_queue = hall_order_queue
		self.run_event = order_fulfillment_run_event
		self.inputPollRate_ms = 25
		self.c_main = Thread(self.run)


	def initialize(self):
		self.c_library = cdll.LoadLibrary('./C_interface/pymain.so')
		self.c_library.elevator_hardware_init()

		if(self.c_library.elevator_hardware_get_floor_sensor_signal() == -1):
			self.c_library.fsm_onInitBetweenFloors()

	def run(self):
		prev_button_status = [[0 for x in range(0, N_BUTTONS)] for y in range(0, N_FLOORS)]
		while(self.run_event.is_set()):
			self.poll_buttons(prev_button_status)
			self.clear_orders()
			self.synchronize_requests()
			if(self.c_library.timer_timedOut()):
				self.c_library.fsm_onDoorTimeout()
				self.c_library.timer_stop()

			self.elevator.update()
			self.elevator.elevator_failure()
			self.synchronize_elevator()
			self.c_library.usleep(self.inputPollRate_ms*500)

		print("c_main thread exited gracefully")

	def clear_orders(self):
		current_floor = self.c_library.elevator_hardware_get_floor_sensor_signal()
		if (current_floor != -1):
			elev_before = deepcopy(self.elevator.requests)
			if(self.c_library.fsm_onFloorArrival(current_floor)):
				#print "before" +repr(elev_before)
				self.elevator.update()
				#self.elevator.print_status()
				if(self.hall_order_queue.empty()):
					clear_button = self.clear_direction(current_floor, elev_before)
					if clear_button == NOONE:
						pass
					elif clear_button != BOTH:
						self.hall_order_update(current_floor, clear_button, CLEAR)
					else:
						for clear_button in range (0, N_BUTTONS-1):
							self.hall_order_update(current_floor, clear_button, CLEAR)

	def poll_buttons(self, prev_button_status):
		for floor in range (0, N_FLOORS):
			for button in range (0, N_BUTTONS):
				button_status = self.c_library.elevator_hardware_get_button_signal(button, floor)
				if(button_status  and  button_status != prev_button_status[floor][button]):
					if(button != 2):
						self.hall_order_update(floor, button, SET)
					else:
						self.c_library.fsm_onRequestButtonPress(floor, button)
				prev_button_status[floor][button] = button_status


	def synchronize_requests(self):
		while(not self.local_orders_queue.empty()):
			local_orders = self.local_orders_queue.get()
			for floor in range (0, N_FLOORS):
				for button in range (0, N_BUTTONS-1):
					if(local_orders[floor][button] == 1 and self.elevator.requests[floor][button] == 0):
						self.elevator.c_library.fsm_onRequestButtonPress(floor, button)
					elif(local_orders[floor][button] == CLEAR and self.elevator.requests[floor][button] == SET):
						self.elevator.c_library.fsm_clear_floor(floor)
					else:
						pass
			self.local_orders_queue.task_done()

	def synchronize_elevator(self):
		if(self.elevator_queue.empty()):
			self.elevator_queue.put(self.elevator.elevator_to_dict())
		else:
			self.elevator_queue.get()
			self.elevator_queue.put(self.elevator.elevator_to_dict())

	def hall_order_update(self, floor, button, status):
		order = [floor, button, status]
		self.hall_order_queue.put(order)

	def clear_direction(self, floor, elev_before):
		counter = 0
		for button in range (0, N_BUTTONS-1):
			if self.elevator.requests[floor][button] != elev_before[floor][button]:
				counter += 1
				button_dirn = button;
		if counter == 2:
			return BOTH
		elif counter == 1:
			if button_dirn == UP:
				return UP
			return DOWN
		else:
			return NOONE
