
#include "elevator_io_device.h"

#include <assert.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netdb.h>
#include <stdio.h>

#include "driver/channels.h"


static int elev_simulation_read_floorSensor(void);
static int elev_simulation_read_requestButton(int floor, Button button);
static int elev_simulation_read_stopButton(void);
static int elev_simulation_read_obstruction(void);

static void elev_simulation_write_floorIndicator(int floor);
static void elev_simulation_write_requestButtonLight(int floor, Button button, int value);
static void elev_simulation_write_doorLight(int value);
static void elev_simulation_write_stopButtonLight(int value);
static void elev_simulation_write_motorDirection(Dirn dirn);

typedef enum {
    ET_Comedi,
    ET_Simulation
} ElevatorType;

static ElevatorType et = ET_Simulation;
static int sockfd;

static void __attribute__((constructor)) elev_init(void){
    int resetSimulator = 0;

    switch(et) {

    case ET_Simulation:
        char* ip = "localhost";
        char* port = "15657";

        sockfd = socket(AF_INET, SOCK_STREAM, 0);
        assert(sockfd != -1 && "Unable to set up socket");

        struct addrinfo hints = {
            .ai_family      = AF_UNSPEC,
            .ai_socktype    = SOCK_STREAM,
            .ai_protocol    = IPPROTO_TCP,
        };
        struct addrinfo* res;
        getaddrinfo(ip, port, &hints, &res);

        int fail = connect(sockfd, res->ai_addr, res->ai_addrlen);
        //assert(fail == 0 && "Unable to connect to simulator server");

        freeaddrinfo(res);

        if(resetSimulator){
            send(sockfd, (char[4]){0}, 4, 0);
        }

        break;
    }

    ElevOutputDevice eo = elevio_getOutputDevice();

    for(int floor = 0; floor < N_FLOORS; floor++) {
        for(Button btn = 0; btn < N_BUTTONS; btn++){
            eo.requestButtonLight(floor, btn, 0);
        }
    }

    eo.stopButtonLight(0);
    eo.doorLight(0);
    eo.floorIndicator(0);
}


ElevInputDevice elevio_getInputDevice(void){
    switch(et) {
    case ET_Simulation:
        return (ElevInputDevice){
            .floorSensor    = &elev_simulation_read_floorSensor,
            .requestButton  = &elev_simulation_read_requestButton,
            .stopButton     = &elev_simulation_read_stopButton,
            .obstruction    = &elev_simulation_read_obstruction
        };
    default:
        return (ElevInputDevice){0};
    }
}


ElevOutputDevice elevio_getOutputDevice(void){
    switch(et) {
    case ET_Simulation:
        return (ElevOutputDevice){
            .floorIndicator     = &elev_simulation_write_floorIndicator,
            .requestButtonLight = &elev_simulation_write_requestButtonLight,
            .doorLight          = &elev_simulation_write_doorLight,
            .stopButtonLight    = &elev_simulation_write_stopButtonLight,
            .motorDirection     = &elev_simulation_write_motorDirection
        };
    default:
        return (ElevOutputDevice){0};
    }
}


char* elevio_dirn_toString(Dirn d){
    return
        d == D_Up    ? "D_Up"         :
        d == D_Down  ? "D_Down"       :
        d == D_Stop  ? "D_Stop"       :
                       "D_UNDEFINED"  ;
}


char* elevio_button_toString(Button b){
    return
        b == B_HallUp       ? "B_HallUp"        :
        b == B_HallDown     ? "B_HallDown"      :
        b == B_Cab          ? "B_Cab"           :
                              "B_UNDEFINED"     ;
}





static const int floorSensorChannels[N_FLOORS] = {
    SENSOR_FLOOR1,
    SENSOR_FLOOR2,
    SENSOR_FLOOR3,
    SENSOR_FLOOR4,
};



static int elev_simulation_read_floorSensor(void){
    send(sockfd, (char[4]){7}, 4, 0);
    unsigned char buf[4];
    recv(sockfd, buf, 4, 0);
    return buf[1] ? buf[2] : -1;
}


static const int buttonChannels[N_FLOORS][N_BUTTONS] = {
    {BUTTON_UP1, BUTTON_DOWN1, BUTTON_COMMAND1},
    {BUTTON_UP2, BUTTON_DOWN2, BUTTON_COMMAND2},
    {BUTTON_UP3, BUTTON_DOWN3, BUTTON_COMMAND3},
    {BUTTON_UP4, BUTTON_DOWN4, BUTTON_COMMAND4},
};

static int elev_simulation_read_requestButton(int floor, Button button){
    send(sockfd, (char[4]){6, button, floor}, 4, 0);
    char buf[4];
    recv(sockfd, buf, 4, 0);
    return buf[1];
}



static int elev_simulation_read_stopButton(void){
    send(sockfd, (char[4]){8}, 4, 0);
    char buf[4];
    recv(sockfd, buf, 4, 0);
    return buf[1];
}



static int elev_simulation_read_obstruction(void){
    send(sockfd, (char[4]){9}, 4, 0);
    char buf[4];
    recv(sockfd, buf, 4, 0);
    return buf[1];
}



static void elev_simulation_write_floorIndicator(int floor){
    send(sockfd, (char[4]){3, floor}, 4, 0);
}


static const int buttonLightChannels[N_FLOORS][N_BUTTONS] = {
    {LIGHT_UP1, LIGHT_DOWN1, LIGHT_COMMAND1},
    {LIGHT_UP2, LIGHT_DOWN2, LIGHT_COMMAND2},
    {LIGHT_UP3, LIGHT_DOWN3, LIGHT_COMMAND3},
    {LIGHT_UP4, LIGHT_DOWN4, LIGHT_COMMAND4},
};


static void elev_simulation_write_requestButtonLight(int floor, Button button, int value){
    send(sockfd, (char[4]){2, button, floor, value}, 4, 0);
}



static void elev_simulation_write_doorLight(int value){
    send(sockfd, (char[4]){4, value}, 4, 0);
}


static void elev_simulation_write_stopButtonLight(int value){
    send(sockfd, (char[4]){5, value}, 4, 0);
}

static void elev_simulation_write_motorDirection(Dirn dirn){
    send(sockfd, (char[4]){1, dirn}, 4, 0);
}
