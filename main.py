#!/usr/bin/env python

__author__      = "gitgudd"
import pprint

from order_fulfillment import *
from network import *
from order_assignment import *
from fsm import *
import subprocess




def main():
	local_orders_queue = Queue.Queue()
	worldview_queue = Queue.Queue()
	state_machine = State_machine(local_orders_queue, worldview_queue)

	elevator_queue = Queue.Queue()
	hall_order_queue = Queue.Queue()
	print_lock = threading.Lock()

	heartbeat_run_event = threading.Event()
	heartbeat_run_event.set()
	network = Network(heartbeat_run_event, worldview_queue, print_lock)

	order_fulfillment_run_event = threading.Event()
	order_fulfillment_run_event.set()
	fulfiller = Fulfiller(order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock)
	#order_fulfillment2 = Thread(order_fulfillment, order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock)
	go = True
	while(go):
		try:
			peers = network.get_peers()
			lost = network.get_lost()
			state_machine.update_peers(peers,lost)

			elevator_queue.join()
			elevator = elevator_queue.get()
			elevator_queue.task_done()
			state_machine.set_elevator(elevator)


			worldview_foreign = network.get_worldview_foreign()
			if (worldview_foreign):
				state_machine.sync_worldviews(worldview_foreign)

			while not hall_order_queue.empty():
				order = hall_order_queue.get()
				state_machine.update_order(order)
				hall_order_queue.task_done()


			state_machine.assign_orders()

			state_machine.pass_local_worldview()
			state_machine.pass_worldview()
			if state_machine.hardware_failure():
				go = False


		except KeyboardInterrupt as e:
			print e
			heartbeat_run_event.clear()
			order_fulfillment_run_event.clear()
			#while(heartbeat.is_alive()):
				#heartbeat.join(timeout = 0.1)
			#while(c_main_fun.is_alive()):
				#c_main_fun.join(timeout = 0.1)
			go = False
	#while end
	heartbeat_run_event.clear()
	order_fulfillment_run_event.clear()
	#sleep(5)
	print_lock.acquire()
	print("Exited Gracefully")
	print_lock.release()


main()
