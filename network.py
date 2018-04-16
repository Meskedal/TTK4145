#!/usr/bin/env python
import threading, thread, Queue, socket, json
from time import sleep, time



class Thread(threading.Thread):
	def __init__(self, t, *args):
		threading.Thread.__init__(self, target=t, args=args)
		self.daemon = True
		self.start()

class Network:
	def __init__(self, heartbeat_run_event, worldview_queue):
		self.heartbeat_timeout = 2
		self.peers = {}
		self.lost_peers = {}

		self.peers_queue = Queue.Queue()
		self.worldview_foreign_queue = Queue.Queue()

		self.receive_run_event = threading.Event()
		self.broadcast_run_event = threading.Event()
		self.receive_run_event.set()
		self.broadcast_run_event.set()

		self.run_event = heartbeat_run_event
		self.heartbeat = Thread(self.run)

		self.receive = Receive(self.peers_queue, self.receive_run_event, self.worldview_foreign_queue)
		self.broadcast = Broadcast(self.broadcast_run_event, worldview_queue)


	def run(self):
		while self.run_event.isSet():
			current_time = time()
			if not self.peers_queue.empty():
				id, time_stamp = self.peers_queue.get()
				self.peers[id] = time_stamp
				self.peers_queue.task_done()
				if id in self.lost_peers:
					del self.lost_peers[id]
			for id in self.peers:
				if self.peers[id] < current_time - self.heartbeat_timeout:
					self.lost_peers[id] = current_time
					del self.peers[id]
					break

		self.receive_run_event.clear()
		self.broadcast_run_event.clear()

	def get_peers(self):
		self.peers_queue.join()
		peer_statuses = [self.peers, self.lost_peers]
		return peer_statuses

	def get_worldview_foreign(self):
		if not self.worldview_foreign_queue.empty():
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
		sock.bind(('<broadcast>', 20002))
		return sock

	def run(self):
		sock = self.socket_init()
		while(self.run_event.isSet()):
			data, addr = sock.recvfrom(1024)
			worldview_foreign_with_id = json.loads(data)
			id_foreign = next(iter(worldview_foreign_with_id))
			peer_entry = [id_foreign, time()]
			if self.run_event.isSet():
				self.peers_queue.put(peer_entry)
				self.worldview_foreign_queue.put(worldview_foreign_with_id)

class Broadcast:
	def __init__(self, broadcast_run_event, worldview_queue):
		self.run_event = broadcast_run_event
		self.worldview_queue = worldview_queue
		self.broadcast = Thread(self.run)

	def sock_init(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		return sock

	def run(self):
		target_port = 20002
		sock = self.sock_init()
		while self.run_event.isSet():
			sleep(0.2)
			while self.worldview_queue.empty() and self.run_event.isSet():
				sleep(0.01)
			while not self.worldview_queue.empty():
					worldview_with_id = self.worldview_queue.get()
			worldview_with_id = json.dumps(worldview_with_id)
			sock.sendto(worldview_with_id, ('<broadcast>', target_port))
			self.worldview_queue.task_done()
