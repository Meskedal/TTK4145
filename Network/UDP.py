#!/usr/bin/env python


__author__      = "gitgudd"


import socket

def udp_heartbeat_send(ip, port, message):

	target_ip = ip
	target_port = port	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(message, (target_ip, target_port))

def udp_receive(port,timeout):


	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.settimeout(timeout)
	try:
    	sock.bind(('localhost', port))
	except:
    	print 'failure to bind'
    	sock.close()
    	return

    try:
    	data, addr = sock.recvfrom(1024)


def 


    
