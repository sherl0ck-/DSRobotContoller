from collections import deque   
import numpy as np
import argparse
import imutils
import cv2
from sys import stdout, stderr
import os

problems = ['atob', 'leader', 'trajectory']
def isStopConditionMet(relevantParam, problem):
	if problem in problems:
		if problem == 'atob' or problem=='trajectory':
			return relevantParam > 380
		elif problem == 'leader':
			return relevantParam > IN_FRONT_OF_US

def getBallDirection(lab, colorRange):
	colorLower, colorUpper = colorRange
	# construct a mask for the color, then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(lab, colorLower, colorUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		if radius > MIN_BALL_RADIUS:
			# draw the circle and centroid on the frame,
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)

			if problem == 'leader':
				relevantParam = int(radius)
			elif problem == 'atob' or problem=='trajectory':
				relevantParam = int(y)

			else:
				relevantParam = None

			radius = int(radius)
			print(-halfFrameWidth, radius) if isStopConditionMet(relevantParam, problem) \
				else print(int(x)-halfFrameWidth, radius)

			stdout.flush()

		else:
			print(halfFrameWidth, 0)
			stdout.flush()

	else:
		print(halfFrameWidth, 0)
		stdout.flush()

redLower = (0, 96, 31)
redUpper = (6, 255, 255)

blueLower = (90, 90, 0)
blueUpper = (143, 183, 255)

yellowLower = (25, 73, 104)
yellowUpper = (62, 255, 255)

yellowHouseLowerLab = (0, 98, 149)
yellowHouseUpperLab = (255, 126, 178)
yellowHouse = [yellowHouseLowerLab, yellowHouseUpperLab]

yellowTennis = [(0, 107, 150), (255, 126, 170)]

yellowBalloon = [(0, 104, 156), (255, 117, 185)]
redBalloon = [(0, 160, 137), (255, 186, 174)]
orangeBalloon = [(0, 147, 145), (255, 171, 184)]
blueBalloon = [(0, 91, 68), (255, 170, 118)]
pinkBalloon = [(0, 165, 126), (255, 184, 146)]

colorsToFollow = [yellowBalloon, redBalloon, blueBalloon]#, blueBalloon, pinkBalloon]
FIFO = 'mypipe'
os.mkfifo(FIFO, 0o777)

nFrames = 0
camera=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
(grabbed, frame) = camera.read()
halfFrameWidth = int(frame.shape[1]/2)
halfFrameHeight = int(frame.shape[0]/2)
MIN_BALL_RADIUS = 10
IN_FRONT_OF_US=0.75*halfFrameHeight
problem = 'trajectory'

print(int(halfFrameWidth)) # For protocol purpose
stdout.flush()
colorIdx = 0
while True:
	# grab the current frame
	(grabbed, frame) = camera.read()
	nFrames+=1
	if nFrames%5==0:
	    continue

	if not grabbed:
		break

	#hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
	try:
		p = os.open(FIFO, os.O_RDONLY | os.O_NONBLOCK)
		input = os.read(p, 2)
	except:
		pass

	if input:
		colorIdx+=1

	getBallDirection(lab, colorsToFollow[colorIdx])
	os.close(p)
	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		print(-halfFrameWidth, 0)
		stdout.flush()
		break

os.unlink(FIFO)
# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
