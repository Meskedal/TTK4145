#!/usr/bin/env python
import threading, thread, Queue, socket, errno, json
from time import sleep, time
import os
#from ..Network.network import *


class Thread(threading.Thread):
	def __init__(self, t, *args):
		threading.Thread.__init__(self, target=t, args=args)
		self.daemon = True
		self.start()

def print_peers(Peers):
	for ip in Peers:
		print(ip + " - " + repr(Peers[ip]))
	return

def network_heartbeat(heartbeatEvent, worldview_queue, worldview_foreign_queue, peers_queue2, print_lock):
	peers = {} #Add timestamp since last redundant check and add to Lost list after t-amout of time
	lost = {}
	peers_queue = Queue.Queue()
	receiveEvent = threading.Event()
	broadcastEvent = threading.Event()
	receiveEvent.set()
	broadcastEvent.set()
	receive = Thread(network_receive_heartbeat, peers_queue, 1.6, receiveEvent, worldview_foreign_queue, print_lock)
	broadcast = Thread(network_broadcast_heartbeat, broadcastEvent, worldview_queue, print_lock)

	while(heartbeatEvent.isSet()):
		current_time = time()
		if not peers_queue.empty():
			item = peers_queue.get()
			peers[item[0]] = item[1]
			if item[0] in lost:
				del lost[item[0]]
			peers_queue2.put(peers)

		for ip in peers:
			if(peers[ip] < current_time - 1): #Hearbeat timeout time
				lost[ip] = current_time
				del peers[ip]
				break

	receiveEvent.clear()
	broadcastEvent.clear()
	receive.join()
	broadcast.join()

	#print_lock.acquire()
	#print_peers(Peers)
	#print_lock.release()

#heartbeat()
def network_broadcast_heartbeat(broadcastEvent, worldview_queue, print_lock):#Broadcasts the JSON formatted worldview of the local id.
	target_ip = '127.0.0.1'
	target_port = 20002
	while(broadcastEvent.isSet()):
		sleep(0.2)
		worldview = network_create_worldview(worldview_queue, print_lock)
		worldview = json.dumps(worldview)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		#s.sendto(data, ('<broadcast>', MYPORT))
		sock.sendto(worldview, ('<broadcast>', target_port))

def network_receive_heartbeat(peers_queue, timeout, receiveEvent, worldview_foreign_queue, print_lock): #Receives worldview from id and passes id with timestamp to peers_queue.
													  #id:worldview is also passed to worldview_foreign_queue
	while(receiveEvent.isSet()):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(timeout)

		try:
			sock.bind(('<broadcast>', 20002))
		except:
			print 'failure to bind'
			sock.close()

		try:
			data, addr = sock.recvfrom(1024)
			worldview_foreign = json.loads(data)
			id_foreign = next(iter(worldview_foreign))
			timestamp = time()
			peer_entry = [id_foreign, timestamp]
			if (receiveEvent.isSet()):
				peers_queue.put(peer_entry)

				worldview_foreign_queue.put(worldview_foreign)
		except socket.timeout as e:
			print_lock.acquire()
			print(e)
			print_lock.release()

def network_create_worldview(worldview_queue, print_lock): #Creates worldview dictionary with ip as key
	while(worldview_queue.empty()):
		sleep(0.02)

	worldview = worldview_queue.get()
	try:
		ip = network_local_ip()
	except IOError as e:
		print_lock.acquire()
		print(e)
		print_lock.release()
	worldview_dict = {}
	worldview_dict[ip] = worldview
	return worldview_dict


def network_local_ip():

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	s.close()
	#print(os.getpid())
	return ip + ':' +  repr(os.getpid())
