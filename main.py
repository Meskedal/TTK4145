#!/usr/bin/env python

__author__      = "gitgudd"

import sys
#sys.path.insert(0, '/home/student/Desktop/TTK4145/single_elevator')
#from order_fulfillment import *
sys.path.insert(0, '/home/student/Desktop/TTK4145/Network')
from network import *
sys.path.insert(0, '/home/student/Desktop/TTK4145')


def main():
	print_lock = threading.Lock()
	heartbeat_run_event = threading.Event()
	heartbeat_run_event.set()
	heartbeat = Thread(network_heartbeat, heartbeat_run_event, print_lock)
	go = True

	while(go):
		try:
			sleep(10)
		except KeyboardInterrupt as e:
			print e
			heartbeat_run_event.clear()
			while(heartbeat.is_alive()):
				heartbeat.join(timeout = 0.1)
			print_lock.acquire()
			print("Exited Gracefully")
			print_lock.release()
			go = False

def worldview():

	return


main()