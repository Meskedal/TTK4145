#!/usr/bin/env python
from UDP import *
import threading
import Queue

class Thread(threading.Thread):
	def __init__(self, t, *args):
		threading.Thread.__init__(self, target=t, args=args)
		self.daemon = True
		self.start()

def print_peers(Peers):
	for ip in Peers:
		print(ip + " - " + repr(Peers[ip]))
	return

def heartbeat():
	Peers = {} #Add timestamp since last redundant check and add to Lost list after t-amout of time
	Lost = {}
	q = Queue.Queue()
	receiveEvent = threading.Event()
	broadcastEvent = threading.Event()
	receiveEvent.set()
	broadcastEvent.set()
	receive = Thread(udp_receive_heartbeat,20002, q, 1.6, receiveEvent)
	broadcast = Thread(udp_broadcast_heartbeat, 20002, broadcastEvent)

	while(True):
		current_time = time()
		try:
			if not q.empty():
				item = q.get()
				Peers[item[0]] = item[1]
				if item[0] in Lost:
					del Lost[item[0]]

		except KeyboardInterrupt as e:
			print (e)
			receiveEvent.clear()
			broadcastEvent.clear()
			receive.join()
			broadcast.join()
			print_peers(Peers)
			return

		for ip in Peers:
			if(Peers[ip] < current_time - 15): #Hearbeat timeout time
				Lost[ip] = current_time
				del Peers[ip]

#heartbeat()