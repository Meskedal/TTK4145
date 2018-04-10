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

class Network:
	def __init__(self, heartbeatEvent, worldview_queue, worldview_foreign_queue, peers_queue2, print_lock):

		self.peers = {}
		self.lost = {}
		self.peers_queue = Queue.Queue()
		self.receiveEvent = threading.Event()
		self.broadcastEvent = threading.Event()
		self.receiveEvent.set()
		self.broadcastEvent.set()
		self.heartbeatEvent = heartbeatEvent
		self.worldview_queue = worldview_queue
		self.worldview_foreign_queue = worldview_foreign_queue
		self.peers_queue2 = peers_queue2
		self.print_lock = print_lock
		self.heartbeat = Thread(self.heartbeating)
		self.receive = Receive(self.peers_queue, self.receiveEvent, self.worldview_foreign_queue, self.print_lock)
		self.broadcast = Broadcast(self.broadcastEvent, self.worldview_queue, self.print_lock)


	def heartbeating(self):
		while(self.heartbeatEvent.isSet()):
			current_time = time()
			if not self.peers_queue.empty():
				item = self.peers_queue.get()
				self.peers[item[0]] = item[1]
				if item[0] in self.lost:
					del self.lost[item[0]]
				self.peers_queue2.put(self.peers)

			for ip in self.peers:
				if(self.peers[ip] < current_time - 1): #Hearbeat timeout time
					self.lost[ip] = current_time
					del self.peers[ip]
					break

		self.receiveEvent.clear()
		self.broadcastEvent.clear()
		#self.receive.join()
		#self.broadcast.join()
	#def network_heartbeat

class Receive:
	def __init__(self, peers_queue, receiveEvent, worldview_foreign_queue, print_lock):
		self.peers_queue = peers_queue
		self.timeout = 1.6
		self.receiveEvent = receiveEvent
		self.worldview_foreign_queue = worldview_foreign_queue
		self.print_lock = print_lock
		self.receive = Thread(self.receiving)

	def receiving(self): #Receives worldview from id and passes id with timestamp to peers_queue.										  #id:worldview is also passed to worldview_foreign_queue
		while(self.receiveEvent.isSet()):
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.settimeout(self.timeout)
			#print(self.timeout)

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
				if (self.receiveEvent.isSet()):
					self.peers_queue.put(peer_entry)
					self.worldview_foreign_queue.put(worldview_foreign)

			except socket.timeout as e:
				self.print_lock.acquire()
				print(e)
				self.print_lock.release()

class Broadcast:
	def __init__(self, broadcastEvent, worldview_queue, print_lock):
		self.broadcastEvent = broadcastEvent
		self.worldview_queue = worldview_queue
		self.print_lock = print_lock
		self.broadcast = Thread(self.broadcasting)

	def broadcasting(self):
		target_ip = '127.0.0.1'
		target_port = 20002
		while(self.broadcastEvent.isSet()):
			sleep(0.2)
			worldview = self.network_create_worldview()
			worldview = json.dumps(worldview)
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			sock.sendto(worldview, ('<broadcast>', target_port))
		return

	def network_local_ip(self):

		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		ip = s.getsockname()[0]
		s.close()
		#print(os.getpid())
		return ip + ':' +  repr(os.getpid())

	def network_create_worldview(self): #Creates worldview dictionary with ip as key
		while(self.worldview_queue.empty()):
			sleep(0.02)

		worldview = self.worldview_queue.get()
		try:
			ip = self.network_local_ip()
		except IOError as e:
			self.print_lock.acquire()
			print(e)
			self.print_lock.release()
		worldview_dict = {}
		worldview_dict[ip] = worldview
		return worldview_dict


def print_peers(Peers):
	for ip in Peers:
		print(ip + " - " + repr(Peers[ip]))
	return
