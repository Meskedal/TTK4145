#!/usr/bin/env python

__author__      = "gitgudd"
import pprint

from order_fulfillment import *
from network import *
from fsm import *




def main():
	local_orders_to_fullfilment_queue = Queue.Queue()
	worldview_to_broadcast_queue = Queue.Queue()
	elevator_to_worldview_queue = Queue.Queue()
	hall_order_to_worldview_queue = Queue.Queue()

	wv_handler = Worldview_handler(local_orders_to_fullfilment_queue, worldview_to_broadcast_queue)



	heartbeat_run_event = threading.Event()
	heartbeat_run_event.set()
	network = Network(heartbeat_run_event, worldview_to_broadcast_queue)

	order_fulfillment_run_event = threading.Event()
	order_fulfillment_run_event.set()
	fulfiller = Fulfiller(order_fulfillment_run_event, elevator_to_worldview_queue, local_orders_to_fullfilment_queue, hall_order_to_worldview_queue)
	#order_fulfillment2 = Thread(order_fulfillment, order_fulfillment_run_event, elevator_queue, local_orders_queue, hall_order_queue, print_lock)
	go = True
	while(go):
		try:
			peers, lost_peers = network.get_peers()
			wv_handler.update_peers(peers,lost_peers)
			print(1)
			#elevator_to_worldview_queue.join()
			elevator = elevator_to_worldview_queue.get()
			#elevator_to_worldview_queue.task_done()
			print(2)
			wv_handler.worldview_update_elevator(elevator)
			print(3)

			worldview_foreign = network.get_worldview_foreign()
			if (worldview_foreign):
				print(4)
				wv_handler.sync_worldviews(worldview_foreign)
			print(5)
			while not hall_order_to_worldview_queue.empty():
				order = hall_order_to_worldview_queue.get()
				print(6)
				wv_handler.update_order(order)
				hall_order_to_worldview_queue.task_done()

			print(7)
			wv_handler.assign_orders()
			print(8)
			wv_handler.pass_local_worldview()
			print(9)
			wv_handler.pass_worldview_with_id()
			print(10)
			if wv_handler.local_hardware_failure():
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
	print("Exited Gracefully")


main()
