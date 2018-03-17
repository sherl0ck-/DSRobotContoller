#!/usr/bin/env python
from socket import *
import time
import threading

def main():
#   connect to Freddie
    freddie = socket(AF_INET, SOCK_STREAM)
    freddie.connect(('192.168.1.1', 2001))

#   start the command thread
    ct = CommandThread()
    ct.start()


class CommandThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.freddie = BasicInteractionsWithFreddie()
        self.freddie.connectToFreddie()

    def run(self):
        # send some command
        while(True):
            self.freddie.sendFreddieForward(0.25)
            self.freddie.sendFreddieBackward(0.25)
            time.sleep(2)



class BasicInteractionsWithFreddie:
	# Forward, backward, left, right, stop commands
	FWD = b'\xff\0\x01\0\xff'
	BCK = b'\xff\0\x02\0\xff'
	LFT = b'\xff\0\x03\0\xff'
	RHT = b'\xff\0\x04\0\xff'
	STP = b'\xff\0\0\0\xff'

	# Set left and right motor speed prefix
	LMS = b'\xff\x02\x01'
	RMS = b'\xff\x02\x02'

	# Camera pan and tilt command prefix
	PAN = b'\xff\x01\x07'
	TLT = b'\xff\x01\x08'

	# For incremental camera changes
	currTLT = 0
	currPAN = 0

	currLMS = 100
	currRMS = 100

	def __init__(self):
		self.s = socket(AF_INET, SOCK_STREAM)

	def connectToFreddie(self):
		TCP_IP = '192.168.1.1'
		TCP_PORT = 2001
		print(self.s.connect((TCP_IP, TCP_PORT)))

	def setFreddiesLeftMotorSpeed(self, lms):
		self.s.send(self.LMS + bytes([lms]) + b'\xff')

	def setFreddiesRightMotorSpeed(self, rms):
		self.s.send(self.RMS + bytes([rms]) + b'\xff')

	def sendFreddieForward(self, durationSeconds):
		self.s.send(self.FWD)
		time.sleep(durationSeconds)
		self.s.send(self.STP)

	def sendFreddieBackward(self, durationSeconds):
		self.s.send(self.BCK)
		time.sleep(durationSeconds)
		self.s.send(self.STP)

	def turnFreddieLeft(self):
		self.s.send(self.LFT)
		time.sleep(0.5)
		self.s.send(self.STP)

	def turnFreddieRight (self):
		self.s.send(self.RHT)
		time.sleep(0.5)
		self.s.send(self.STP)

	def panFreddiesCameraAbs(self, deg):
		self.currPAN = deg
		instruction = self.PAN + bytes([self.currPAN]) + b'\xff'
		self.s.send(instruction)

	def panFreddiesCameraRel(self, deg):
		self.panFreddiesCameraAbs(self.currPAN + deg)

	def tiltFreddiesCameraAbs(self, deg):
		self.currTLT = deg
		instruction = self.TLT + bytes([self.currTLT]) + b'\xff'
		self.s.send(instruction)

	def tiltFreddiesCameraRel(self, deg):
		self.tiltFreddiesCameraAbs(self.currTLT + deg)

	def resetFreddiesCamera(self):
		self.tiltFreddiesCameraAbs(0)
		time.sleep(0.1)
		self.panFreddiesCameraAbs(90)

	def closeConnectionToFreddie(self):
		self.s.close()

if __name__ == "__main__":
    main()
