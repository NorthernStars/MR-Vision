from cv2 import *
from copy import copy
from os.path import isfile

def minMax(contour=[]):
    '''
    Gets the minimum and maximum X-/Y-Value
    of a contour
    @param contour: Contour
    @return: minX, maxX, minY, maxY
    '''
    minX = None
    minY = None
    maxX = None
    maxY = None
    
    for p in contour:
        p = p[0]
        
        if minX == None or p[0] < minX:
            minX = p[0]
        elif maxX == None or p[0] > maxX:
            maxX = p[0]
        
        if minY == None or p[1] < minY:
            minY = p[1]
        elif maxY == None or p[1] > maxY:
            maxY = p[1]
    
    return minX, maxX, minY, maxY


def getContours(img=None, epsilon=0.1):
    '''
    Searches in image for contours
    @param img: Image to analyse (needs to be grayscale!)
    @param epsilon: Epsilon parameter for approxPolyDP algorithm
    @return: List of contours
    '''
    retContours = []
    if img != None:
        # find contours
        contours, hirachy = findContours( img, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE )     
        
        # approximate contours
        for cnt in contours:
            cntArc = arcLength( cnt, True )
            approx = approxPolyDP( cnt, epsilon*cntArc, True )
            
            # sort contour points clockwise by using convex hull
            #approx = convexHull( approx, clockwise=True )
            retContours.append(approx)
    
    return retContours



def regMarker(fName=""): 
    '''
    Recognizes marker contours
    @param fName: Filepath of marker file (needs to be binary)
    @return: List of contours of the marker
    '''
    
    # check if file exsits
    if not isfile(fName):
        return []
       
    # read image
    img = imread(fName)
    
    shapeList = []
    
    # convert to gray and blur
    gray = cvtColor(img, COLOR_RGB2GRAY) 
                
    # create binary image
    gray = threshold( gray, 30, 255, THRESH_BINARY )[1]        
    
    # find contours
    contours, hirachy = findContours( gray, RETR_TREE, CHAIN_APPROX_SIMPLE )
    
    imgArea = gray.shape[0]*gray.shape[1]    
    for i in range( len(contours) ):
        cnt = contours[i]
        
        if len( cnt ) > 3:            
            # get area of contour and arc length
            cntArea = contourArea( cnt )
            
            # check if contour area is big enough
            if cntArea < 0.9*imgArea:                    
                shapeList.append(cnt)
                
    # return list of shapes
    return shapeList