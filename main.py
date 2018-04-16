#!/usr/bin/env python

__author__      = "gitgudd"

from order_fulfillment import *
from network import *
from worldview_handler import *




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
			if worldview_foreign:
				wv_handler.sync_worldviews(worldview_foreign)

			while not hall_order_to_worldview_queue.empty():
				order = hall_order_to_worldview_queue.get()
				wv_handler.update_order(order)
				hall_order_to_worldview_queue.task_done()

			wv_handler.assign_orders()
			wv_handler.pass_local_worldview() #sends local orders to fullfiller
			wv_handler.pass_worldview_with_id() #sends worldview to broadcaster

			if wv_handler.local_hardware_failure(): #if true, the elevator disconnects itself until restart
				go = False

		except KeyboardInterrupt as e:
			print e
			heartbeat_run_event.clear()
			order_fulfillment_run_event.clear()
			go = False

	heartbeat_run_event.clear()
	order_fulfillment_run_event.clear()
	sleep(2) #enough time for the other threads to exit

main()
