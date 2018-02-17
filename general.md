#Project
Generally thinking about Peer-to-Peer, Scaleable, Fault tolerant.
Using JSON to transfer/sync databases.
All messages need to be ACK, maybe send synced information back to confirm correct information.
Want the elevators to do orders inside orders indenpendetly. Based on idle, dir and lastFloor, the elevatorswill be assigned based on score.

Elevators only drive in a chosen direction and look for orders in floors passing by based on direction (Will not look for hall orders down when moving up etc.).
This may cause som elevators to fullfill an order thats been assigned to some other elevator in some egde cases. The result of this would be that a elevator would end up at either bottom or top floor.
If an elevator that is assigned an order, doesn't acknowledge this, the order will be assigned to the "next best" elevator. What happens if all elevators lose connection to each other?
Do all hall orders sync over network, or are they linked by hardware?
If a elevator shuts down, is it best to store inside orders in a local file, or store "local" inside orders in cloud of the peer-to-peer network?


#Exercise4 Network Module
1. Do all nodes have to agree before making an order? No, only majority. If else, source of hall order has veto.



General
* Peer-to-peer; Handles sudden disconnects and shutdowns with ease. Scaleable.
* JSON: Standarized message formatting? Using json as binary string and using checksum?
* Sync: Every node has has information of all hall orders, direction and last floor for every elevator. Inside orders are also synced because of shutdown faults(Local file?).
	The sync takes place when new input is registered and needs to be shared. While syncing there will be a acknowledgement of the new information, if a node fails to acknowledge they will be regarded as offline/not available until they respond. (Will not be delegated any orders.)
	For every sync, ALL information is synced to keep lagged nodes up to date.
* Order delegation: Scoresystem based on dir and lastfloor. An order delegation involves setting the elevator in motion in the required dir. Source of order input delegates order based on algorithm.
* Order comlpetion: For every floor passed the elevator checks for orders at the current floor. If the dir matches the order, the elevator executes that order. 
	-Edge case: May result in some elevator fullfilling a request that was meant to be completed by another elevator, This edge case will in the worst case make the elevator reach a end and be idle there. 

Threading
 * Each node has a network module consisting of two threads for receiving and sending. 
 * Thread for elevator operations. 

 Python:
 * Pros:
 	- Python is a high level programming language, easy to use and very widespread support. 
 	- Chosen because we want to achieve a good understanding of one of the most commonly used lanugages.
 * Cons:
 	- Global interpreter lock. (why is this a limiting factor?.)
 	- Hard to share objects between processes. 
 	- Is not as optimized for multithreading as certain languages (eg GO).

Flesh out network module interface, handle packet losses, orders not fullfilled.
Using UDP, how does one acknowledge? acknowledgements involves IP adress so tthey can be differntiated. Broadcasting of information
Draw diagrams to present the flow of network messaging.


Faults:
* Powerloss
	- Case: Powerlosss
	- Solution: The peer-to-peer network will known if a elevator is offline by it not akcnowledgeing new syncs. The result is a new delegation of all orders in global table that is not in any of the remaining local tables. In choosing the delegating elevator, is is choosen by lowest ip or elevator number. 
* Disconnects
	- Case: Disconnect
	- Solution: see Case Powerloss, The disconnected elevator will still execute the orders but will not be able to sync the completion and the other elevators will redundentaly fulfill the same orders to guarantee 		completion. 
	- Sub Case: The elevator that is disconnected sees all the other elevators as disocennted and itself as online. It will then try to fullfill all orders in the global table itself whithout knowing that it is 			actually itself that is disconnected.
	-Solution: Do nothing, let the disconnected elevator fullfill redundently all orders. Alternatively find a way to determine if elevator is disconnected or if all others are disconnected. 
* Returning offline elevators
	- Case: A elevator that has been disconnected for a period of time while fullfilling orders needs to sync this information but the order has also been fullfilled by the online elevators and they have received a new order on the same floor. Who has the right information?
	- Solution:	Timestamps resolves uniqueness of orders. 
	- Sub case: Timestamps solves the uniqueness of orders, but when is it safe to remove a order from the global order table?.
	- Solution: The disconnected elevator knows it is disconnected. Conflicts in global table is resolved by newest timestamp. 


* Be wary of dataraces 
* Orders not fullfiled
	-Case: Elevator receives order but goes offline before execution. 
	-Solution: Redundacy in form of timestaping orders and reasonable expected execution time not fullfilled. 

Case:
	All elevators are going in one direction, and recives order in opposite direction, how to receive this order?
	soloution: Cant assign order in opposite direction until idle. 





Ordertables needed:
- 1 universal order table. This is based on that everyone has information of everything in case of disconnects.
- 1 node based order table. This is the orders that a node is expected to fullfill. Is this needed for everyone? The orders exist in the global table also untill fulfilled so in case of a disconnect the order would 		still exist in the golbal table and could just be delegated again with regards to disconnect elevators.

Network Module:
- Heartbeat
	- Every node snedsout their 
- JSON messages
- Broadcast
- Listen