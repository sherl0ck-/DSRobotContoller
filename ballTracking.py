from collections import deque
import numpy as np
import argparse
import imutils
import cv2
from sys import stdout

# 3 problems:
#  - Stop when we approach the ball on the ground
#  - Stop when we approach the ball on the robot
#  - Note where the ball dissapears (R/L)

redLower = (0, 96, 31)
redUpper = (6, 255, 255)

blueLower = (104, 54, 0)
blueUpper = (143, 183, 255)

yellowLower = (25, 73, 104)
yellowUpper = (62, 255, 255)

nFrames = 0
camera=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
(grabbed, frame) = camera.read()
halfFrameWidth = int(frame.shape[1]/2)
halfFrameHeight = int(frame.shape[0]/2)
MIN_BALL_RADIUS = 10
UNDER_OUR_NOSE=450
IN_FRONT_OF_US=0.75*halfFrameHeight

print(int(halfFrameWidth)) # For protocol purpose
stdout.flush()

while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
    nFrames=(nFrames+1)%5
    if (nFrames!=0):
        continue

    if not grabbed:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color, then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, yellowLower, yellowUpper)
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

            # Ball is below the camera, which means we arrived at the destination
            if int(y)>380:
                print(-halfFrameWidth)
                break
            if int(radius) > IN_FRONT_OF_US:
                print(-halfFrameWidth)
            else:
                print(int(x) - halfFrameWidth)
            stdout.flush()

        else:
            print(halfFrameWidth)
            stdout.flush()

    else:
        print(halfFrameWidth)
        stdout.flush()

    # show the frame to our screen
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
