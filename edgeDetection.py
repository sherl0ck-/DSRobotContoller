import cv2
import numpy as np
from matplotlib import pyplot as plt
from random import randint
from math import sqrt

class LineDetector:

	### Canny detector, invariant to a change in overall image brightness.
	### Requires no pixel boundary params specifications
	def autoCanny(image, sigma=0.33):
		median = np.median(image)
		lower = int(max(0, (1.0-sigma)*median))
		upper = int(min(255, (1.0 + sigma)*median))
		return cv2.Canny(image, lower, upper)

	### Displays a list of lines onto an image using random colors.
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

	### Inputs: edges, usually output from a Canny detector, 
	### 		nLongestLines the caller is trying to identify,
	###			all lineLengthThreshold pixels or larger. 
	### Method: HoughLinesP identifies all such lines,
	###			we dynamically keep track of the longest ones in a set.
	###	Output:	a list of nLongestLines longest lines identified in the image.
	def getLongestLines(edgedImage, nLongestLines, lineLengthThreshold): 
		
		RO_ACCURACY = 3
		THETA_ACCURACY = np.pi/180
		
		# can be increased to detect more lines
		MAX_LINE_GAP = 10
		
		longestLines = {}
		for i in range(nLongestLines):
			arr = [0, 0, 0, 0]
			longestLines[i] = arr

		allLines = cv2.HoughLinesP(edgedImage, RO_ACCURACY, THETA_ACCURACY, 
			threshold=lineLengthThreshold, 
			minLineLength=lineLengthThreshold,
			maxLineGap=MAX_LINE_GAP)

		if allLines is None:
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

		return list(longestLines.values())
				
# For testing
cap=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')

while True:
	ret,frame=cap.read()
	cv2.imshow("frame", frame)
	
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	edgedFrame = LineDetector.autoCanny(gray)
	lines = LineDetector.getLongestLines(edgedFrame, 
		nLongestLines=1, lineLengthThreshold=int((edgedFrame.shape)[0]/3))
	if lines is not None:
		LineDetector.showLines(frame, lines)

	cv2.imshow('Lines', frame)
	cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()