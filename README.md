# DSRobotContoller

Embedded Systems Spring 2018 final project, NYUAD

Usage:

```bash
$ git clone git@github.com:sherl0ck-/DSRobotContoller.git
$ cd DSRobotController/c++
$ mkdir bin; make
$ python ../balltracking.py -p PROBLEM | bin/main 192.168.1.1 2001 [trajectory] 
# PROBLEM must be atob or trajectory
	# atob follows the ball to a point or a leader when the ball is put on it
	# trajectory follows a trajectory
```

