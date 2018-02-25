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









main = cdll.LoadLibrary('./pymain.so')

def go(main):
	print("Started")
	inputPollRate_ms = 25
	N_FLOORS = 4
	N_BUTTONS = 3

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
		#print(f)
		if (f != -1 and f != prev):
			main.fsm_onFloorArrival(f)
		prev = f

		if(main.timer_timedOut()):
			main.fsm_onDoorTimeout()
			main.timer_stop()
		main.usleep(inputPollRate_ms*1000)
		Elevator_requests = fsm_get_e_requests()
		print(main.fsm_get_e_floor())


go(main)