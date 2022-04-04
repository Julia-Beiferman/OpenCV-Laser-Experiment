import cv2
import numpy as np

lower_red = np.array([170,150,0])
upper_red = np.array([180,255,255])

cam = cv2.VideoCapture(0)
ret, img = cam.read()

imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
mask = cv2.inRange(imgHSV,lower_red,upper_red)

kernelOpen=np.ones((0,0))
kernelClose=np.ones((0,0))

maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

cv2.imshow("maskClose",maskClose)
cv2.imshow("maskOpen",maskOpen)
cv2.waitKey(10)

