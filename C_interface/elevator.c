
#include "elevator.h"

#include <stdio.h>

#include "timer.h"

char* eb_toString(ElevatorBehaviour eb){
    return
        eb == EB_Idle       ? "EB_Idle"         :
        eb == EB_DoorOpen   ? "EB_DoorOpen"     :
        eb == EB_Moving     ? "EB_Moving"       :
                              "EB_UNDEFINED"    ;
}

Elevator elevator_uninitialized(void){
    return (Elevator){
        .floor = -1,
        .dirn = D_Stop,
        .behaviour = EB_Idle,
        .config = {
            .clearRequestVariant = CV_All,
            .doorOpenDuration_s = 3.0,
        },
    };
}
