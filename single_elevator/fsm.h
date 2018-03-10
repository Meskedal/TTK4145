#pragma once

#include "elevator_io_types.h"

void fsm_onInitBetweenFloors(void);
void fsm_onRequestButtonPress(int btn_floor, Button btn_type);
int fsm_onFloorArrival(int newFloor);
void fsm_onDoorTimeout(void);

int fsm_get_e_floor(void);
int fsm_get_e_dirn(void);
int fsm_get_e_behaviour(void);
int fsm_get_e_request(int floor, int btn);
int fsm_set_e_request(int value, int floor, int btn);
