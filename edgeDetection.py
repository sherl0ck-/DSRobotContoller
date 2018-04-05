import cv2
import numpy as np
from matplotlib import pyplot as plt
from random import randint
from math import sqrt, atan2, pi
from sys import stdout
from time import sleep

class LineDetector:

	"""" Canny detector, invariant to a change in overall image brightness.
		Requires no pixel boundary params specifications """
	def autoCanny(image, sigma=0.33):
		median = np.median(image)
		lower = int(max(0, (1.0-sigma)*median))
		upper = int(min(255, (1.0 + sigma)*median))
		return cv2.Canny(image, lower, upper)

	### Display a list of lines onto an image using random colors.
	def showLines(img, lines):
		randColor=[0, 0, 0]
		for l in lines:
			for i in range (3):
				randColor[i] = randint(0, 255)

			x1, y1, x2, y2 = l
			cv2.line(img,(x1,y1),(x2,y2),tuple(randColor),3)

	""" 
		Inputs: edges, usually output from a Canny detector, 
	 	nLongestLines the caller is trying to identify,
		all lineLengthThreshold pixels or larger. 
		Method: HoughLinesP identifies all such lines,
		we dynamically keep track of the longest ones in a set.
		Output:	a list of nLongestLines identified in the image.
	"""
	def getLongestLines(edgedImage, nLongestLines, lineLengthThreshold): 
		
		RO_ACCURACY = 3
		THETA_ACCURACY = np.pi/180
		# can be increased to detect more lines
		MAX_LINE_GAP = 15
		
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
				x1, y1, x2, y2 = line
				lineLength = sqrt((y2-y1)**2 + (x2-x1)**2)

				sortedLengths = sorted(longestLines.keys())

				# Replace the shortest so far in the set
				if (lineLength>sortedLengths[0]):
					# It could happen that this length is already present
					if lineLength in longestLines:
						lineLength += 0.00001*randint(1,10)

					del longestLines[sortedLengths[0]]
					longestLines[lineLength] = list([x1,y1,x2,y2])

		return list(longestLines.values())
	
	""" 
		Inputs: numpy or other array-like structures where 
				subtraction is defined
		Output: distance in pixels to the farther endpoint on the segment.
	"""
	def distanceToFartherEndpointOnSegment(point, segment0, segment1, frameWidth):
		fartherEndpoint=segment1 if segment1[1] - segment0[1] > 0 else segment0
		return int(fartherEndpoint[0]-frameWidth/2)
	
	""" 
		Not being used anywhere for now.
		Inputs: numpy or other array-like structures where 
		subtraction is defined
		Output: angle in degrees to the nearest point on the line 
	"""
	def angleFromPointToLineSegment(point, segment0, segment1):
		v = segment1 - segment0
		w = point - segment0

		vw = np.dot(v, w)
		vv = np.dot(v, v)
		if (vw<=0):
			return np.linalg.norm(point-segment0)
		if (vv <= vw):
			return np.linalg.norm(point-segment1)

		pointOnSegment = segment0 + (vw/vv)*v
		directionToPoint = pointOnSegment-point
		return atan2(directionToPoint[1], directionToPoint[0])*180/pi

def main():

	cap=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
	ret,frame=cap.read()
	LINE_LENGTH_THRESHOLD = int((frame.shape)[0]/5)
	FRAME_WIDTH = frame.shape[1]
	
	frameCount = 0
	while True:
		ret,frame=cap.read()
		frameCount+=1
		# Reducing FPS by 5 for better processing
		if (frameCount%5 != 0):
			continue
		
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		edgedFrame = LineDetector.autoCanny(gray)
		longestLine = LineDetector.getLongestLines(edgedFrame, 
			nLongestLines=1, lineLengthThreshold=LINE_LENGTH_THRESHOLD)
		if longestLine is not None:
			horizontalDistanceFromCenter = \
				LineDetector.distanceToFartherEndpointOnSegment(\
					np.array([edgedFrame.shape[1]/2, 0]), \
					np.array(longestLine)[0, :2], \
					np.array(longestLine)[0, 2:], FRAME_WIDTH)
			
			LineDetector.showLines(frame, longestLine)

			print(horizontalDistanceFromCenter)
			stdout.flush()
		
		frameCount=0
		cv2.imshow('Lines', frame)
		cv2.waitKey(1)

	cap.release()
	cv2.destroyAllWindows()

if __name__=="__main__":
	main()