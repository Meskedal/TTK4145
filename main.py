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
	worldview_foreign = {}
	worldview_queue = Queue.Queue()
	elevator_queue = Queue.Queue()
	worldview_foreign_queue = Queue.Queue()
	Network_peers_queue = Queue.Queue()
	local_orders_queue = Queue.Queue()
	hall_orders_pos_queue = Queue.Queue()
	Peers = {}
	my_id = network_local_ip()
	print_lock = threading.Lock()
	heartbeat_run_event = threading.Event()
	c_main_run_event = threading.Event()
	heartbeat_run_event.set()
	c_main_run_event.set()
	network = Network(heartbeat_run_event, worldview_queue, worldview_foreign_queue, network_peers_queue, print_lock)
	c_main_fun = Thread(c_main, c_main_run_event, elevator_queue, local_orders_queue, hall_orders_pos_queue, print_lock)
	go = True

	while(go):
		try:
			#print elevator_queue.qsize()
			elevator_queue.join()
			elevator = elevator_queue.get()
			elevator_queue.task_done()
			id = next(iter(elevator))
			worldview['elevators'][id] = elevator[id]


			Peers = network.get_peers()
			print Peers
			#if(not Peers_queue2.empty()):
				#Peers = Peers_queue2.get()
				#print(Peers)

			if(not worldview_foreign_queue.empty()):
				worldview_foreign = worldview_foreign_queue.get()
				id_foreign = next(iter(worldview_foreign))
				worldview_foreign = worldview_foreign[id_foreign]
				worldview = worldview_hall_orders_correct(worldview, worldview_foreign,id_foreign)

				while not hall_orders_pos_queue.empty():
					order = hall_orders_pos_queue.get()
					worldview['hall_orders'][order[0]][order[1]] = [order[2], time()]
					#print ("beffore :")
					#print worldview['hall_orders']
					if order[2] == 0:
						worldview['elevators'][network_local_ip()]['requests'][order[0]][order[1]] = order[2]

				assigner_thingy = Assigner(worldview, network_local_ip(), Peers)
				#print(worldview['elevators'][network_local_ip()]['requests'])
				#print("a")
				worldview = assigner_thingy.should_i_take_order()
				#print(worldview['elevators'][network_local_ip()]['requests'])
				#p#rint("aa")
				#worldview = should_i_take_order(worldview, network_local_ip(), Peers) #INF LOOP
				#print ("after :")
				#print worldview['hall_orders']

			#print(worldview['hall_orders'])
			local_orders = worldview['elevators'][id]['requests']
			local_orders_queue.join()
			local_orders_queue.put(local_orders)
			if (worldview_queue.empty()):
				worldview_queue.put(worldview)
			#print(worldview)

		except KeyboardInterrupt as e:
			print e
			heartbeat_run_event.clear()
			c_main_run_event.clear()
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
main()
