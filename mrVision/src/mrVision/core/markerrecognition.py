'''
Created on 13.11.2013

@author: northernstars
'''
from os import listdir, getcwd
from os.path import isfile, isdir
from math import sqrt, atan2, degrees, radians, cos, sin

from cv2 import imread, cvtColor, threshold, getRotationMatrix2D, warpAffine, findContours
from cv2 import arcLength, approxPolyDP, convexHull, mean
from cv2 import COLOR_RGB2GRAY, THRESH_BINARY, CHAIN_APPROX_SIMPLE, RETR_EXTERNAL
from numpy import array, zeros, bool_, array_equal

def getReferenceMarker(path=None, rows=7, columns=7):
    '''
    Returns list of reference markers
    '''
    # check path
    if path == None or not isdir(path):
        path = getcwd()
        print "using", path
    
    if not path.endswith("/"):
        path += "/"
    
    # analyse marker files
    markerList = {}
    for e in listdir(path):
        if isfile(path+e) and str(e).startswith("id") and str(e).endswith(".jpg"):
            vID = e.replace("id", "").replace(".jpg", "")
            
            marker = analyseMarkerFromFile( path+e, rows, columns )
            
            # add marker to list
            if marker != None:
                markerList[str(vID)] = marker
            
    return markerList

            
def analyseMarkerFromFile(fName="", rows=7, columns=7):
    '''
    Recognizes marker contours
    @param fName: Filepath of marker file (needs to be binary)
    @return: List of contour of the marker and center of contours
             [ <list contours>, <list center 0>, <list center 90>, <list center 180>, <list center 270> ]
    '''
    shapeList = {'d0': None, 'd90': None, 'd180': None, 'd270': None }
    
    # check if file exsits
    if not isfile(fName):
        print fName, "is no file!"
        return None
       
    # read image
    img = imread(fName)
                     
    # convert to gray and blur
    gray = cvtColor(img, COLOR_RGB2GRAY) 
                
    # create binary image
    gray = threshold( gray, 128, 255, THRESH_BINARY )[1]
    center = (gray.shape[1]*0.5, gray.shape[0]*0.5)
    minmax = [ 0, gray.shape[1], 0, gray.shape[0] ]
    
    for i in range(4):
        grayCopy = gray
        angle = i*90
        rot = getRotationMatrix2D(center, angle, 1.0)
        grayCopy = warpAffine(grayCopy, rot, gray.shape) 
    
        # get matrix
        matrix = getMarkerMatrix( grayCopy, minmax, rows, columns, 128)
        
        # add matrix of rotation
        shapeList[ "d"+str(i*90) ] = matrix
                    
    # return list of shapes
    return shapeList

def getCenterOfContour(contour):
    '''
    Calculates center of contour
    '''
    mmCnt = minMax( contour)
    return ( mmCnt[0]+(mmCnt[1]-mmCnt[0])*0.5, mmCnt[2]+(mmCnt[3]-mmCnt[2])*0.5 )
    
def getContours(img=None, epsilon=0.1, retr=RETR_EXTERNAL, enConvexHull=False):
    '''
    Searches in image for contours
    @param img: Image to analyse (needs to be grayscale!)
    @param epsilon: Epsilon parameter for approxPolyDP algorithm
    @param retr: retr value of opencv findContours method
    @param enConvexHull: If True convex hull for approximation is used 
    @return: List of contours
    '''
    retContours = []
    if img != None:
        # find contours
        contours, hirachy = findContours( img, retr, CHAIN_APPROX_SIMPLE ) #@UnusedVariable     
        
        # approximate contours
        for cnt in contours:
            cntArc = arcLength( cnt, True )
            approx = approxPolyDP( cnt, epsilon*cntArc, True )
            
            # sort contour points clockwise by using convex hull
            if enConvexHull:
                approx = convexHull( approx, clockwise=True )
            retContours.append(approx)
    
    return retContours

def getBoundingRect(cnt = []):
    '''
    @return: Bounding contour of contour
    '''
    leftmost = array(cnt[cnt[:,:,0].argmin()][0])
    rightmost = array(cnt[cnt[:,:,0].argmax()][0])
    topmost = array(cnt[cnt[:,:,1].argmin()][0])
    bottommost = array(cnt[cnt[:,:,1].argmax()][0])
    return array( [leftmost, bottommost, rightmost, topmost] )
    

def getTranslateVector(vec, point, foreward=True):
    '''
    @return: New vector from point to vector
    '''
    v = []
    if foreward:
        v.append( vec[0]-point[0] )
        v.append( vec[1]-point[1] )
    else:
        v.append( point[0]+vec[0] )
        v.append( point[1]+vec[1] )
    return v
    

def minMax(contour=[]):
    '''
    Gets the minimum and maximum X-/Y-Value
    of a contour
    @param contour: Contour
    @return: minX, maxX, minY, maxY
    '''
    minX = contour[0][0]
    maxX = contour[2][0]
    minY = contour[3][1]
    maxY = contour[1][1]
        
    return minX, maxX, minY, maxY

def getAngleOfVector(vec):
    '''
    Returns rotation of vector to y axis
    '''
    return degrees( atan2(vec[1], vec[0]) )

def rotateVector(vec, angle):
    '''
    @return: Vector rotated by angle
    '''
    angle = radians(angle)
    r = sqrt(vec[0]*vec[0] + vec[1]*vec[1])
    return array( [r*cos(angle), r*sin(angle)] )

def detectMarkerID(img, minmax, th=100, refMarker={}):
    '''
    Detects marker ID using hamming code
    '''
    markerID = {'id': -1, 'center': (0,0), 'angle': 0, 'size': (minmax[1]-minmax[0], minmax[3]-minmax[2]) }
    
    # get matrix of image
    matrix = getMarkerMatrix(img, minmax, th=th)
    
    # check reference marker to get correct ID and rotation
    for vID in refMarker:
        marker = refMarker[vID]
        angle = -1
        
        # check angles
        if array_equal(matrix, marker['d0']):
            angle = 0
        elif array_equal(matrix,marker['d90']):
            angle = 90
        elif array_equal(matrix, marker['d180']):
            angle = 180
        elif array_equal(matrix, marker['d270']):
            angle = 270
        else:
            continue
        
        markerID['id'] = vID
        markerID['angle'] = angle
        break
    
    return markerID

def getMarkerMatrix(img, minmax, rows=7,columns=7, th=100):
    '''
    Creates code matrix, based on image
    '''    
    minX, maxX, minY, maxY = minmax
    imgW = maxX-minX
    imgH = maxY-minY
    dx = int( round(float(imgW)/float(columns)) )
    dy = int( round(float(imgH)/float(rows)) )
    
    # createempty matrix
    matrix = zeros( (rows, columns), bool_ )
    
    for r in range(rows):
        
        for c in range(columns):
            startX = minX+r*dx
            endX = startX+dx
            startY = minY+c*dy
            endY = startY+dy

            # set matrix element
            matrix[r][c] = mean( img[ startX:endX, startY:endY ] )[0] > th
                    
    print "matrix\n", matrix
    return matrix
    