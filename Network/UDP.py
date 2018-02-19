#!/usr/bin/env python


__author__      = "gitgudd"


import socket

def udp_broadcast_heartbeat(port):

	target_ip = '127.0.0.1'
	target_port = port
	message = 'hei'
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(message, (target_ip, target_port))

def udp_receive_heartbeat(port,queue,timeout):

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	sock.settimeout(timeout)
	try:
    	sock.bind(('127.0.0.1', port))
	except:
    	print 'failure to bind'
    	sock.close()
    	return

    try:
    	data, addr = sock.recvfrom(1024)
    except timeout as e:
    	print e
    	return False

    queue.put(addr)

    return True
