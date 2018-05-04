import argparse
import imutils
import cv2
from sys import stdout
import os

problems = ['atob', 'leader', 'trajectory']
def isStopConditionMet(relevantParam, problem):
	if problem in problems:
		if problem == 'atob' or problem=='trajectory':
			return relevantParam > 380
		elif problem == 'leader':
			return relevantParam > IN_FRONT_OF_US

def getArgs():
	ap = argparse.ArgumentParser()
	ap.add_argument('-p', '--problem', required=True,
					help='Problem - atob, trajectory, or leader')
	
	args = vars(ap.parse_args())

	if not args['problem'].lower() in ['atob', 'leader', 'trajectory']:
		ap.error("Please specify a correct problem.")

	return args


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

			radius = int(radius)
			if isStopConditionMet(relevantParam, problem):
				return -halfFrameWidth, radius

			return int(x)-halfFrameWidth, radius

		return halfFrameWidth, 0
			
	return halfFrameWidth, 0


yellowTennis = [(0, 107, 150), (255, 126, 170)]

yellowBalloon = [(0, 104, 156), (255, 117, 185)]
redBalloon = [(0, 160, 137), (255, 186, 174)]
orangeBalloon = [(0, 147, 145), (255, 171, 184)]
blueBalloon = [(0, 91, 68), (255, 170, 118)]
pinkBalloon = [(0, 165, 126), (255, 184, 146)]

FIFO = 'mypipe'
os.mkfifo(FIFO, 0o777)

nFrames = 0
camera=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
(grabbed, frame) = camera.read()
halfFrameWidth = int(frame.shape[1]/2)
MIN_BALL_RADIUS = 10
IN_FRONT_OF_US=int(3*frame.shape[0]/8) # 3/4 of half the height.
problem = getArgs()['problem'].lower()

if problem == 'trajectory':
	colorsToFollow = [blueBalloon, redBalloon, orangeBalloon, yellowBalloon, pinkBalloon]
else:
	colorsToFollow = [yellowHouse]

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

	lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
	try:
		p = os.open(FIFO, os.O_RDONLY | os.O_NONBLOCK)
		input = os.read(p, 2)
	except:
		pass

	# Time to switch to tracking the next ball
	if input:
		colorIdx+=1

	direction, radius = getBallDirection(lab, colorsToFollow[colorIdx])
	print(direction, radius)
	stdout.flush()

	os.close(p)

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		print(-halfFrameWidth, 0)
		stdout.flush()
		break

os.unlink(FIFO)
camera.release()
cv2.destroyAllWindows()
