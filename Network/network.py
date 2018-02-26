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

def network_heartbeat(heartbeatEvent, print_lock):
	Peers = {} #Add timestamp since last redundant check and add to Lost list after t-amout of time
	Lost = {}
	q = Queue.Queue()
	receiveEvent = threading.Event()
	broadcastEvent = threading.Event()
	receiveEvent.set()
	broadcastEvent.set()
	receive = Thread(udp_receive_heartbeat,20002, q, 1.6, receiveEvent, print_lock)
	broadcast = Thread(udp_broadcast_heartbeat, 20002, broadcastEvent, print_lock)

	while(heartbeatEvent.isSet()):
		current_time = time()
		if not q.empty():
			item = q.get()
			Peers[item[0]] = item[1]
			if item[0] in Lost:
				del Lost[item[0]]

		for ip in Peers:
			if(Peers[ip] < current_time - 15): #Hearbeat timeout time
				Lost[ip] = current_time
				del Peers[ip]

	receiveEvent.clear()
	broadcastEvent.clear()
	receive.join()
	broadcast.join()

	print_lock.acquire()
	print_peers(Peers)
	print_lock.release()

#heartbeat()