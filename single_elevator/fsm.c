
#include "fsm.h"

#include <stdio.h>

#include "con_load.h"
#include "elevator.h"
//#include "elevator_io_device.h"
#include "driver/elevator_hardware.h"
#include "requests.h"
#include "timer.h"

static Elevator             elevator;
static ElevOutputDevice     outputDevice;


static void __attribute__((constructor)) fsm_init(){
    elevator = elevator_uninitialized();
    
    con_load("elevator.con",
        con_val("doorOpenDuration_s", &elevator.config.doorOpenDuration_s, "%lf")
        con_enum("clearRequestVariant", &elevator.config.clearRequestVariant,
            con_match(CV_All)
            con_match(CV_InDirn)
        )
    )
    
    //outputDevice = elevio_getOutputDevice();
}

static void setAllLights(Elevator es){
    for(int floor = 0; floor < N_FLOORS; floor++){
        for(int btn = 0; btn < N_BUTTONS; btn++){
            elevator_hardware_set_button_lamp(btn, floor, es.requests[floor][btn]);
        }
    }
}

void fsm_onInitBetweenFloors(void){
    elevator_hardware_set_motor_direction(D_Down);
    elevator.dirn = D_Down;
    elevator.behaviour = EB_Moving;
}

int get_a(){
    return 3;
}


void fsm_onRequestButtonPress(int btn_floor, Button btn_type){
    //printf("\n\n%s(%d, %s)\n", __FUNCTION__, btn_floor, elevio_button_toString(btn_type));
    //elevator_print(elevator);
    
    switch(elevator.behaviour){
        
    case EB_DoorOpen:
        if(elevator.floor == btn_floor){
            timer_start(elevator.config.doorOpenDuration_s);
        } else {
            elevator.requests[btn_floor][btn_type] = 1;
        }
        break;

    case EB_Moving:
        elevator.requests[btn_floor][btn_type] = 1;
        break;
        
    case EB_Idle:
        if(elevator.floor == btn_floor){
            elevator_hardware_set_door_open_lamp(1);
            timer_start(elevator.config.doorOpenDuration_s);
            elevator.behaviour = EB_DoorOpen;
        } else {
            elevator.requests[btn_floor][btn_type] = 1;
            elevator.dirn = requests_chooseDirection(elevator);
            elevator_hardware_set_motor_direction(elevator.dirn);
            elevator.behaviour = EB_Moving;
        }
        break;
        
    }
    
    setAllLights(elevator);
    
    //printf("\nNew state:\n");
    //elevator_print(elevator);
}




void fsm_onFloorArrival(int newFloor){
    //printf("\n\n%s(%d)\n", __FUNCTION__, newFloor);
    //elevator_print(elevator);
    
    elevator.floor = newFloor;
    
    elevator_hardware_set_floor_indicator(elevator.floor);
    
    switch(elevator.behaviour){
    case EB_Moving:
        if(requests_shouldStop(elevator)){
            elevator_hardware_set_motor_direction(D_Stop);
            elevator_hardware_set_door_open_lamp(1);
            elevator = requests_clearAtCurrentFloor(elevator, 0);
            timer_start(elevator.config.doorOpenDuration_s);
            setAllLights(elevator);
            elevator.behaviour = EB_DoorOpen;
        }
        break;
    default:
        break;
    }
    
    //printf("\nNew state:\n");
    //elevator_print(elevator); 
}




void fsm_onDoorTimeout(void){
    //printf("\n\n%s()\n", __FUNCTION__);
    //elevator_print(elevator);
    
    switch(elevator.behaviour){
    case EB_DoorOpen:
        elevator.dirn = requests_chooseDirection(elevator);
        
        elevator_hardware_set_door_open_lamp(0);
        elevator_hardware_set_motor_direction(elevator.dirn);
        
        if(elevator.dirn == D_Stop){
            elevator.behaviour = EB_Idle;
        } else {
            elevator.behaviour = EB_Moving;
        }
        
        break;
    default:
        break;
    }
    
    //printf("\nNew state:\n");
    //elevator_print(elevator);
}

int fsm_get_e_floor(void){
    return elevator.floor;
}

int fsm_get_e_dirn(void){
    return elevator.dirn;
}

int fsm_get_e_behaviour(void){
    return elevator.behaviour;
}

int* fsm_get_e_behaviour(void){
    return elevator.requests;
}






