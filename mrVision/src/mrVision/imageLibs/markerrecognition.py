'''
Created on 13.11.2013

@author: northernstars
'''
from os import listdir, getcwd
from os.path import isfile, isdir
from math import sqrt, atan2, degrees, radians, cos, sin

from cv2 import imread, cvtColor, threshold, getRotationMatrix2D, warpAffine, findContours
from cv2 import arcLength, approxPolyDP, convexHull, rectangle
from cv2 import COLOR_RGB2GRAY, THRESH_BINARY, THRESH_BINARY_INV, CHAIN_APPROX_SIMPLE, RETR_EXTERNAL, COLOR_GRAY2RGB
from numpy import array, zeros, bool_, uint8, count_nonzero

import Image

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
    shapeList = []
    
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
        matrix = getMarkerMatrix( grayCopy, minmax, rows, columns, 0.5)
        
        # add matrix of rotation
        shapeList.append( ( i*90, matrix ) ) 
                    
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

def detectMarkerID(img, minmax, th=0.3, refMarker={}):
    '''
    Detects marker ID
    '''
    markerID = {'id': -1, 'center': (0,0), 'angle': 0, 'size': (minmax[1]-minmax[0], minmax[3]-minmax[2]) }
    
    # get matrix of image
    img = threshold(img, 155, 255, THRESH_BINARY_INV)[1]
    
    if img == None:
        return markerID
    
    matrix = getMarkerMatrix(img, minmax, th=th, show=False)
    
    MAX = 5
    
    # check reference marker to get correct ID and rotation
    for vID in refMarker:

        for p in range(4):
            angle, marker = refMarker[vID][p]
            i = 0
            
            for r in range(7):
                
                for c in range(7):
    
                    if marker[r][c] != matrix[r][c]:
                        i += 1
                    if i > MAX:
                        break
            
                if i > MAX:
                    break
                    
            if i < MAX:
                MAX = i
                markerID['id'] = vID
                markerID['angle'] = angle
                print "errors", i
        
            if i == 0:
                break
        if i == 0:
            break
    
    return markerID

def getMarkerMatrix(img, minmax, rows=7,columns=7, th=0.3, show=False):
    '''
    Creates code matrix, based on image
    '''    
    imgHeight, imgWidth = img.shape
    borderMultiply = 4.0
    
    imgC = cvtColor(img, COLOR_GRAY2RGB)
    
    # create empty matrix
    matrix = zeros( (rows, columns), bool_ )
    matrix2 = zeros( (rows, columns), uint8 )
    matrix3 = zeros( (rows, columns), uint8 )
    
    restHeight = imgHeight
    for r in range(rows):
        # calculate height of pattern
        drow = restHeight / (rows - r)
        restWidth = imgWidth

        for c in range(columns):
            # calculate width and position of pattern        
            dcol = restWidth / (columns - c)
            patternSize = drow * dcol
            
            xStart = imgWidth - restWidth
            yStart = imgHeight - restHeight
            xEnd = xStart + dcol
            yEnd = yStart + drow
            
            rectangle( imgC, (xStart, yStart), (xEnd, yEnd), (255,0,0) )
            
            # set matrix element
            val = count_nonzero( img[yStart:yEnd, xStart:xEnd] )
            matrix[r][c] = val
            matrix2[r][c] = val
            
            if r == 0 or r == rows-1 or c == 0 or c == columns-1:
                thres = patternSize * th * borderMultiply
            else:
                thres = patternSize * th

            matrix[r][c] = val > thres
            if show:
                matrix2[r][c] = val
                matrix3[r][c] = thres
            
            # set rest width and height
            restWidth -= dcol
            
        # set rest height
        restHeight -= drow
          
    if show:  
        bild = Image.fromarray(imgC)
        bild.show()           
        print "matrix:\n", matrix 
        print "matrix2:\n", matrix2
        print "matrix3:\n", matrix3    
        
    return matrix
    