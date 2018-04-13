#!/usr/bin/env python


__author__      = "gitgudd"

from copy import deepcopy, copy
from order_fulfillment import *


## Global variables ##

N_FLOORS = 4
N_BUTTONS = 3

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2

B_HallUp = 0
B_HallDown = 1
B_Cab = 2

D_Up = 1
D_Down = -1
D_Stop = 0

TRAVEL_TIME = 3
DOOR_OPEN_TIME = 3

class Assigner:
	def __init__(self, worldview, id, peers):
		self.elevator = Elevator(None)
		self.elevator.worldview_to_elevator(worldview, id)
		self.id = id
		self.worldview = worldview
		self.peers = peers
		self.copy_elevator = deepcopy(self.elevator)

	def time_to_idle(self):
		#return 0
		duration = 0
		if self.copy_elevator.behaviour == EB_Idle:
			elevator_dirn = self.choose_direction()
			if elevator_dirn == D_Stop:
				return duration
		elif self.copy_elevator.behaviour == EB_Moving:
			duration += TRAVEL_TIME/2
			self.copy_elevator.floor += self.copy_elevator.dirn
		elif self.copy_elevator.behaviour == EB_DoorOpen:
			duration -= DOOR_OPEN_TIME/2
		while True:
			if self.should_stop():
				self.clear_at_current_floor()
				duration += DOOR_OPEN_TIME
				self.copy_elevator.dirn = self.choose_direction();
				if self.copy_elevator.dirn == D_Stop:
					return duration

			self.copy_elevator.floor += self.copy_elevator.dirn;
			duration += TRAVEL_TIME
		return duration

	def choose_direction(self):

		if self.copy_elevator.dirn == D_Up:
			if self.assignment_above():
				return D_Up
			elif self.assignment_below():
				return D_Down
			else:
				return D_Stop
		elif self.copy_elevator.dirn == D_Stop:
			if self.assignment_below():
				return D_Down
			elif self.assignment_above():
				return D_Up
			else:
				return D_Stop
		else:
			return D_Stop

	def assignment_above(self): # Returns boolean

		for floor in range(self.copy_elevator.floor+1, N_FLOORS):
			for button in range(0,N_BUTTONS):
				if self.copy_elevator.requests[floor][button]:
					return True
		return False

	def assignment_below(self): # Returns boolean
		for floor in range(0, self.copy_elevator.floor):
			for button in range(0,N_BUTTONS):
				if self.copy_elevator.requests[floor][button]:
					return True
		return False

	def should_stop(self): # Returns boolean

		if self.copy_elevator.dirn == D_Down:
			if self.copy_elevator.requests[self.copy_elevator.floor][B_HallDown] or self.copy_elevator.requests[self.copy_elevator.floor][B_Cab] or not self.assignment_below():
				return True
			else:
				return False
		elif self.copy_elevator.dirn == D_Up:
			if self.copy_elevator.requests[self.copy_elevator.floor][B_HallUp] or self.copy_elevator.requests[self.copy_elevator.floor][B_Cab] or not self.assignment_above():
				return True
			else:
				return False
		else:
			return True


	def clear_at_current_floor(self):
		for button in range(0,N_BUTTONS):
			if self.copy_elevator.requests[self.copy_elevator.floor][button] == 1:
				self.copy_elevator.requests[self.copy_elevator.floor][button] = 0

	def should_i_take_order(self):
		worldview = self.worldview
		#counter = 0
		for floor in range (0, N_FLOORS):
			for button in range (0, N_BUTTONS-1):
				if not self.is_order_taken(floor,button):
					for id in self.peers:
						if(self.am_i_faster_than_id(id,floor)):
							worldview['elevators'][self.id]['requests'][floor][button] = 1
						else:
							self.worldview['elevators'][self.id]['requests'][floor][button] = 0
							break
				else:
					pass #Check next button
		return worldview

	def is_order_taken(self, floor, button):
		hall_orders = self.worldview['hall_orders']
		elevators_without_order = 0
		for id in self.peers:
			#print("")
			#print(self.peers)
			#print(self.worldview['elevators'])
			try:
				local_orders = self.worldview['elevators'][id]['requests']
				if(hall_orders[floor][button][0] and not local_orders[floor][button]):#must do this for all peers before calculating time
					elevators_without_order += 1
				elif(not hall_orders[floor][button][0] and local_orders[floor][button] and id == self.id): #Does something that the function is not designed to do
					self.worldview['elevators'][self.id]['requests'][floor][button] = 0
				else:
					break #The order is either taken or nonexistent

			except KeyError as e:
				print(e)
				print(self.worldview['elevators'])

		if elevators_without_order >= len(self.peers): #No elevator has taken the order, it needs to be assigned
			return False
		return True

	def am_i_faster_than_id(self, id, floor):
		my_duration = self.time_to_idle()
		if(id != self.id):
			other_elevator = Assigner(self.worldview, id, self.peers)
			other_duration = other_elevator.time_to_idle()
			if other_elevator.elevator.behaviour == EB_DoorOpen and other_elevator.elevator.floor == floor:
				return False #Another elevator is currently at the ordered floor
			elif my_duration > other_duration:
				return False #Another Elevator is faster
			elif my_duration == other_duration:
				if abs(self.elevator.floor - floor) > abs(other_elevator.elevator.floor - floor):
					return False #The other elevator is closer
				elif abs(self.elevator.floor - floor) - abs(other_elevator.elevator.floor - floor) == 0 and self.id > id:
					return False #The elevator with the lowest id takes order
		return True






########################
def assignment_time_to_idle(elevator): # Remember to pass a copy of the elevator with the new unassigned order added to requests.
	duration = 0
	elevator_copy = deepcopy(elevator)
	if elevator_copy.behaviour == EB_Idle:
		elevator_dirn = assignment_choose_direction(elevator_copy)
		if elevator_dirn == D_Stop:
			return duration
	elif elevator_copy.behaviour == EB_Moving:
		duration += TRAVEL_TIME/2
		elevator_copy.floor += elevator_copy.dirn
	elif elevator_copy.behaviour == EB_DoorOpen:
		duration -= DOOR_OPEN_TIME/2
	while True:
		if assignment_should_stop(elevator_copy):
			elevator_copy = assignment_clear_at_current_floor(elevator_copy, True)
			duration += DOOR_OPEN_TIME
			elevator_copy.dirn = assignment_choose_direction(elevator_copy);
			if elevator_copy.dirn == D_Stop:
				return duration

		elevator_copy.floor += elevator_copy.dirn;
		duration += TRAVEL_TIME
	return duration

def assignment_distance_to_order(elevator):
	distance = 0
	for f in range(0, N_FLOORS):
		for btn in range(0,N_BUTTONS):
			if elevator.requests[f][btn]:
				distance = abs(elevator.floor - f)
	return distance



def assignment_choose_direction(elevator):

	if elevator.dirn == D_Up:
		if assignment_above(elevator):
			return D_Up
		elif assignment_below(elevator):
			return D_Down
		else:
			return D_Stop
	elif elevator.dirn == D_Stop:
		if assignment_below(elevator):
			return D_Down
		elif assignment_above(elevator):
			return D_Up
		else:
			return D_Stop
	else:
		return D_Stop



def assignment_above(elevator): # Returns boolean

	for f in range(elevator.floor+1, N_FLOORS):
		for btn in range(0,N_BUTTONS):
			if elevator.requests[f][btn]:
				return True
	return False

def assignment_below(elevator): # Returns boolean
	for f in range(0, elevator.floor):
		for btn in range(0,N_BUTTONS):
			if elevator.requests[f][btn]:
				return True
	return False

def assignment_should_stop(elevator): # Returns boolean
	#print "dirn: " + repr(elevator.dirn)
	#print "floor: " + repr(elevator.floor)
	#print (elevator.dirn)
	#print(elevator.floor)
	#print(elevator.requests)
	if elevator.dirn == D_Down:
		if elevator.requests[elevator.floor][B_HallDown] or elevator.requests[elevator.floor][B_Cab] or not assignment_below(elevator):
			#print("case 1")
			#print(elevator.floor)
			#print(elevator.requests)
			return True
		else:
			return False
	elif elevator.dirn == D_Up:
		if elevator.requests[elevator.floor][B_HallUp] or elevator.requests[elevator.floor][B_Cab] or not assignment_above(elevator):
			#print("case 2")
			return True
		else:
			return False
	else:
		#print("3")
		return True


def assignment_clear_at_current_floor(elevator, simulate):
	#print("hei")
	elevator_new = deepcopy(elevator)
	#print elevator_new.floor
	for btn in range(0,N_BUTTONS):
		if elevator_new.requests[elevator_new.floor][btn] == 1:
			elevator_new.requests[elevator_new.floor][btn] = 0
			if simulate == False:
				if elevator.requests[elevator.floor][btn] == 1:
					elevator.requests[elevator.floor][btn] = 0
				return  elevator

	return elevator_new

#hei
