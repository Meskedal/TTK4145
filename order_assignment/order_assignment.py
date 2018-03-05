#!/usr/bin/env python


__author__      = "gitgudd"

from copy import deepcopy


## Global variables ## 

N_FLOORS = 4
N_BUTTONS = 3

EB_Idle = 0
EB_DoorOpen = 1
EB_Moving = 2

D_up = 1                
D_down = -1
D_stop = 0

TRAVEL_TIME = 3
DOOR_OPEN_TIME = 3      


########################
class worldview()



def time_to_idle(elevator): # Remember to pass a copy of the elevator with the new unassigned order added to requests.
	duration = 0
	if elevator.behaviour == EB_Idle:
		elevator_dirn = requests_choose_direction_py(elevator)
		if elevator_dirn == D_Stop:
			return duration
	elif elevator.behaviour == EB_Moving:
		duration += TRAVEL_TIME/2
		elevator_copy.floor += elevator_copy.dirn
	elif elevator_copy.behaviour == EB_DoorOpen:
		duration -= DOOR_OPEN_TIME/2
   
	while True:
		if requests_shouldStop(elevator_copy):
			elevator = requests_clear_at_current_floor(elevator, True)
			duration += DOOR_OPEN_TIME
			elevator.dirn = requests_choose_direction_py(elevator);
			if elevator.dirn == D_Stop
				return duration
			
		
		elevator.floor += elevator.dirn;
		duration += TRAVEL_TIME
	return duration


def requests_choose_direction_py(elevator):

	if elevator.dirn == D_up:
		if requests_above_py(elevator):
			return D_up
		elif requests_below_py(elevator):
			return D_down
		else:
			return D_stop
	elif elevator.dirn == D_stop:
		if requests_below_py(elevator):
			return D_down
		elif requests_above_py(elevator):
			return D_up
		else: 
			return D_stop
	else:
		return D_stop


def requests_above_py(elevator): # Returns boolean

	for f in range(elevator.floor+1, N_FLOORS):
		for btn in range(0,N_BUTTONS):
			if elevator.requests[f][btn]:
				return True
	return False

def requests_below_py(elevator): # Returns boolean
	for f in range(0, elevator.floor):
		for btn in range(0,N_BUTTONS):
			if elevator.requests[f][btn]:
				return True
	return False

def requests_should_stop(elevator): # Returns boolean
	if elevator.dirn == D_Down:
		if elevator.requests[elevator.floor][B_HallDown] or elevator.requests[elevator.floor][B_Cab] or not requests_below(elevator):
			return True
		else:
			return False
	elif elevator.drin == D_up:
		if elevator.requests[elevator.floor][B_HallDown] or elevator.requests[elevator.floor][B_Cab] or not requests_above(elevator):
			return True
		else:
			return False
	else:
		return True


def requests_clear_at_current_floor(elevator, simulate):
	elevator_new = deepcopy(elevator)
	for btn in range(0,N_BUTTONS):
		if elevator_new.requests[elevator_new.floor][btn] == 1:
			elevator_new.requests[elevator_new.floor] = 0
			if simulate == False:
				if elevator.requests[elevator.floor][btn] == 1:
					elevator.requests[elevator.floor] = 0
				return  elevator

	return elevator_new






