__author__      = "gitgudd"


from order_assignment import *
import argparse as ap
import getpass as gp

class Worldview_handler:
    def __init__(self, local_orders_queue, worldview_queue):
        self.id = None
        self.config_init()
        self.worldview = worldview = {}
    	self.worldview['hall_orders'] = [[[0,0] for x in range(0,N_BUTTONS-1)] for y in range(0,N_FLOORS)]
    	self.worldview['elevators'] = {}
        self.peers = None
        self.lost_peers = None
        self.alone = False
        self.local_orders_queue = local_orders_queue
        self.worldview_to_broadcast_queue = worldview_queue

    def local_hardware_failure(self):
        return self.worldview['elevators'][self.id]['hardware_failure']

    def redundancy_check(self):
        if len(self.peers) < 2:
            for f in range (0, N_FLOORS):
                    for b in range (0, N_BUTTONS-1):
                        self.worldview['elevators'][self.id]['requests'][f][b] = 0
                        self.worldview['hall_orders'][f][b] =[0,0]

    def worldview_update_elevator(self, elevator):
        self.worldview['elevators'][self.id] = elevator
        self.redundancy_check()

    def update_peers(self, peers, lost_peers):
        self.peers = peers
        self.lost_peers = lost_peers
        self.delete_lost_peers()

    def pass_local_worldview(self):
        if len(self.peers) >= 2:
            local_orders = self.worldview['elevators'][self.id]['requests']
            self.local_orders_queue.put(local_orders)

    def pass_worldview_with_id(self):
        worldview_with_id = {}
        worldview_with_id[self.id] = self.worldview
        self.worldview_to_broadcast_queue.put(worldview_with_id)

    def delete_lost_peers(self):
    	for id in self.worldview['elevators']:
    		if id in self.lost_peers:
    			del self.worldview['elevators'][id]
    			break

    def assign_orders(self):
        if len(self.peers) >= 2:
            assigner_thingy = Assigner(self.worldview, self.id, self.peers) #local requests goes from 0 to 1 after assigner
            self.worldview = assigner_thingy.should_i_take_order()

    def sync_worldviews(self, worldview_foreign_with_id):
        id_foreign = next(iter(worldview_foreign_with_id))
        worldview_foreign = worldview_foreign_with_id[id_foreign]

        self.worldview['elevators'][id_foreign] = worldview_foreign['elevators'][id_foreign]
    	hall_orders = self.worldview['hall_orders']
    	hall_orders_foreign = worldview_foreign['hall_orders']
    	for f in range (0, N_FLOORS):
    		for b in range (0, N_BUTTONS-1):
    			if hall_orders[f][b][1] < hall_orders_foreign[f][b][1]:
    				hall_orders[f][b][0] = hall_orders_foreign[f][b][0]
    				hall_orders[f][b][1] = hall_orders_foreign[f][b][1]

    	self.worldview['hall_orders'] = hall_orders

    def update_order(self, order):
        floor, button, button_status = order
        self.worldview['hall_orders'][floor][button] = [button_status, time()]
        if button_status == 0:
            self.worldview['elevators'][self.id]['requests'][floor][button] = 0

    def config_init(self):
        parser = ap.ArgumentParser(description='Port for simulation')
    	parser.add_argument('-p', '--port', dest='sim_port', required=False, metavar='<port_number>')
    	parser.add_argument('-i', '--id', dest='id', required=True, metavar='<elev_id')
    	args = parser.parse_args()
    	port_number = args.sim_port #Sender's email address
    	self.id = args.id
    	if port_number:
    		with open('C_interface/elevator_hardware.con', 'r') as file:
    			print(port_number)
    			data = file.readlines()

    # now change the 2nd line, note that you have to add a newline
    		data[3] = "--com_port              " + port_number

    		# and write everything back
    		with open('C_interface/elevator_hardware.con', 'w') as file:
    		    file.writelines(data)
    		#subprocess.call(['cd', 'elevatorHW'])
    		#subprocess.call(['./' , 'SimElevatorServer'])
    	else:
    		with open('C_interface/elevator_hardware.con', 'r') as file:
    			print(port_number)
    			data = file.readlines()

    # now change the 2nd line, note that you have to add a newline
    		data[3] = "--com_port              " + '15657'

    		# and write everything back
    		with open('C_interface/elevator_hardware.con', 'w') as file:
    		    file.writelines(data)
