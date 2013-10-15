import cv2
from imageprocessing import *
from time import time


cam = openCam(0, 1024, 768)
if cam:
	r = 10

	tm1 = time()
	for i in range(r):
		img = getImgFromCam(cam)
	tm2 = time()
	print "fps:", r/(tm2-tm1)

	while cv2.waitKey(1) < 0:
		img = getImgFromCam(cam)
		if img != None:
			cv2.imshow("img2", img)

	cam.release()	
	cv2.destroyAllWindows()
