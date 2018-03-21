import cv2
import numpy as np
from matplotlib import pyplot as plt
import glob


def auto_canny(image, sigma=0.33):
	median = np.median(image)
	lower = int(max(0, (1.0-sigma)*median))
	upper = int(min(255, (1.0 + sigma)*median))
	return cv2.Canny(image, lower, upper)

cap=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
while True:
	ret,frame=cap.read()
	cv2.imshow("test-h264", frame)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#blurred = cv2.GaussianBlur(gray, (3, 3), 0)
	edged_frame = auto_canny(gray)
	cv2.imshow('Edges', edged_frame)
	(h,w) = edged_frame.shape
	
	cv2.waitKey(10)

cap.release()
cv2.destroyAllWindows()