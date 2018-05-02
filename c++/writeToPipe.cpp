#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

int main(){
	char FIFO[] = "../mypipe";
	int fd;
	while (1) {
		fd = open(FIFO, O_WRONLY);
		write(fd, "1", 1);
		close(fd);
	}
	return 0;
}
