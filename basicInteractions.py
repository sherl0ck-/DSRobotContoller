#!/usr/bin/env python
import socket
import time

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

	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
	def connectToFreddie(self):
		TCP_IP = '192.168.1.1'
		TCP_PORT = 2001
		self.s.connect((TCP_IP, TCP_PORT))
		self.resetFreddiesCamera()

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

# Testing the implementations
freddie = BasicInteractionsWithFreddie()
freddie.connectToFreddie()
freddie.tiltFreddiesCameraAbs(0)
freddie.panFreddiesCameraAbs(50)
freddie.closeConnectionToFreddie()