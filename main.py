#!/usr/bin/env python

__author__      = "gitgudd"
import pprint

from single_elevator.order_fulfillment import *
from Network.network import *
from order_assignment.order_assignment import*
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
		with open('single_elevator/elevator_hardware.con', 'r') as file:
			print(port_number)
			data = file.readlines()

# now change the 2nd line, note that you have to add a newline
		data[3] = "--com_port              " + port_number

		# and write everything back
		with open('single_elevator/elevator_hardware.con', 'w') as file:
		    file.writelines(data)
		#subprocess.call(['cd', 'elevatorHW'])
		#subprocess.call(['./' , 'SimElevatorServer'])
	else:
		with open('single_elevator/elevator_hardware.con', 'r') as file:
			print(port_number)
			data = file.readlines()

# now change the 2nd line, note that you have to add a newline
		data[3] = "--com_port              " + '15657'

		# and write everything back
		with open('single_elevator/elevator_hardware.con', 'w') as file:
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
	go = True

	while(go):
		try:
			elevator = elevator_queue.get()
			id = next(iter(elevator))
			worldview['elevators'][id] = elevator[id]

			if(not Peers_queue2.empty()):
				Peers = Peers_queue2.get()

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


				worldview = should_i_take_order(worldview, network_local_ip(), Peers) #INF LOOP
				#print ("after :")
				#print worldview['hall_orders']


			local_orders = worldview['elevators'][id]['requests']

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

def should_i_take_order(worldview, my_id, Peers):
	hall_orders = worldview['hall_orders']
	nontaken_order = 0
	for f in range (0, N_FLOORS):
		for b in range (0, N_BUTTONS-1):
			nontaken_order = 0 #Number of elevators that does not have the order
			for id in Peers:
				local_orders = worldview['elevators'][id]['requests']
				if(hall_orders[f][b][0] and not local_orders[f][b]):#must do this for all peers before calculating time
					nontaken_order += 1
					pass
				elif(not hall_orders[f][b][0] and local_orders[f][b] and id == my_id):
					worldview['elevators'][my_id]['requests'][f][b] = 0
				else:
					break

			if nontaken_order >= len(Peers):

				my_elevator = Elevator(None, False)
				my_elevator.worldview_to_elevator(worldview['elevators'][my_id])
				my_duration = Assigner.time_to_idle(my_elevator)


				print("my duration: " + repr(my_duration))

				i_should_take = True #This elevator should take the order until mayhaps another elevator has been found
				for id in Peers:
					if(id != my_id):
						other_elevator = Elevator(None, False)
						other_elevator.worldview_to_elevator(worldview['elevators'][id])
						other_duration = Assigner.time_to_idle(other_elevator)
						if(my_duration > other_duration):
							i_should_take = False #Another Elevator is faster
							break
						elif my_duration == other_duration:
							#print(abs(my_elevator.floor - f))
							#print("other")
							#print(abs(other_elevator.floor - f))
							if abs(my_elevator.floor - f) > abs(other_elevator.floor - f):
								print("hei")
								i_should_take = False
								break
							elif my_elevator.floor == other_elevator.floor and my_id > id:
								i_should_take = False
								break
							else:
								pass

						else:
							pass
					else:
						pass
				if(i_should_take):
					worldview['elevators'][my_id]['requests'][f][b] = 1
					#print("took order")
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
