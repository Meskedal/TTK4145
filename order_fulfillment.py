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


N_FLOORS = 8
N_BUTTONS = 3

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2

SET = True
CLEAR = False

class Elevator:
	def __init__(self, c_library):
		if(c):
			self.c_library = c_library
			self.behaviour = c_library.fsm_get_e_behaviour()
			self.floor = c_library.fsm_get_e_floor()
			self.dirn = c_library.fsm_get_e_dirn()
			self.requests = self.get_requests()
			self.id = network_local_ip()
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
				requests[f][b] = self.c_library.fsm_get_e_request(c_int(floor),c_int(button))
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
		elev[self.elevator.id] = {}
		elev[self.elevator.id]["behaviour"] = self.elevator.behaviour
		elev[self.elevator.id]["floor"] = self.elevator.floor
		elev[self.elevator.id]["dirn"] = self.elevator.dirn
		elev[self.elevator.id]["requests"] = self.elevator.requests
		return elev

class Fulfiller:
	def __init__(self, Elevator, order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock):
		self.c_library = None
		self.initialize():
		self.elevator = Elevator(self.c_library)
		self.elevator_queue = elevator_queue
		self.local_orders_queue = local_orders_queue
		self.hall_order_queue = hall_order_queue
		self.print_lock = print_lock
		self.order_fulfillment_run_event = order_fulfillment_run_event

	def initialize(self):
		self.c_library = cdll.LoadLibrary('./C_interface/pymain.so')
		inputPollRate_ms = 25
		self.c_library.elevator_hardware_init()

		if(self.c_library.elevator_hardware_get_floor_sensor_signal() == -1):
			self.c_library.fsm_onInitBetweenFloors()

	def order_fulfillment(self):
		while(self.order_fulfillment_run_event.is_set()):
			prev = [[0 for x in range(0, N_BUTTONS)] for y in range(0, N_FLOORS)]
			for floor in range (0, N_FLOORS):
				for button in range (0, N_BUTTONS):
					button_status = self.c_library.elevator_hardware_get_button_signal(button, floor)
					if(button_status  and  button_status != prev[floor][button]):
						if(button != 2):
							self.hall_order_update(floor, button, SET)
						else:
							self.c_library.fsm_onRequestButtonPress(floor, button)
					prev[floor][button] = button_status

			current_floor = self.c_library.elevator_hardware_get_floor_sensor_signal()
			if (current_floor != -1 and current_floor != prev):
				if(self.c_library.fsm_onFloorArrival(current_floor)):
					for button in range (0, N_BUTTONS-1):
						self.hall_order_update(current_floor, button, CLEAR)

			self.synchronize_requests()
			#if(not local_orders_queue.empty()):
				#local_orders = local_orders_queue.get()
				#synchronize_requests(local_orders, elevator)
				#local_orders_queue.task_done()
			#prev = current_floor #Unknown if needed
			if(self.c_library.timer_timedOut()):
				self.c_library.fsm_onDoorTimeout()
				self.c_library.timer_stop()

			self.elevator.update()
			self.synchronize_elevator()
			c_library.usleep(inputPollRate_ms*1000)

	def synchronize_requests(self):
		if(not self.local_orders_queue.empty()):
			local_orders = self.local_orders_queue.get()
			for floor in range (0, N_FLOORS):
				for button in range (0, N_BUTTONS-1):
					if(local_orders[floor][button] == 1 and self.elevator.requests[floor][button] == 0):
						self.elevator.c_library.fsm_onRequestButtonPress(floor, button)
					elif(local_orders[floor][button] == 0 and self.elevator.requests[floor][button] == 1):
						self.elevator.c_library.fsm_clear_floor(floor)
					else:
						pass
			self.local_orders_queue.task_done()

	def synchronize_elevator(self):
		if(self.elevator_queue.empty()):
			self.elevator_queue.put(self.elevator.elevator_to_dict())
		else:
			self.elevator_queue.get() #may get concurrency erros, maybe use task done/join
			self.elevator_queue.put(self.elevator.elevator_to_dict())

	def hall_order_update(self, floor, button, status):
		order = [floor, button, status]
		self.hall_order_queue.put(order)



def get_requests(c):
	requests = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
	for floor in range(0,N_FLOORS):
		for button in range(0,N_BUTTONS):
			requests[f][b] = c_library.fsm_get_e_request(c_int(floor),c_int(button))
	return requests

def c_main(c_main_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock):

	c = cdll.LoadLibrary('./C_interface/pymain.so')
	inputPollRate_ms = 25

	c_library.elevator_hardware_init()

	if(c_library.elevator_hardware_get_floor_sensor_signal() == -1):
		c_library.fsm_onInitBetweenFloors()
	elevator = Elevator(c)

	while(c_main_run_event.is_set()):
		prev = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
		for f in range (0, N_FLOORS):
			for b in range (0, N_BUTTONS):
				v = c_library.elevator_hardware_get_button_signal(b, f)
				if(v  and  v != prev[f][b]):
					if(b != 2):
<<<<<<< HEAD
						hallorder_update(hall_order_pos_queue,f,b, 1)
=======
						hall_order_update(hall_order_queue,f,b, True)
>>>>>>> 1f0149959782bf263ad4dbe61ffeeb1ebabb7fa4
					else:
						c_library.fsm_onRequestButtonPress(f, b)
				prev[f][b] = v

		f = c_library.elevator_hardware_get_floor_sensor_signal()
		if (f != -1 and f != prev):
			if(c_library.fsm_onFloorArrival(f)):
				for b in range (0, N_BUTTONS-1):
<<<<<<< HEAD
					hallorder_update(hall_order_pos_queue, f, b, 0)
=======
					hall_order_update(hall_order_queue, f, b, False)
>>>>>>> 1f0149959782bf263ad4dbe61ffeeb1ebabb7fa4

		synchronize_requests(local_orders_queue, elevator)
		#if(not local_orders_queue.empty()):
			#local_orders = local_orders_queue.get()
			#synchronize_requests(local_orders, elevator)
			#local_orders_queue.task_done()

		prev = f


		if(c_library.timer_timedOut()):
			c_library.fsm_onDoorTimeout()
			c_library.timer_stop()
		elevator.update()

		if(elevator_queue.empty()):
			elevator_queue.put(elevator_to_dict(elevator))
		else:
			elevator_queue.get() #may get concurrency erros, maybe use task done/join
			elevator_queue.put(elevator_to_dict(elevator))
			elevator_queue.task_done()

		c_library.usleep(inputPollRate_ms*1000)
		#print(elevator.floor)

def elevator_to_dict(elevator):
	elev = {}
	elev[elevator.id] = {}
	elev[elevator.id]["behaviour"] = elevator.behaviour
	elev[elevator.id]["floor"] = elevator.floor
	elev[elevator.id]["dirn"] = elevator.dirn
	elev[elevator.id]["requests"] = elevator.requests
	return elev

def synchronize_requests(local_orders_queue, elevator): #Needs a queue from main to c_main function. Puts the assigned orders into the elevators own requests table.
	if(not local_orders_queue.empty()):
		local_orders = local_orders_queue.get()
		for f in range (0, N_FLOORS):
			for b in range (0, N_BUTTONS-1):
				if(local_orders[f][b] == 1 and elevator.requests[f][b] == 0):
					elevator.c_library.fsm_onRequestButtonPress(f, b)
				elif(local_orders[f][b] == 0 and elevator.requests[f][b] == 1):
					elevator.c_library.fsm_clear_floor(f)
				else:
					pass
		local_orders_queue.task_done()



def hall_order_update(hall_order_queue, floor, button, status):
	order = [floor, button, status]
	hall_order_queue.put(order)

#main()
