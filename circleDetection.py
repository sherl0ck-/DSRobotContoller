import cv2
from math import pi

from LineDetector import *

def detectCircles(gray):
	dp = 2

	minRadius=50
	maxRadius=300
	minDist=300
	
	# Use code from auto_canny function to select param1
	median = np.median(gray)
	
	sigma=0.33
	param1 = int(min(255, (1.0 + sigma)*median))

	param2= int(minRadius*pi)

	circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp, \
	minDist=minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
	return circles

def getHouseBall(img, circles):
	# 41, 25 - 58,34
	lowerAB = np.array([0, 150, 150])
	upperAB = np.array([100, 250, 250])
	labImg = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)

	mask = cv2.inRange(labImg, lowerAB, upperAB)
	#res = np.zeros(labImg.shape)
	#res = cv2.bitwise_and(img, img, dst=res, mask=mask)
	
	for circle in circles:
		cx,cy,r = circle
		lx = int(min(0, cx-r))
		ux = int(min(cx+r, img.shape[1]-1))
		ly = int(min(0, cy-r))
		uy = int(min(cy+r, img.shape[0]-1))
		countRedPixels = 0
		for x in range(lx, ux):
			for y in range(ly, uy):
				if mask[y, x] != 0:
					countRedPixels+=1

		if countRedPixels > 500:
			showCircles(img, circle)
		
		
		print(countRedPixels)	
			
def showCircles(img, circles):
	circles = np.uint16(np.around(circles))
	for circle in circles:
		center = (circle[0], circle[1])
		# circle center
		cv2.circle(img, center, 1, (0, 100, 100), 3)
		# circle outline
		radius = circle[2]
		cv2.circle(img, center, radius, (255, 0, 255), 3)


def main():
	cap=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
	ret,frame=cap.read()
	frameCount=0
	while True:
		ret,frame=cap.read()
		frameCount+=1
		
		if (frameCount%3 == 0):
			continue
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		circles = detectCircles(gray)
		if circles is not None:
			getHouseBall(frame, circles[0])
			
		cv2.imshow('circles', frame)
		cv2.waitKey(1)

	cv2.destroyAllWindows()


if __name__=="__main__":
	main()