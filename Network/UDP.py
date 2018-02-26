#!/usr/bin/env python


__author__      = "gitgudd"

from LocalIP import *
import socket, errno
from time import sleep, time


def udp_broadcast_heartbeat(port, broadcastEvent, print_lock):
	while(broadcastEvent.isSet()):
		try:
			ip = local_ip()
		except IOError as e:
			print_lock.acquire()
			print(e)
			print_lock.release()
		target_ip = '127.0.0.1'
		target_port = port
		sleep(0.5)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(ip, (target_ip, target_port))

def udp_receive_heartbeat(port,queue,timeout, receiveEvent, print_lock):
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
			print_lock.acquire()
			print(addr)
			print_lock.release()
			entry = [data, time()]
			if (receiveEvent.isSet()):
				queue.put(entry)
		except socket.timeout as e:
			print_lock.acquire()
			print(e)
			print_lock.release()
