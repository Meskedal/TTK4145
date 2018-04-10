#!/usr/bin/env python


__author__      = "gitgudd"

from copy import deepcopy, copy

## Global variables ##

N_FLOORS = 4
N_BUTTONS = 3

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2

B_HallUp = 0
B_HallDown = 1
B_Cab = 2

D_up = 1
D_down = -1
D_stop = 0

TRAVEL_TIME = 3
DOOR_OPEN_TIME = 3

########################
def assignment_time_to_idle(elevator): # Remember to pass a copy of the elevator with the new unassigned order added to requests.
	duration = 0
	elevator_copy = deepcopy(elevator)
	if elevator_copy.behaviour == EB_Idle:
		elevator_dirn = assignment_choose_direction(elevator_copy)
		if elevator_dirn == D_stop:
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
			if elevator_copy.dirn == D_stop:
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

	if elevator.dirn == D_up:
		if assignment_above(elevator):
			return D_up
		elif assignment_below(elevator):
			return D_down
		else:
			return D_stop
	elif elevator.dirn == D_stop:
		if assignment_below(elevator):
			return D_down
		elif assignment_above(elevator):
			return D_up
		else:
			return D_stop
	else:
		return D_stop



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
	if elevator.dirn == D_down:
		if elevator.requests[elevator.floor][B_HallDown] or elevator.requests[elevator.floor][B_Cab] or not assignment_below(elevator):
			return True
		else:
			return False
	elif elevator.dirn == D_up:
		if elevator.requests[elevator.floor][B_HallUp] or elevator.requests[elevator.floor][B_Cab] or not assignment_above(elevator):
			return True
		else:
			return False
	else:
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
