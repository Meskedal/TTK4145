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






main = cdll.LoadLibrary('./pymain.so')

def get_requests(main):
	ELEVATOR_REQUESTS = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
	for f in range(0,N_FLOORS):
		for b in range(0,N_BUTTONS):
			ELEVATOR_REQUESTS[f][b] = main.fsm_get_e_request(c_int(f),c_int(b))
	return ELEVATOR_REQUESTS

def go(main):
	print("Started")
	inputPollRate_ms = 25
	#

	main.elevator_hardware_init()  
	
	if(main.elevator_hardware_get_floor_sensor_signal() == -1):
		main.fsm_onInitBetweenFloors()

	while(1):
		prev = [[0 for x in range(0,N_BUTTONS)] for y in range(0,N_FLOORS)]
		for f in range (0, N_FLOORS):
			for b in range (0, N_BUTTONS):
				v = main.elevator_hardware_get_button_signal(b, f)
				if(v  and  v != prev[f][b]):
					main.fsm_onRequestButtonPress(f, b)
				prev[f][b] = v
				
		f = main.elevator_hardware_get_floor_sensor_signal()
		
		if (f != -1 and f != prev):
			main.fsm_onFloorArrival(f)
		prev = f

		if(main.timer_timedOut()):
			main.fsm_onDoorTimeout()
			main.timer_stop()

		main.usleep(inputPollRate_ms*1000)
		requests = get_requests(main)
		print(requests) 
		print("\n")


go(main)

def timeToIdle(main):
    duration = 0
    e_behaviour = main.get_e_behaviour()
    if(e_behaviour == EB_Idle):
        e_dirn = main.requests_chooseDirection(e)
        if(e_dirn == D_Stop):
            return duration
    elif(e_behaviour == EB_Moving):
        duration += TRAVEL_TIME/2
        e.floor += e.dirn
    elif(e_behaviour == EB_DoorOpen):
        duration -= DOOR_OPEN_TIME/2
    }


    while(true):
        if(requests_shouldStop(e)){
            e = requests_clearAtCurrentFloor(e, NULL);
            duration += DOOR_OPEN_TIME;
            e.dirn = requests_chooseDirection(e);
            if(e.dirn == D_Stop){
                return duration;
            }
        }
        e.floor += e.direction;
        duration += TRAVEL_TIME;
