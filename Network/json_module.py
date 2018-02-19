#!/usr/bin/env python


__author__      = "gitgudd"

import json
import numpy

def array_to_json(A):
	return json.dumps(A)

def worldview_to_json(orders, states):

	worldview = {
	"orders": orders,
	"states": states,
	}
	return json.dumps(worldview)

def json_to_worldview(str):
	return

def main():
	A = [[0 for i in range(3)] for j in range(3)]
	B = [[0 for i in range(3)] for j in range(3)]	
	A[1][1] = 1
	B[1][1] = 2
	result = array_to_json(A)
	worldview = worldview_to_json(A,B)
	worldview_parsed = json.loads(worldview)
	print worldview_parsed["states"][1]
	return

main()

