#!/usr/bin/env python


__author__      = "gitgudd"

from LocalIP import *
import socket, errno
from time import sleep


def udp_broadcast_heartbeat(port, broadcastEvent):
	while(broadcastEvent.isSet()):
		try:
			ip = local_ip()
		except IOError as e:
			print e
		target_ip = '127.0.0.1'
		target_port = port
		sleep(0.5)
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(ip, (target_ip, target_port))
	print("exited broadcast")

def udp_receive_heartbeat(port,queue,timeout, receiveEvent):
	while(receiveEvent.isSet()):

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		sock.settimeout(timeout)
		try:
			sock.bind(('127.0.0.1', port))
		except:
			print 'failure to bind'
			sock.close()

		try:
			#print("ready")
			data, addr = sock.recvfrom(1024)
			#print("got")
			if (receiveEvent.isSet()):
				queue.put(data)
			#print("put data in queue")
		except socket.timeout as e:
			print e


	print("exited receive")
