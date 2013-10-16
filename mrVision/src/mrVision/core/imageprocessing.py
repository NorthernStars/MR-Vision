from cv2 import VideoCapture, cvtColor, cv, findChessboardCorners, cornerSubPix, undistort, calibrateCamera, imread
from cv2 import TERM_CRITERIA_COUNT, TERM_CRITERIA_EPS, COLOR_RGB2GRAY
from os.path import isfile

def openCam(camNum=0):
	'''
	Returns VideoCapture object for camera
	'''
	if type(camNum) == int and camNum >= 0:
		cam = VideoCapture(0)
		cam.set( cv.CV_CAP_PROP_FRAME_WIDTH, vidW )
		cam.set( cv.CV_CAP_PROP_FRAME_HEIGHT, vidH )
		return cam
	return False


def getImgFromCam(cam=None, grey=False):
	'''
	Grabs image from camera 
	'''
	if cam != None & cam.isOpened():
		retval, img = cam.read()
		if retval:
			if grey:
				img = cvtColor( img, COLOR_RGB2GRAY )
			return img
	return None
	
	
def getImgFromFile(fname=None, gray=False):
	'''
	Grabs image from file
	'''
	if type(fname) == str and isfile(fname):
		img = imread( fname, 1 )
		if gray:
			img = cvtColor( img, COLOR_RGB2GRAY )
		return img
		
	return None
		

def getChessBoardCorners(img, patternSize, term=(TERM_CRITERIA_EPS+TERM_CRITERIA_COUNT,30,0.1), subpix=(5,5)):
	'''
	Tries to find chessboard corners in image
	'''
	found = False
	corners = None
	if img != None and patternSize != None:
		gray = cvtColor( img, COLOR_RGB2GRAY )
		found, corners = findChessboardCorners( gray, patternSize )
		if found:			
			cornerSubPix( gray, corners, subpix, (-1, -1), term )
			corners.reshape(-1, 2)
					
	return found, corners
	
	
def findChessBoardPatternSize(img, xMax=10, yMax=10, xStart=3, yStart=3):
	'''
	Finds maximum chessboard pattern size in image
	'''
	if xMax > 2 and yMax > 2 and xStart > 2 and yStart > 2:
		patternSize = []
		found = False
			
		# try every compination of pattern size
		for x in range(xStart, xMax+1):
			for y in range(yStart, yMax+1):
				# check for pattern in image
				if getChessBoardCorners( img, (x,y) )[0]:
					# found pattern
					found = True
					patternSize.append( (x,y) )
					
		if found:
			# return found pattern
			return patternSize		
	return None
	
	
def getCalibrationData(img, obj_points, img_points):
	'''
	Returns calibration data camera_matrix, dist_coefs for image
	'''
	camera_matrix = None
	dist_coefs = None
	if img != None and obj_points != None and img_points != None:
		h, w = img.shape[:2]
		parameters = calibrateCamera( obj_points, img_points, (w, h) )
		
		if len(parameters) == 5:
			return parameters[1], parameters[2]
		
	return camera_matrix, dist_coefs


def undistortImg( img, camera_matrix, dist_coefs ):
	'''
	Undistorts image using calibration data
	'''
	if img != None and camera_matrix != None and dist_coefs != None:
		return undistort( img, camera_matrix, dist_coefs )

	return None

