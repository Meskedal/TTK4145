
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "con_load.h"
#include "driver/elevator_hardware.h"
#include "fsm.h"
#include "timer.h"


int main(void){

    printf("Started!\n");

    int inputPollRate_ms = 25;
    con_load("elevator.con",
        con_val("inputPollRate_ms", &inputPollRate_ms, "%d")
    )

    elevator_hardware_init();

    if(elevator_hardware_get_floor_sensor_signal() == -1){
        fsm_onInitBetweenFloors();
    }

    while(1){
        { // Request button
            static int prev[N_FLOORS][N_BUTTONS];
            for(int f = 0; f < N_FLOORS; f++){
                for(int b = 0; b < N_BUTTONS; b++){
                    int v = elevator_hardware_get_button_signal(b, f);
                    if(v  &&  v != prev[f][b]){
                        fsm_onRequestButtonPress(f, b);
                    }
                    prev[f][b] = v;
                }
            }
        }

        { // Floor sensor
            static int prev;
            int f = elevator_hardware_get_floor_sensor_signal();
            if(f != -1  &&  f != prev){
                fsm_onFloorArrival(f);
            }
            prev = f;
        }


        { // Timer
            if(timer_timedOut()){
                fsm_onDoorTimeout();
                timer_stop();
            }
        }

        usleep(inputPollRate_ms*1000);
    }
}
