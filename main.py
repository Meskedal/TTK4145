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
	parser.add_argument('-f', '--alone', dest='alone', required=False, metavar='<if_elevator_alone')
	args = parser.parse_args()
	port_number = args.sim_port #Sender's email address
	alone = args.alone
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
	if alone:
		return True

def main():
	alone = init()
	pp = pprint.PrettyPrinter(indent=4)
	print(alone)

	worldview = {}
	worldview['hall_orders'] = [[[0,0] for x in range(0,N_BUTTONS-1)] for y in range(0,N_FLOORS)]
	worldview['elevators'] = {}
	worldview_queue = Queue.Queue()
	elevator_queue = Queue.Queue()
	local_orders_queue = Queue.Queue()
	hall_order_queue = Queue.Queue()
	my_id = network_local_ip()
	print_lock = threading.Lock()
	heartbeat_run_event = threading.Event()
	order_fulfillment_run_event = threading.Event()
	heartbeat_run_event.set()
	network = Network(heartbeat_run_event, worldview_queue, print_lock)

	order_fulfillment_run_event.set()
	fulfiller = Fulfiller(order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock)
	#order_fulfillment2 = Thread(order_fulfillment, order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock)
	go = True
	while(go):
		try:
			peers = network.get_peers()
			lost = network.get_lost()
			elevator_queue.join()
			elevator = elevator_queue.get()
			elevator_queue.task_done()
			id = next(iter(elevator))
			worldview['elevators'][id] = elevator[id]
			if elevator_is_ooo(worldview, my_id):
				print("oooo")
				#break

			#print id
			if len(peers) < 2:
				for f in range (0, N_FLOORS):
						for b in range (0, N_BUTTONS-1):
							worldview['elevators'][id]['requests'][f][b] = 0
							worldview['hall_orders'][f][b] =[0,0]
			#print(worldview[hall_orders])
			worldview = delete_lost_peers(worldview, peers, lost)
			#print worldview
			#print peers
			#if(not Peers_queue2.empty()):
				#Peers = Peers_queue2.get()
				#print(Peers)


			worldview_foreign = network.get_worldview_foreign()
			if (worldview_foreign):
				id_foreign = next(iter(worldview_foreign))
				#if id_foreign != my_id:
				worldview_foreign = worldview_foreign[id_foreign]
				worldview = worldview_hall_orders_correct(worldview, worldview_foreign,id_foreign)
				#worldview_foreign_queue.task_done()
			while not hall_order_queue.empty():
				order = hall_order_queue.get()
				worldview['hall_orders'][order[0]][order[1]] = [order[2], time()]
				#print worldview['hall_orders']
				if order[2] == 0:
					worldview['elevators'][my_id]['requests'][order[0]][order[1]] = order[2]
			#print "worldview"
			#print worldview['hall_orders']
			#print("local orders")
			#print(worldview['elevators'][my_id]['requests'])
			assigner_thingy = Assigner(worldview, my_id, peers) #local requests goes from 0 to 1 after assigner
			worldview = assigner_thingy.should_i_take_order()
			#print(worldview['elevators'][my_id]['requests'])
			#print worldview['hall_orders']
			#for id in worldview['elevators']:
				#print id
				#pass
			#print(worldview['hall_orders'])
			if len(peers) >= 2:
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
	#while end
	heartbeat_run_event.clear()
	order_fulfillment_run_event.clear()

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

def delete_lost_peers(worldview, peers, lost): ##FIX this
	for id in worldview['elevators']:
		if id in lost:
			del worldview['elevators'][id]
			break
	return worldview

def elevator_is_ooo(worldview, my_id):
	current_time = time()
	for f in range (0, N_FLOORS):
		for b in range (0, N_BUTTONS-1):
			hall_order_status = []
			hall_order_status = worldview['hall_orders'][f][b]
			#print repr(hall_order_status[0]) + " " +repr(f) + " " + repr(b) + " " +repr(my_id)
			#print(f)
			if hall_order_status[0] and worldview['elevators'][my_id]['requests'][f][b]:
				if current_time - hall_order_status[1] > 7:
					return True


	return False

main()
