#!/usr/bin/env python


__author__      = "gitgudd"

from LocalIP import *
import socket, errno, json
from time import sleep, time


def udp_broadcast_heartbeat(port, broadcastEvent, worldview_queue, print_lock):
	while(broadcastEvent.isSet()):
		worldview = udp_send_worldview(worldview_queue, print_lock)
		print_lock.acquire()
		print("worldview aquired")
		print_lock.release()
		worldview = json.dumps(worldview)
		target_ip = '127.0.0.1'
		target_port = port
		sleep(0.5)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(worldview, (target_ip, target_port))
		print_lock.acquire()
		print("sent")
		print_lock.release()

def udp_receive_heartbeat(port, Peers_queue, timeout, receiveEvent, worldview_foreign_queue, print_lock):
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
			worldview_foreign = [data[id_foreign], id_foreign]
			timestamp = time()
			peer_entry = [id_foreign, timestamp]
			if (receiveEvent.isSet()):
				Peers_queue.put(peer_entry)
				worldview_foreign_queue.put(worldview_foreign)
		except socket.timeout as e:
			print_lock.acquire()
			print(e)
			print_lock.release()

def udp_send_worldview(worldview_queue, print_lock):
	while(worldview_queue.empty()):
		pass
	worldview = worldview_queue.get()
	try:
		ip = local_ip()
	except IOError as e:
		print_lock.acquire()
		print(e)
		print_lock.release()
	new_dict = {}
	new_dict[ip] = worldview
	return new_dict
