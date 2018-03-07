#!/usr/bin/env python
from UDP import *
import threading, thread, Queue


class Thread(threading.Thread):
	def __init__(self, t, *args):
		threading.Thread.__init__(self, target=t, args=args)
		self.daemon = True
		self.start()

def print_peers(Peers):
	for ip in Peers:
		print(ip + " - " + repr(Peers[ip]))
	return

def network_heartbeat(heartbeatEvent, worldview_queue, worldview_foreign_queue, Peers_queue2, print_lock):
	peers = {} #Add timestamp since last redundant check and add to Lost list after t-amout of time
	lost = {}
	Peers_queue = Queue.Queue()
	receiveEvent = threading.Event()
	broadcastEvent = threading.Event()
	receiveEvent.set()
	broadcastEvent.set()
	receive = Thread(udp_receive_heartbeat, peers_queue, 1.6, receiveEvent, worldview_foreign_queue, print_lock)
	broadcast = Thread(udp_broadcast_heartbeat, broadcastEvent, worldview_foreign_queue, print_lock)

	while(heartbeatEvent.isSet()):
		current_time = time()
		if not peers_queue.empty():
			item = peers_queue.get()
			peers_queue2.put(item)
			peers[item[0]] = item[1]
			if item[0] in lost:
				del lost[item[0]]

		for ip in peers:
			if(peers[ip] < current_time - 15): #Hearbeat timeout time
				lost[ip] = current_time
				del peers[ip]

	receiveEvent.clear()
	broadcastEvent.clear()
	receive.join()
	broadcast.join()

	print_lock.acquire()
	print_peers(Peers)
	print_lock.release()

#heartbeat()
