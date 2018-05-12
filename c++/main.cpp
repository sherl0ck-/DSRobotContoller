#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <cmath>
#include <fcntl.h>

// first and last byte of payload
#define START_COND '\xFF'
#define STOP_COND  '\xFF'

// second byte for motion commands
#define MOV        '\x00'

//third byte for motion command
#define MOV_STOP   0
#define MOV_FWD    1
#define MOV_BWD    2
#define MOV_LEFT   3
#define MOV_RIGHT  4
#define CAM_PAN    5
#define CAM_TILT   6
#define SPD_LEFT   7
#define SPD_RIGHT  8

#define SET_DEGREE 3
#define PAY_LOAD_N 5

#define FULL_SPEED 100
#define SEARCH_SPEED 10
#define CRUISE_SPEED 0
#define INC_SPEED 10

#define CONCESSION 0.6

class Car {
    private:
        int socketfd;
        struct sockaddr_in address;
        char command[9][PAY_LOAD_N]  = {
            /* 0 through 4 are motion commands */
            {'\xFF', '\x00', '\x00', '\x00', '\xFF'}, // stop
            {'\xFF', '\x00', '\x01', '\x00', '\xFF'}, // forward
            {'\xFF', '\x00', '\x02', '\x00', '\xFF'}, // backward
            {'\xFF', '\x00', '\x03', '\x00', '\xFF'}, // left
            {'\xFF', '\x00', '\x04', '\x00', '\xFF'}, // right
            /* 5-6 for camera command */
            {'\xFF', '\x01', '\x07', '\x00', '\xFF'}, // left-right
            {'\xFF', '\x01', '\x07', '\x00', '\xFF'}, // up-down
            /* 7-8 are for speed control */
            {'\xFF', '\x02', '\x01', '\x00', '\xFF'}, // left wheels
            {'\xFF', '\x02', '\x02', '\x00', '\xFF'}  // right wheels
        };

    public:
    Car(char** argv) {
        // create a socket for the car
        socketfd = socket(AF_INET, SOCK_STREAM, 0);
        if (socketfd < 0) exit(-1);
        
        // fill in address of the car
        memset(&address, 0, sizeof(struct sockaddr_in));
        address.sin_family = AF_INET;
        address.sin_port = htons(atoi(argv[2]));
        address.sin_addr.s_addr = inet_addr(argv[1]);

        // connect to the car
        if (connect(socketfd, (struct sockaddr *) &address, sizeof(address)) < 0)
            exit(-1);
        setSpeed(SEARCH_SPEED);
    }

    ~Car() { 
        shutdown(socketfd, SHUT_RDWR);
    }

    void move(char dir) {
        send(socketfd, command[dir], PAY_LOAD_N, MSG_NOSIGNAL); 
    }

    void stop() {
        send(socketfd, command[MOV_STOP], PAY_LOAD_N, MSG_NOSIGNAL);
    }

    void setSpeed(char x) {
        setRightSpeed(x);
        setLeftSpeed(x);
    }

    void setRightSpeed(char x) {
        command[SPD_RIGHT][SET_DEGREE] = x;
        send(socketfd, command[SPD_RIGHT], PAY_LOAD_N, MSG_NOSIGNAL);
    }

    void setLeftSpeed(char x) {
        command[SPD_LEFT][SET_DEGREE] = x;
        send(socketfd, command[SPD_LEFT], PAY_LOAD_N, MSG_NOSIGNAL);
    }
};

int main(int argc, char **argv) {
    // setup
    Car Freddie = Car(argv);
    char FIFO[] = "./mypipe";
    int fd = open(FIFO, O_WRONLY);
    bool following_trajectory = true;
 
    // variables initialization
    int halfFrameWidth; std::cin >> halfFrameWidth;
    int concession = CONCESSION * halfFrameWidth;
    int degree = halfFrameWidth, radius = halfFrameWidth;

    // flags to keep track of motion
    bool moving_left = false, moving_right = false;
    bool seen = false;  // track if the ball was seen recently
    int counter = 0;    // ball count for trajectory following

    // main loop
    while(std::cin >> degree >> radius) {
        if (degree == halfFrameWidth) { // can't find anything in the frame
            if (seen == true) write(fd, "1", ++counter);
            seen = false; 
            Freddie.setSpeed(SEARCH_SPEED);

            // task-specific turning for search
            if (following_trajectory) {
                (counter == 0 || counter == 1 || counter == 4) \
                    ? Freddie.move(MOV_RIGHT) : Freddie.move(MOV_LEFT);
            } else {
                moving_left ? Freddie.move(MOV_LEFT) : Freddie.move(MOV_RIGHT);
            }
        } else {    // found a ball in the frame
            seen = true;
            if (degree == -1 * halfFrameWidth) { // close enough, stop
                Freddie.stop();
                moving_left = moving_right = false;
            } else {    // not close enough, make a decision for motion
                int cruise_speed = (radius < 100) ? CRUISE_SPEED : SEARCH_SPEED;
                int inc = (abs(degree) * (FULL_SPEED-cruise_speed)) / halfFrameWidth;
                if (degree < 0) {   // ball is in the left of the frame
                    moving_left = true, moving_right = false;
                    inc = (degree + concession > 0) ? 0 : inc;
                    Freddie.setRightSpeed(cruise_speed + inc);
                    Freddie.setLeftSpeed(cruise_speed);
                } else {              // ball is in the right of the frame
                    moving_right = true, moving_left = false;
                    inc = (degree - concession < 0) ? 0 : inc;
                    Freddie.setRightSpeed(cruise_speed);
                    Freddie.setLeftSpeed(cruise_speed + inc);
                }
                Freddie.move(MOV_FWD);
            }
        }
    }
    Freddie.stop();
    return 0;
}
