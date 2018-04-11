#!/usr/bin/env python


__author__      = "gitgudd"

from copy import deepcopy, copy
#IMPORT ELEVATOR CLASS


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
	def __init__(self, elevator, worldview, id, peers):
		self.elevator = deepcopy(elevator)
		self.id = id
		self.worldview = worldview

	def time_to_idle(self):
		duration = 0
		if self.elevator.behaviour == EB_Idle:
			elevator_dirn = self.choose_direction()
			if elevator_dirn == D_Stop:
				return duration
		elif self.elevator.behaviour == EB_Moving:
			duration += TRAVEL_TIME/2
			self.elevator.floor += self.elevator.dirn
		elif self.elevator.behaviour == EB_DoorOpenOpen:
			duration -= DOOR_OPEN_TIME/2
		while True:
			if self.should_stop():
				self.clear_at_current_floor()
				duration += DOOR_OPEN_TIME
				self.elevator.dirn = self.choose_direction();
				if self.elevator.dirn == D_Stop:
					return duration

			self.elevator.floor += self.elevator.dirn;
			duration += TRAVEL_TIME
		return duration

	def choose_direction(self):

		if self.elevator.dirn == D_Up:
			if self.assignment_above():
				return D_Up
			elif self.assignment_below():
				return D_Down
			else:
				return D_Stop
		elif self.elevator.dirn == D_Stop:
			if self.assignment_below():
				return D_Down
			elif self.assignment_above():
				return D_Up
			else:
				return D_Stop
		else:
			return D_Stop

	def assignment_above(self): # Returns boolean

		for floor in range(self.elevator.floor+1, N_FLOORS):
			for button in range(0,N_BUTTONS):
				if self.elevator.requests[floor][button]:
					return True
		return False

	def assignment_below(self): # Returns boolean
		for floor in range(0, self.elevator.floor):
			for button in range(0,N_BUTTONS):
				if self.elevator.requests[floor][button]:
					return True
		return False

	def should_stop(self): # Returns boolean

		if self.elevator.dirn == D_Down:
			if self.elevator.requests[self.elevator.floor][B_HallDown] or self.elevator.requests[self.elevator.floor][B_Cab] or not self.assignment_below():
				return True
			else:
				return False
		elif self.elevator.dirn == D_Up:
			if self.elevator.requests[self.elevator.floor][B_HallUp] or self.elevator.requests[self.elevator.floor][B_Cab] or not self.assignment_above():
				return True
			else:
				return False
		else:
			return True


	def clear_at_current_floor(self):
		for button in range(0,N_BUTTONS):
			if self.elevator.requests[self.elevator.floor][button] == 1:
				self.elevator.requests[self.elevator.floor][button] = 0

	def should_i_take_order(self, worldview, my_id, peers):
		hall_orders = worldview['hall_orders']
		for f in range (0, N_FLOORS):
			for b in range (0, N_BUTTONS-1):
				elevators_without_order = 0
				for id in peers:
					local_orders = worldview['elevators'][id]['requests']
					if(hall_orders[f][b][0] and not local_orders[f][b]):#must do this for all peers before calculating time
						elevators_without_order+= 1
					elif(not hall_orders[f][b][0] and local_orders[f][b] and id == my_id): #Does something that the function is not designed to do
						worldview['elevators'][my_id]['requests'][f][b] = 0
					else:
						break

				if elevators_without_order >= len(peers): #No elevator has taken the order, it needs to be assigned
					i_should_take = True #This elevator should take the order until mayhaps another elevator has been found
					my_duration = self.time_to_idle()

					for id in peers:
						if(id != my_id):
							other_elevator = Elevator(None, False)
							other_elevator.worldview_to_elevator(worldview['elevators'][id])
							assign_elev2 = Assigner(other_elevator)
							other_duration = assign_elev2.time_to_idle()
							if(my_duration > other_duration):a
								i_should_take = False #Another Elevator is faster
								break
							elif my_duration == other_duration:
								#print(abs(my_elevator.floor - f))
								#print("other")
								#print(abs(other_elevator.floor - f))
								if abs(my_elevator.floor - f) > abs(other_elevator.floor - f):
									print("hei")
									i_should_take = False
									break
								elif my_elevator.floor == other_elevator.floor and my_id > id:
									i_should_take = False
									break
								else:
									pass

							else:
								pass
						else:
							pass
					if(i_should_take):
						worldview['elevators'][my_id]['requests'][f][b] = 1
						#print("took order")
					else:
						pass #Check next button
				else:
					pass #A Elevator has the order
		return worldview



########################
def assignment_time_to_idle(elevator): # Remember to pass a copy of the elevator with the new unassigned order added to requests.
	duration = 0
	elevator_copy = deepcopy(elevator)
	if elevator_copy.behaviour == EB_Idle:
		elevator_dirn = assignment_choose_direction(elevator_copy)
		if elevator_dirn == D_Stop:
			return duration
	elif elevator_copy.behaviour == EB_MOVING:
		duration += TRAVEL_TIME/2
		elevator_copy.floor += elevator_copy.dirn
	elif elevator_copy.behaviour == EB_DOOROPEN:
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
