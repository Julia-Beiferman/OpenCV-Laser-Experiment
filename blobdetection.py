import cv2
import numpy as np;

im = cv2.imread("blob_detection.jpg", cv2.IMREAD_GRAYSCALE)

detector = cv2.SimpleBlobDetector_create()

keypoints = detector.detect(im)

im_with_keypoints = cv2.drawKeypoints(im, keypoints, np.array([]), (255,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 
cv2.imshow("Keypoints", im_with_keypoints)
cv2.waitKey(0)
