#!/usr/bin/env python


__author__      = "gitgudd"

from local_ip import *
import socket, errno, json
from time import sleep, time


def udp_broadcast_heartbeat(broadcastEvent, worldview_queue, print_lock):#Broadcasts the JSON formatted worldview of the local id.
	target_ip = '127.0.0.1'
	target_port = 20002
	while(broadcastEvent.isSet()):
		worldview = udp_create_worldview(worldview_queue, print_lock)
		
		print_lock.acquire()
		print("worldview aquired")
		print_lock.release()
		
		worldview = json.dumps(worldview)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(worldview, (target_ip, target_port))
		
		print_lock.acquire()
		print("sent")
		print_lock.release()

def udp_receive_heartbeat(port, peers_queue, timeout, receiveEvent, worldview_foreign_queue, print_lock): #Receives worldview from id and passes id with timestamp to peers_queue.
													  #id:worldview is also passed to worldview_foreign_queue
	while(receiveEvent.isSet()):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.settimeout(timeout)
		
		try:
			sock.bind(('127.0.0.1', port))
		except:
			print 'failure to bind'
			sock.close()

		try:
			data, addr = sock.recvfrom(1024)
			data = json.loads(data)
			id_foreign = next(iter(data))
			worldview_foreign_dict = {}
			worldview_foreign_dict[id_foreign] = data
			timestamp = time()
			peer_entry = [id_foreign, timestamp]
			if (receiveEvent.isSet()):
				peers_queue.put(peer_entry)
				worldview_foreign_queue.put(worldview_foreign_dict)
		except socket.timeout as e:
			print_lock.acquire()
			print(e)
			print_lock.release()

def udp_create_worldview(worldview_queue, print_lock): #Creates worldview dictionary with ip as key
	while(worldview_queue.empty()):
		pass
	worldview = worldview_queue.get()
	try:
		ip = local_ip()
	except IOError as e:
		print_lock.acquire()
		print(e)
		print_lock.release()
	worldview_dict = {}
	worldview_dict[ip] = worldview
	return worldview_dict
