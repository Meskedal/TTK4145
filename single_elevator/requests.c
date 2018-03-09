#include "requests.h"

static int requests_above(Elevator e){
    for(int f = e.floor+1; f < N_FLOORS; f++){
        for(int btn = 0; btn < N_BUTTONS; btn++){
            if(e.requests[f][btn]){
                return 1;
            }
        }
    }
    return 0;
}

static int requests_below(Elevator e){
    for(int f = 0; f < e.floor; f++){
        for(int btn = 0; btn < N_BUTTONS; btn++){
            if(e.requests[f][btn]){
                return 1;
            }
        }
    }
    return 0;
}

Dirn requests_chooseDirection(Elevator e){
    switch(e.dirn){
    case D_Up:
        return  requests_above(e) ? D_Up    :
                requests_below(e) ? D_Down  :
                                    D_Stop  ;
    case D_Down:
    case D_Stop: // there should only be one request in this case. Checking up or down first is arbitrary.
        return  requests_below(e) ? D_Down  :
                requests_above(e) ? D_Up    :
                                    D_Stop  ;
    default:
        return D_Stop;
    }
}

int requests_shouldStop(Elevator e){
    switch(e.dirn){
    case D_Down:
        return
            e.requests[e.floor][B_HallDown] ||
            e.requests[e.floor][B_Cab]      ||
            !requests_below(e);
    case D_Up:
        return
            e.requests[e.floor][B_HallUp]   ||
            e.requests[e.floor][B_Cab]      ||
            !requests_above(e);
    case D_Stop:
    default:
        return 1;
    }
}


//Elevator requests_clearAtCurrentFloor(Elevator e){
Elevator requests_clearAtCurrentFloor(Elevator e){
    for(Button btn = 0; btn < N_BUTTONS; btn++){
         e.requests[e.floor][btn] = 0;
    }   
    return e;
}











