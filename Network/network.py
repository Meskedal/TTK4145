#!/usr/bin/env python
from UDP import *
import threading
import Queue
class Thread(threading.Thread):
	def __init__(self, t, *args):
		threading.Thread.__init__(self, target=t, args=args)
		self.daemon = True
		self.start()


def heartbeat():
	Peers = [] #Add timestamp since last redundant check and add to Lost list after t-amout of time
	Lost = [] 
	q = Queue.Queue()
	receiveEvent = threading.Event()
	receiveEvent.set()
	broadcastEvent = threading.Event()
	broadcastEvent.set()
	receive = Thread(udp_receive_heartbeat,20002, q, 1.6, receiveEvent)
	broadcast = Thread(udp_broadcast_heartbeat, 20002, broadcastEvent)
	while(True):
		try:
			if not q.empty():
				item = q.get()
				if item not in Peers:
					Peers.append(item)

		except KeyboardInterrupt as e:
			print e
			receiveEvent.clear()
			broadcastEvent.clear()
			receive.join()
			broadcast.join()
			print Peers
			return
	
heartbeat()