from cv2 import VideoCapture, cvtColor, findChessboardCorners, cornerSubPix, undistort, calibrateCamera, imread
from cv2 import TERM_CRITERIA_COUNT, TERM_CRITERIA_EPS
from cv2 import COLOR_RGB2GRAY

from PyQt4.QtGui import QImage, QPixmap
from numpy import ndarray
from os.path import isfile

def openCam(camNum=0):
	'''
	Returns VideoCapture object for camera
	'''
	if type(camNum) == int and camNum >= 0:
		cam = VideoCapture(0)
		return cam
	return False


def getImgFromCam(cam=None, grey=False):
	'''
	Grabs image from camera 
	'''
	if (cam != None) and cam.isOpened():
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


def imageToPixmap(img=None):
	'''
	Converts image to pyqt pixmap
	'''
	# get image shape
	w = img.shape[1]
	h = img.shape[0]
	
	# convert image
	qimg = QImage( img.data, w, h, QImage.Format_RGB888 )
	return QPixmap.fromImage( qimg )

def getImageSizeFromCorners(corners=[]):
	'''
	Searches in list of corners for image size (outer borders)
	@return: [ (xmin, xmax), (ymin, ymax) ]
	'''	
	xmin = -1
	xmax = -1
	ymin = -1
	ymax = -1
	
	if type(corners) == ndarray and len(corners) > 0:
		xmin = corners[0][0][0]
		xmax = corners[0][0][0]
		ymin = corners[0][0][1]
		ymax = corners[0][0][1]
		
		# sreach max and min
		for c in corners:
			if c[0][0] > xmax:
				xmax = c[0][0]
			if c[0][0] < xmin:
				xmin = c[0][0]
			if c[0][1] > ymax:
				ymax = c[0][1]
			if c[0][1] < ymin:
				ymin = c[0][1]
			
		return [ (xmin, xmax), (ymin, ymax) ]
	
	return None