import numpy as np
import cv2
from time import sleep
from core.imageprocessing import *


# pattern and square dimension
#pattern_size = (9, 12)
#pattern_size = (7, 7) # tisch
pattern_size = (5, 8) # testmuster
square_size = 1.0

# video size
vidW = 1024
vidH = 768

# set usePic = True to use pictures instead of cam
usePic = False
#fname = "ImageRGB2.png"
fname = "testimg/chess10.jpg"
#fname2 = "testimg/transform.jpg"
fname2 = "testimg/testpunkte.jpg"
output = "testimg/finTestpunkte.jpg"

# set findPattern = True to search for pattern
findPattern = True

# several data
pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)
pattern_points *= square_size

obj_points = []
img_points = []
camera_matrix, dist_coefs = None, None

# exit flag
ex = False



# set and open capture device
if not usePic:
	cam = openCam(0)
	
# find pattern size

if findPattern:
	# get image
	if not usePic:
		img = getImgFromCam(cam)
	else:
		img = getImgFromFile(fname)
	
	# find pattern
	if img != None:	
		
		print "searching for chessboard pattern"
		pattern = findChessBoardPatternSize( img, 25, 25, 3, 3 )
	
		if len(pattern) > 0:
			pattern_size = pattern[-1]
			print "found pattern size:", pattern_size
		else:
			print "ERROR: NO CHESSBOARD FOR CALIBRATION"
			exit()


'''
------------------ GET CALIBRATION DATA ------------------
'''
frames = 0
maxFrames = 10
while not ex and (usePic or cam):
	
	# read image
	if not usePic:
		img = getImgFromCam(cam)
	else:
		img = getImgFromFile(fname)
	
	if img != None:
		# show source
		cv2.imshow( "source", img )
	
		print "processing img..."
		# get chess board corners
		found, corners = getChessBoardCorners( img, pattern_size )

		# If found, add object points, image points (after refining them)
		if found:
			
			# show chessboard
			cv2.drawChessboardCorners( img, pattern_size, corners, found )
			cv2.imshow( "chessboard", img )
			
			# add img and obj points
			img_points.append( corners.reshape(-1, 2) )
        	obj_points.append( pattern_points )
        		
        	frames += 1
        		
        	# get calibration values
        	camera_matrix, dist_coefs = getCalibrationData(img, obj_points, img_points )
        
        else:
			cv2.destroyWindow( "chessboard" )
		
	else:
		ex = True
		
	if cv2.waitKey(1) >= 0 or frames >= maxFrames:
		ex = True

# close windows
cv2.destroyAllWindows()
sleep(1)


'''
------------------ UNDISTORT IMAGE ------------------
'''
if camera_matrix != None:
	print "camera matrix:\n", camera_matrix
	print "distortion coefficients: ", dist_coefs.ravel()

	
	ex = False
	
	while not ex and (usePic or cam):

		# read image
		if not usePic:
			img = getImgFromCam(cam)
		else:
			img = getImgFromFile(fname2)
	
		if img != None:
			# show source image
			cv2.imshow( "source", img )
		
			# undistort 1
			dst = undistortImg( img, camera_matrix, dist_coefs )
		
			# show image
			cv2.imshow( "undistorted", dst )
			cv2.imwrite(output, dst)
		else:
			ex = True
	
		if cv2.waitKey(1) >= 0:
			ex = True
			

if not usePic:
	cam.release()
	
cv2.destroyAllWindows()
