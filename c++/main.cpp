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
        setSpeed(2);
    }

    ~Car() { 
        shutdown(socketfd, SHUT_RDWR);
    }

    void move(char dir) {
        int time = 150000;
        send(socketfd, command[dir], PAY_LOAD_N, MSG_NOSIGNAL); 
        usleep(time);
        stop();
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
    Car Freddie = Car(argv);
    fprintf(stderr, "Connected to Freddie.\nReady to receive command.....\n");
    int degree;
    while(std::cin >> degree) {
        std::cout << degree << std::endl;
        if (degree > 20) {
            Freddie.move(MOV_RIGHT);
        } else if (degree < -20) {
            Freddie.move(MOV_LEFT);
        }
        Freddie.move(MOV_FWD);
    }
    return 0;
}
