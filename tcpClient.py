#!/usr/bin/env python
import socket
import time

TCP_IP = '192.168.1.1'
TCP_PORT = 2001
GOFORWARD = b'\xff\0\x01\0\xff'
STOP = b'\xff\0\0\0\xff'

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

s.send(GOFORWARD)
time.sleep(5)
s.send(STOP)

s.close()
