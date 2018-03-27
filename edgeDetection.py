import cv2
import numpy as np
from matplotlib import pyplot as plt
import glob
from random import randint

def auto_canny(image, sigma=0.33):
	median = np.median(image)
	lower = int(max(0, (1.0-sigma)*median))
	upper = int(min(255, (1.0 + sigma)*median))
	return cv2.Canny(image, lower, upper)

def houghLines(img, edged_frame):
	h = (img.shape)[0]
	w = (img.shape)[1]
	print(h,w)
	LINE_LENGTH_THRESHOLD = int(2*h/3)
	RO_ACCURACY = 3
	THETA_ACCURACY = np.pi/180
	# can be increased to detect more lines
	MAX_LINE_GAP = 10

	#edged_frame = edged_frame/255
	lines = cv2.HoughLinesP(edged_frame, RO_ACCURACY, THETA_ACCURACY, 
		threshold=LINE_LENGTH_THRESHOLD, 
		minLineLength=LINE_LENGTH_THRESHOLD,
		maxLineGap=MAX_LINE_GAP)

	if lines is None:
		return
	print(len(lines))
	# show
	randColor=[0, 0, 0]
	for l in lines:
		for line in l:
			x1 = line[0]
			y1 = line[1]
			x2 = line[2]
			y2 = line[3]
			
			for i in range (3):
				randColor[i] = randint(0, 255)

			cv2.line(img,(x1,y1),(x2,y2),tuple(randColor),3)
	
cap=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
while True:
	ret,frame=cap.read()
	cv2.imshow("test-h264", frame)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	edged_frame = auto_canny(gray)
	houghLines(frame, edged_frame)
	cv2.imshow('Lines', frame)
	cv2.waitKey(100)

cap.release()
cv2.destroyAllWindows()