#!/usr/bin/env python

__author__      = "gitgudd"

#sys.path.insert(0, '/home/student/Desktop/TTK4145/single_elevator')
from single_elevator.order_fulfillment import *
#sys.path.insert(0, '/home/student/Desktop/TTK4145/Network')
from Network.network import *
#sys.path.insert(0, '/home/student/Desktop/TTK4145')
#import order_assignment.order_assignment.py
 

def main():
	worldview = {}
	elevator_queue = Queue.Queue()
	print_lock = threading.Lock()
	heartbeat_run_event = threading.Event()
	c_main_run_event = threading.Event()
	heartbeat_run_event.set()
	c_main_run_event.set()
	heartbeat = Thread(network_heartbeat, heartbeat_run_event, print_lock)
	c_main_fun = Thread(c_main, c_main_run_event, print_lock)
	go = True

	while(go):
		try:
			sleep(10)
		except KeyboardInterrupt as e:
			print e
			heartbeat_run_event.clear()
			c_main_run_event.clear()
			while(heartbeat.is_alive()):
				heartbeat.join(timeout = 0.1)
			while(c_main_fun.is_alive()):
				c_main_fun.join(timeout = 0.1)
			print_lock.acquire()
			print("Exited Gracefully")
			print_lock.release()
			go = False


main()