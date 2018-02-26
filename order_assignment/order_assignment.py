#!/usr/bin/env python


__author__      = "gitgudd"

from copy import copy


# Define these elsewhere
TRAVEL_TIME = 3
DOOR_OPEN_TIME = 2      
D_up = 1                
D_down = -1
D_stop = 0
########################

def timeToIdle(elevator):
	elevator.update()
	duration = 0
	if(elevator.behaviour == EB_Idle):
		e_dirn = requests_choose_direction_py(elevator)##
		if e_dirn == D_Stop:
			return duration
	elif elevator.behaviour == EB_Moving:
		duration += TRAVEL_TIME/2
		elevator.floor += elevator.dirn
	elif elevator.behaviour == EB_DoorOpen:
		duration -= DOOR_OPEN_TIME/2
   
	while True:
		if requests_shouldStop(elevator):
			elevator = requests_clear_at_current_floor(elevator, True)
			duration += DOOR_OPEN_TIME
			elevator.dirn = requests_chooseDirection(e);
			if(e.dirn == D_Stop){
				return duration
			}
		}
		e.floor += e.direction;
		duration += TRAVEL_TIME;


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


def requests_clear_at_current_floor(elevator):
	elevator_new = copy(elevator)
	for btn in range(0,N_BUTTONS):
		if elevator_new.requests[elevator_new.floor][btn] == 1:
			elevator_new.requests[elevator_new.floor] = 0
			if simulate == False:
				return elevator

	return elevator_new






