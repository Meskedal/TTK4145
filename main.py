#!/usr/bin/env python

__author__      = "gitgudd"

#sys.path.insert(0, '/home/student/Desktop/TTK4145/single_elevator')
from single_elevator.order_fulfillment import *
#from order_assignment.order_assignment import *
#sys.path.insert(0, '/home/student/Desktop/TTK4145/Network')
from Network.network import *
from order_assignment.order_assignment import*
#sys.path.insert(0, '/home/student/Desktop/TTK4145')
#import order_assignment.order_assignment.py


def main():
	worldview = {}
	worldview['hall_orders'] = [[[0,0] for x in range(0,N_BUTTONS-1)] for y in range(0,N_FLOORS)]
	worldview['elevators'] = {}
#	print(worldview)
	worldview_foreign = {}
	worldview_queue = Queue.Queue()
	elevator_queue = Queue.Queue()
	worldview_foreign_queue = Queue.Queue()
	Peers_queue2 = Queue.Queue()
	local_orders_queue = Queue.Queue()
	hall_orders_pos_queue = Queue.Queue()
	Peers = {}
	my_id = network_local_ip()

	print_lock = threading.Lock()
	heartbeat_run_event = threading.Event()
	c_main_run_event = threading.Event()
	heartbeat_run_event.set()
	c_main_run_event.set()
	heartbeat = Thread(network_heartbeat, heartbeat_run_event, worldview_queue, worldview_foreign_queue, Peers_queue2, print_lock)
	c_main_fun = Thread(c_main, c_main_run_event, elevator_queue, local_orders_queue, hall_orders_pos_queue, print_lock)
	#worldview = elevator_queue.get()
	go = True
	while(go):
		try:
			elevator = elevator_queue.get()
			id = next(iter(elevator))
			worldview['elevators'][id] = elevator[id]
			#local_orders = worldview['elevators'][id]['requests']



			while not hall_orders_pos_queue.empty():
					#for i in range(0,len(hall_orders_pos_queue)):
				order = hall_orders_pos_queue.get()
				worldview['hall_orders'][order[0]][order[1]] = [order[2], time()]

			if(not Peers_queue2.empty()):
				item = Peers_queue2.get()
				Peers[item[0]] = item[1]
			if(not worldview_foreign_queue.empty()):
				worldview_foreign = worldview_foreign_queue.get()
				#print_lock.acquire()
				#print(worldview_foreign)
				#print_lock.release()
				id_foreign = next(iter(worldview_foreign))
				#print(worldview_foreign[id_foreign])
				worldview_foreign = worldview_foreign[id_foreign]
				#print(worldview_foreign)
				#print('mine')
				#print(worldview['hall_orders'])
				#print('foreign')
				#print(worldview_foreign['hall_orders'])
				worldview = worldview_hall_orders_correct(worldview, worldview_foreign,id_foreign)
				worldview['hall_orders'][order[0]][order[1]] = [order[2], time()]
				worldview = should_i_take_order(worldview, network_local_ip(), Peers)
				#print worldview['elevators'][network_local_ip()]['requests']

			local_orders = worldview['elevators'][id]['requests']
				#print(worldview)
			print "local orders: "
			print local_orders
			print "elevator orders: "
			print elevator[id]['requests']
			print "worldview: "
			print worldview['hall_orders']
			if (local_orders_queue.empty()):
				local_orders_queue.put(local_orders)
			if (worldview_queue.empty()):
				worldview_queue.put(worldview)

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


def worldview_hall_orders_correct(worldview, worldview_foreign, id_foreign):

	#print(worldview_foreign)
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

	worldview['elevators'][id_foreign] = worldview_foreign['elevators'][id_foreign]
	worldview['hall_orders'] = hall_orders
	return worldview

def should_i_take_order(worldview, my_id, Peers):
	hall_orders = worldview['hall_orders']
	nontaken_order = 0
	for f in range (0, N_FLOORS):
		for b in range (0, N_BUTTONS-1):
			nontaken_order = 0 #Number of elevators that does not have the order
			for id in Peers:
				local_orders = worldview['elevators'][id]['requests']
				if(hall_orders[f][b][0] == local_orders[f][b]):#must do this for all peers before calculating time
					break
				else:
					nontaken_order += 1
					pass

			if nontaken_order >= len(Peers):
				my_elevator = Elevator(None, False)
				my_elevator.worldview_to_elevator(worldview['elevators'][my_id])
				#my_elevator.print_status()
				my_duration = assignment_time_to_idle(my_elevator)

				i_should_take = True #This elevator should take the order until mayhaps another elevator has been found
				for id in Peers:
					if(id != my_id):
						other_elevator = Elevator(None, False)
						other_elevator.worldview_to_elevator(worldview['elevators'][id])
						if(my_duration > time_to_idle(other_elevator)):
							i_should_take = False #Another Elevator is faster
							break
						else:
							pass
					else:
						pass
				if(i_should_take):
					worldview['elevators'][my_id]['requests'][f][b] = 1
				else:
					pass #Check next button
			else:
				pass #A Elevator has the order
	return worldview
def worldview_from_local_elevator(worldview, local_orders_elevator):
	my_ip = network_local_ip()
	local_orders = worldview['elevators'][my_ip]['requests']
	for f in range (0, N_FLOORS):
		for b in range (0, N_BUTTONS-1):
			pass
main()
