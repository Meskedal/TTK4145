#!/usr/bin/env python

__author__      = "gitgudd"

#sys.path.insert(0, '/home/student/Desktop/TTK4145/single_elevator')
from single_elevator.order_fulfillment import *
#from order_assignment.order_assignment import *
#sys.path.insert(0, '/home/student/Desktop/TTK4145/Network')
from Network.network import *
#sys.path.insert(0, '/home/student/Desktop/TTK4145')
#import order_assignment.order_assignment.py
 

def main():
	worldview = {}
	worldview_queue = Queue.Queue()
	elevator_queue = Queue.Queue()

	print_lock = threading.Lock()
	heartbeat_run_event = threading.Event()
	c_main_run_event = threading.Event()
	heartbeat_run_event.set()
	c_main_run_event.set()
	heartbeat = Thread(network_heartbeat, heartbeat_run_event, worldview_queue, print_lock)
	c_main_fun = Thread(c_main, c_main_run_event, elevator_queue, print_lock)

	go = True

	while(go):
		try:
			sleep(10)

			#if(worldview_queue.empty):
				#worldview_queue.
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

def elevator_to_worldview():
	return

def worldview_hall_orders_correct(worldview, worldview_foreign, id_foreign):
	hall_orders = worldview['hall_orders']
	hall_orders_foreign = worldview_foreign['hall_orders']
	for f in range (0, N_FLOORS):
			for b in range (0, N_BUTTONS-1):
				if hall_orders[f][b][0] != hall_orders_foreign[f][b][0]:
					if hall_orders[f][b][1] < hall_orders_foreign[f][b][1]:
						hall_orders[f][b][0] = hall_orders_foreign[f][b][0]
						hall_orders[f][b][1] = hall_orders_foreign[f][b][1]
					else:
						pass

	worldview[elevators][id_foreign] = worldview_foreign[elevators][id_foreign]
	worldview['hall_orders'] = hall_orders
	return worldview

def should_i_take_order(worldview, my_id, Peers):
	hall_orders = worldview['hall_orders']
	nontaken_order = 0
	for f in range (0, N_FLOORS):
		for b in range (0, N_BUTTONS-1):
			nontaken_order = 0 #Number of elevators that does not have the order
			for i in range(0, len(Peers)):
				local_orders = worldview['elevators'][Peers[i]]
				if(hall_orders[f][b][0] == local_orders[f][b]):#must do this for all peers before calculating time
					break
				else:
					nontaken_order += 1
					pass
			
			if nontaken_order >= len(Peers):
				my_elevator = Elevator(None, False)
				my_elevator.worldview_to_elevator(worldview['elevators'][my_id])
				my_duration = time_to_idle(my_elevator)
				i_should_take = True #This elevator should take the order until mayhaps another elevator has been found
				for i in range(0, len(Peers)):
					if(Peers[i] != my_id):
						other_elevator = Elevator(None, False)
						other_elevator.worldview_to_elevator(worldview['elevators'][Peers[i]])
						if(my_duration > time_to_idle(other_elevator)):
							i_should_take = False #Another Elevator is faster
							break
						else:
							pass
					else:
						pass
				if(i_should_take):
					worldview['elevators'][my_id][f][b] = 1
				else:
					pass #Check next button
			else:
				pass #A Elevator has the order
	return worldview
				

