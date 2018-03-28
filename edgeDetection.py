import cv2
import numpy as np
from matplotlib import pyplot as plt
import glob
from random import randint
from math import sqrt

def auto_canny(image, sigma=0.33):
	median = np.median(image)
	lower = int(max(0, (1.0-sigma)*median))
	upper = int(min(255, (1.0 + sigma)*median))
	return cv2.Canny(image, lower, upper)

def showLines(img, lines):
	randColor=[0, 0, 0]
	for l in lines:
		for i in range (3):
			randColor[i] = randint(0, 255)

		x1 = l[0]
		y1 = l[1]
		x2 = l[2]
		y2 = l[3]
		cv2.line(img,(x1,y1),(x2,y2),tuple(randColor),3)

def houghLines(img, edged_frame):
	h = (img.shape)[0]
	w = (img.shape)[1]
	LINE_LENGTH_THRESHOLD = int(h/3)
	RO_ACCURACY = 3
	THETA_ACCURACY = np.pi/180
	# can be increased to detect more lines
	MAX_LINE_GAP = 10
	N_LONGEST_LINES = 2

	longestLines = {}
	for i in range(N_LONGEST_LINES):
		arr = [0, 0, 0, 0]
		longestLines[i] = arr

	#edged_frame = edged_frame/255
	allLines = cv2.HoughLinesP(edged_frame, RO_ACCURACY, THETA_ACCURACY, 
		threshold=LINE_LENGTH_THRESHOLD, 
		minLineLength=LINE_LENGTH_THRESHOLD,
		maxLineGap=MAX_LINE_GAP)

	if allLines is None:
		print('No lines')
		return

	for l in allLines:
		for line in l:
			x1 = line[0]
			y1 = line[1]
			x2 = line[2]
			y2 = line[3]
			lineLength = sqrt((y2-y1)**2 + (x2-x1)**2)

			sortedLengths = sorted(longestLines.keys())

			if (lineLength>sortedLengths[0]):
				# It could happen that this length is already present
				if lineLength in longestLines:
					lineLength += 0.00001*randint(1,10)

				del longestLines[sortedLengths[0]]
				longestLines[lineLength] = list([x1,y1,x2,y2])

	showLines(img, list(longestLines.values()))
				
cap=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')

while True:
	ret,frame=cap.read()
	cv2.imshow("test-h264", frame)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	edged_frame = auto_canny(gray)
	houghLines(frame, edged_frame)
	cv2.imshow('Lines', frame)
	cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()

#img = cv2.imread('tstPics/tst.jpg')
#cv2.imshow('original', img)
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#edged_frame = auto_canny(gray)
#houghLines(img, edged_frame)
#cv2.imshow('Lines', img)

#cv2.waitKey(0)