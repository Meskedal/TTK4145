#!/usr/bin/env python

__author__      = "gitgudd"
import pprint

from order_fulfillment import *
from network import *
from order_assignment import *
import subprocess
#sys.path.insert(0, '/home/student/Desktop/TTK4145')
#import order_assignment.order_assignment.py
import argparse as ap
import getpass as gp

#Get sender_email and recipient_email as arguments to the program
def init():
	parser = ap.ArgumentParser(description='Port for simulation')
	parser.add_argument('-p', '--port', dest='sim_port', required=False, metavar='<port_number>')
	args = parser.parse_args()
	port_number = args.sim_port #Sender's email address
	if port_number:
		with open('C_interface/elevator_hardware.con', 'r') as file:
			print(port_number)
			data = file.readlines()

# now change the 2nd line, note that you have to add a newline
		data[3] = "--com_port              " + port_number

		# and write everything back
		with open('C_interface/elevator_hardware.con', 'w') as file:
		    file.writelines(data)
		#subprocess.call(['cd', 'elevatorHW'])
		#subprocess.call(['./' , 'SimElevatorServer'])
	else:
		with open('C_interface/elevator_hardware.con', 'r') as file:
			print(port_number)
			data = file.readlines()

# now change the 2nd line, note that you have to add a newline
		data[3] = "--com_port              " + '15657'

		# and write everything back
		with open('C_interface/elevator_hardware.con', 'w') as file:
		    file.writelines(data)

def main():
	init()
	pp = pprint.PrettyPrinter(indent=4)


	worldview = {}
	worldview['hall_orders'] = [[[0,0] for x in range(0,N_BUTTONS-1)] for y in range(0,N_FLOORS)]
	worldview['elevators'] = {}
	worldview_queue = Queue.Queue()
	elevator_queue = Queue.Queue()
<<<<<<< HEAD
	local_orders_queue = Queue.Queue()
	hall_orders_pos_queue = Queue.Queue()
	peers = {}
=======
	worldview_foreign_queue = Queue.Queue()
	Peers_queue2 = Queue.Queue()
	local_orders_queue = Queue.Queue()
	hall_order_queue = Queue.Queue()
	Peers = {}
>>>>>>> 1f0149959782bf263ad4dbe61ffeeb1ebabb7fa4
	my_id = network_local_ip()
	print_lock = threading.Lock()
	heartbeat_run_event = threading.Event()
	order_fulfillment_run_event = threading.Event()
	heartbeat_run_event.set()
<<<<<<< HEAD
	c_main_run_event.set()
	network = Network(heartbeat_run_event, worldview_queue, print_lock)
	c_main_fun = Thread(c_main, c_main_run_event, elevator_queue, local_orders_queue, hall_orders_pos_queue, print_lock)
=======
	order_fulfillment_run_event.set()
	network = Network(heartbeat_run_event, worldview_queue, worldview_foreign_queue, Peers_queue2, print_lock)
	order_fulfillment = Thread(order_fulfillment, order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock)
>>>>>>> 1f0149959782bf263ad4dbe61ffeeb1ebabb7fa4
	go = True

	while(go):
		try:
<<<<<<< HEAD
			peers = network.get_peers()
			print peers

			elevator_queue.join()
=======
			#print elevator_queue.qsize()
>>>>>>> 1f0149959782bf263ad4dbe61ffeeb1ebabb7fa4
			elevator = elevator_queue.get()
			id = next(iter(elevator))
			worldview['elevators'][id] = elevator[id]
<<<<<<< HEAD
=======

			Peers = network.get_peers()
			print Peers
>>>>>>> 1f0149959782bf263ad4dbe61ffeeb1ebabb7fa4
			#if(not Peers_queue2.empty()):
				#Peers = Peers_queue2.get()
				#print(Peers)

			worldview_foreign = network.get_worldview_foreign()
			if (worldview_foreign):
				id_foreign = next(iter(worldview_foreign))
				worldview_foreign = worldview_foreign[id_foreign]
				worldview = worldview_hall_orders_correct(worldview, worldview_foreign,id_foreign)
				#worldview_foreign_queue.task_done()

				while not hall_order_queue.empty():
					order = hall_order_queue.get()
					worldview['hall_orders'][order[0]][order[1]] = [order[2], time()]
					if order[2] == 0:
						worldview['elevators'][network_local_ip()]['requests'][order[0]][order[1]] = order[2]

				assigner_thingy = Assigner(worldview, network_local_ip(), peers)
				worldview = assigner_thingy.should_i_take_order()
			worldview = delete_lost_peers(worldview, peers)

			#print(worldview['hall_orders'])
			local_orders = worldview['elevators'][id]['requests']
			local_orders_queue.join()
			local_orders_queue.put(local_orders)
			if (worldview_queue.empty()):
				#worldview_queue.join()
				worldview_queue.put(worldview)
				#worldview_queue.task_done()
			else:
				worldview_queue.get()
				worldview_queue.put(worldview)
				#worldview_queue.task_done()
			#print(worldview)

		except KeyboardInterrupt as e:
			print e
			heartbeat_run_event.clear()
			order_fulfillment_run_event.clear()
			#while(heartbeat.is_alive()):
				#heartbeat.join(timeout = 0.1)
			#while(c_main_fun.is_alive()):
				#c_main_fun.join(timeout = 0.1)
			print_lock.acquire()
			print("Exited Gracefully")
			print_lock.release()
			go = False

def worldview_hall_orders_correct(worldview, worldview_foreign, id_foreign):
	worldview['elevators'][id_foreign] = worldview_foreign['elevators'][id_foreign]
	hall_orders = worldview['hall_orders']
	hall_orders_foreign = worldview_foreign['hall_orders']
	for f in range (0, N_FLOORS):
			for b in range (0, N_BUTTONS-1):
				#if hall_orders[f][b][0] != hall_orders_foreign[f][b][0]:
				if hall_orders[f][b][1] < hall_orders_foreign[f][b][1]:
					hall_orders[f][b][0] = hall_orders_foreign[f][b][0]
					hall_orders[f][b][1] = hall_orders_foreign[f][b][1]
				else:
					pass

	worldview['hall_orders'] = hall_orders
	return worldview


def worldview_from_local_elevator(worldview, local_orders_elevator):
	my_ip = network_local_ip()
	local_orders = worldview['elevators'][my_ip]['requests']
	for f in range (0, N_FLOORS):
		for b in range (0, N_BUTTONS-1):
			pass
def delete_lost_peers(worldview, peers): ##FIX this
	for id in worldview['elevators']
		if id not in peers:
			del worldview['elevators'][id]
			break
	return worldview


main()
