#!/usr/bin/env python
import threading, thread, Queue, socket, errno, json
from time import sleep, time
import os, sys


class Thread(threading.Thread):
	def __init__(self, t, *args):
		threading.Thread.__init__(self, target=t, args=args)
		self.daemon = True
		self.start()

class Network:
	def __init__(self, heartbeatEvent, worldview_queue, print_lock):

		self.peers = {}
		self.peers[network_local_ip()] = time()
		self.lost = {}

		self.peers_queue = Queue.Queue()
		self.worldview_foreign_queue = Queue.Queue()
		self.print_lock = print_lock

		self.heartbeatEvent = heartbeatEvent
		self.receiveEvent = threading.Event()
		self.broadcastEvent = threading.Event()
		self.receiveEvent.set()
		self.broadcastEvent.set()

		self.heartbeat = Thread(self.run)
		self.receive = Receive(self.peers_queue, self.receiveEvent, self.worldview_foreign_queue, self.print_lock)
		self.broadcast = Broadcast(self.broadcastEvent, worldview_queue, self.print_lock)


	def run(self):
		while(self.heartbeatEvent.isSet()):
			current_time = time()
			if not self.peers_queue.empty():
				item = self.peers_queue.get()
				self.peers[item[0]] = item[1]
				self.peers_queue.task_done()
				if item[0] in self.lost:
					del self.lost[item[0]]
				#self.peers_queue2.put(self.peers)

			for ip in self.peers:
				if(self.peers[ip] < current_time - 1): #Hearbeat timeout time
					self.lost[ip] = current_time
					del self.peers[ip]
					break
			#self.peers_queue.task_done()

		self.receiveEvent.clear()
		self.broadcastEvent.clear()

		self.print_lock.acquire()
		print("Thread heartbeat exited gracefully")
		self.print_lock.release()

	def get_peers(self):
		self.peers_queue.join()
		return self.peers

	def get_lost(self):
		return self.lost

	def get_worldview_foreign(self):
		if(not self.worldview_foreign_queue.empty()):
			return self.worldview_foreign_queue.get()
		else:
			return None

class Receive:
	def __init__(self, peers_queue, receiveEvent, worldview_foreign_queue, print_lock):
		self.peers_queue = peers_queue
		self.timeout = 2
		self.receiveEvent = receiveEvent
		self.worldview_foreign_queue = worldview_foreign_queue
		self.print_lock = print_lock
		self.receive = Thread(self.run)

	def socket_init(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(self.timeout)
		try:
			sock.bind(('<broadcast>', 20002))
		except:
			print 'failure to bind'
			sock.close()
			return None
		return sock

	def run(self): #Receives worldview from id and passes id with timestamp to peers_queue.
		sock = self.socket_init()
											  #id:worldview is also passed to worldview_foreign_queue
		while(self.receiveEvent.isSet()):
			try:
				data, addr = sock.recvfrom(1024)
				worldview_foreign = json.loads(data)
				#print worldview_foreign
				id_foreign = next(iter(worldview_foreign))
				timestamp = time()
				peer_entry = [id_foreign, timestamp]
				if (self.receiveEvent.isSet()):
					#peers_queue.join()
					self.peers_queue.put(peer_entry)
					#worldview_foreign_queue.join()
					self.worldview_foreign_queue.put(worldview_foreign)

			except socket.timeout as e:
				self.print_lock.acquire()
				print(e)
				self.print_lock.release()
			#except:
				#print(worldview_foreign)
				#print "Unexpected error:", sys.exc_info()[0]
				#raise
		self.print_lock.acquire()
		print("Thread receiving exited gracefully")
		self.print_lock.release()

class Broadcast:
	def __init__(self, broadcastEvent, worldview_queue, print_lock):
		self.broadcastEvent = broadcastEvent
		self.worldview_queue = worldview_queue
		self.print_lock = print_lock
		self.broadcast = Thread(self.run)

	def run(self):
		#target_ip = '127.0.0.1'
		target_port = 20002
		sock = self.sock_init()
		while(self.broadcastEvent.isSet()):
			sleep(0.2)
			worldview = self.network_create_worldview()
			worldview = json.dumps(worldview)
			if(self.broadcastEvent.isSet()):
				sock.sendto(worldview, ('<broadcast>', target_port))

		self.print_lock.acquire()
		print("Thread broadcasting exited gracefully")
		self.print_lock.release()

	def sock_init(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		return sock

	def network_create_worldview(self): #Creates worldview dictionary with ip as key
		while(self.worldview_queue.empty() and self.broadcastEvent.isSet()):
			sleep(0.02)
	#	self.worldview_queue.join()
		worldview = self.worldview_queue.get()
		#self.worldview_queue.task_done()
		try:
			ip = network_local_ip()
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

def network_local_ip():

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	s.close()
		#print(os.getpid())
	return ip + ':' +  repr(os.getpid())
