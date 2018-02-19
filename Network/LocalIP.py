#!/usr/bin/env python

__author__      = "gitgudd"

import socket

def local_ip():

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	IP = s.getsockname()[0]
	print IP
	s.close()
	return IP
