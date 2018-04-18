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

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
redLower = (0, 96, 31)
redUpper = (6, 255, 255)

nFrames = 0
camera=cv2.VideoCapture('http://192.168.1.1:8080/?action=stream')
(grabbed, frame) = camera.read()
halfFrameWidth = int(frame.shape[1]/2)
print(int(halfFrameWidth))
stdout.flush()

while True:
    # grab the current frame
    (grabbed, frame) = camera.read()
    nFrames=(nFrames+1)%5
    if (nFrames!=0):
        continue
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if not grabbed:
        break

    # resize the frame, blur it, and convert it to the HSV
    # color space
    # frame = imutils.resize(frame, width=600)
    # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    mask = cv2.inRange(hsv, redLower, redUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
        # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points

            cv2.circle(frame, (int(x), int(y)), int(radius),
                (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

            # Ball is below the camera, which means we arrived at the destination
            if int(y)>450:
                print(-halfFrameWidth)
                break

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
