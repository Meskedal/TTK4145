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
	def __init__(self, heartbeat_run_event, worldview_queue):

		self.peers = {}
		#self.peers[] = time()
		self.lost = {}

		self.peers_queue = Queue.Queue()
		self.worldview_foreign_queue = Queue.Queue()

		self.run_event = heartbeat_run_event
		self.receive_run_event = threading.Event()
		self.broadcast_run_event = threading.Event()
		self.receive_run_event.set()
		self.broadcast_run_event.set()

		self.heartbeat = Thread(self.run)
		self.receive = Receive(self.peers_queue, self.receive_run_event, self.worldview_foreign_queue)
		self.broadcast = Broadcast(self.broadcast_run_event, worldview_queue)


	def run(self):
		while(self.run_event.isSet()):
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

		self.receive_run_event.clear()
		self.broadcast_run_event.clear()

		print("Thread heartbeat exited gracefully")


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
	def __init__(self, peers_queue, receive_run_event, worldview_foreign_queue):
		self.peers_queue = peers_queue
		self.timeout = 2
		self.run_event = receive_run_event
		self.worldview_foreign_queue = worldview_foreign_queue
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
		while(self.run_event.isSet()):
			try:
				data, addr = sock.recvfrom(1024)
				worldview_foreign = json.loads(data)
				#print worldview_foreign
				id_foreign = next(iter(worldview_foreign))
				timestamp = time()
				peer_entry = [id_foreign, timestamp]
				if (self.run_event.isSet()):
					#peers_queue.join()
					self.peers_queue.put(peer_entry)
					#worldview_foreign_queue.join()
					self.worldview_foreign_queue.put(worldview_foreign)

			except socket.timeout as e:
				print(e)
				raise

		print("Thread receiving exited gracefully")


class Broadcast:
	def __init__(self, broadcast_run_event, worldview_queue):
		self.run_event = broadcast_run_event
		self.worldview_queue = worldview_queue
		self.broadcast = Thread(self.run)

	def run(self):
		#target_ip = '127.0.0.1'
		target_port = 20002
		sock = self.sock_init()
		while(self.run_event.isSet()):
			sleep(0.1)
			while(self.worldview_queue.empty() and self.run_event.isSet()):
				sleep(0.02)
			while(not self.worldview_queue.empty()):
					worldview = self.worldview_queue.get()
			worldview = json.dumps(worldview)
			if(self.run_event.isSet()):
				sock.sendto(worldview, ('<broadcast>', target_port))
			self.worldview_queue.task_done()

		print("Thread broadcasting exited gracefully")

	def sock_init(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		return sock

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
