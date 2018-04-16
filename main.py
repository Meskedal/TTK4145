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
			while elevator_to_worldview_queue.empty():
				pass
			while not elevator_to_worldview_queue.empty():
				elevator = elevator_to_worldview_queue.get()
			wv_handler.worldview_update_elevator(elevator)

			worldview_foreign = network.get_worldview_foreign()
			if (worldview_foreign):
				wv_handler.sync_worldviews(worldview_foreign)
			while not hall_order_to_worldview_queue.empty():
				order = hall_order_to_worldview_queue.get()
				wv_handler.update_order(order)
				hall_order_to_worldview_queue.task_done()

			wv_handler.assign_orders()
			wv_handler.pass_local_worldview()
			wv_handler.pass_worldview_with_id()
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
