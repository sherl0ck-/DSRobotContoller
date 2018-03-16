#!/usr/bin/env python
import socket
import time

class BasicInteractionsWithFreddie:
	FWD = b'\xff\0\x01\0\xff'
	STP = b'\xff\0\0\0\xff'
	PAN = b'\xff\x01\x07'
	TLT = b'\xff\x01\x08'
	currTLT = 0
	currPAN = 0

	def __init__(self):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
	def connectToFreddie(self):
		TCP_IP = '192.168.1.1'
		TCP_PORT = 2001
		self.s.connect((TCP_IP, TCP_PORT))

	def sendFreddieForward(self, durationSeconds):
		self.s.send(FWD)
		time.sleep(durationSeconds)
		self.s.send(STOP)

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


freddie = BasicInteractionsWithFreddie()
freddie.connectToFreddie()
freddie.resetFreddiesCamera()
freddie.closeConnectionToFreddie()