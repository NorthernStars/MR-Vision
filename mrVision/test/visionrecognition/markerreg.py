from cv2 import *
from copy import copy
from os.path import isfile
from math import sqrt, atan2
from operator import itemgetter
from numpy import array

def sortContour(contour=[]):
    '''
    Sorts contour clockwise
    @param contour: Contour with 4 points
    @return: Contour and list of vectors with clockwise sorted vectors
    '''
    if len(contour) != 4:
        return contour
    
    # create list of polar coordinates
    polar = []
    for p in contour:
        if len(p[0]) == 2:
            
            # get cartesian coordinates
            x = p[0][0]
            y = p[0][1]
            
            # calc polar coordinates
            r = sqrt(x*x + y*y)
            a = atan2(y, x)
            
            # add polar point
            polar.append( [a, r, x, y] )
    
    # get nearest and farest point
    polar = sorted(polar, key=itemgetter(1))
    p0 = polar[0]
    p2 = polar[-1]
    del polar[0]
    del polar[-1]
    
    # get other points by angle
    polar = sorted(polar, key=itemgetter(0))
    p1 = polar[0]
    p3 = polar[1]
    
    # create cartesian coordinates
    p0 = [p0[2], p0[3]]
    p1 = [p1[2], p1[3]]
    p2 = [p2[2], p2[3]]
    p3 = [p3[2], p3[3]]
    
    return contour, [p0, p1, p2, p3]
    

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


def getContours(img=None, epsilon=0.1, retr=RETR_EXTERNAL):
    '''
    Searches in image for contours
    @param img: Image to analyse (needs to be grayscale!)
    @param epsilon: Epsilon parameter for approxPolyDP algorithm
    @return: List of contours
    '''
    retContours = []
    if img != None:
        # find contours
        contours, hirachy = findContours( img, retr, CHAIN_APPROX_SIMPLE )     
        
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
    
    shapeList = [[], [], [], []]
    
    # convert to gray and blur
    gray = cvtColor(img, COLOR_RGB2GRAY) 
                
    # create binary image
    gray = threshold( gray, 30, 255, THRESH_BINARY )[1]
    center = (gray.shape[1]*0.5, gray.shape[0]*0.5)
    
    for i in range(4):
        angle = i*90
        rot = getRotationMatrix2D(center, angle, 1.0)
        gray = warpAffine(gray, rot, gray.shape)  
    
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
                    shapeList[i-1].append(cnt)
                    
    # return list of shapes
    return shapeList



def getMatch(contour, refSet):
    # search a reference for every contour
    y = 0
    set = copy(refSet)
    matches = []
    
    # search for best reference contour
    # for every contour touch every reference
    # contour and calculate match
    matches = []
    
    for i in range( len(contour) ):        
        cnt = copy( contour[i] )
        
        for y in range( len(refSet) ):
            refCnt = copy( refSet[y] )
            
            # check number of points
            # must be more than 3 points
            if len(cnt) > 3 and len(refCnt) > 3:
                # get match
                match = matchShapes( cnt, refCnt, cv.CV_CONTOURS_MATCH_I3, 0 ) 
                
                # get minmax values
                mmCnt = minMax( cnt )
                mmRefCnt = minMax( refCnt )
                
                if None not in mmCnt and None not in mmRefCnt:
                    # get distance between shapes
                    centerCnt = (mmCnt[1]-mmCnt[0], mmCnt[3]-mmCnt[2])
                    centerRefCnt = (mmRefCnt[1]-mmRefCnt[0], mmRefCnt[3]-mmRefCnt[2])
                    distance = (centerCnt[0]-centerRefCnt[0], centerCnt[1]-centerRefCnt[1])
                    distance = sqrt( distance[0]*distance[0] + distance[1]*distance[1] )
                    
                    # calculate current match
                    match *= distance
                    
                    # add match
                    matches.append( [i, y, match] )
        
    # return best match
    return calcMatch(matches)


def calcMatch(matches=[]):
    '''
    Calculates complete match
    @param matches: List of matches
    @return: Match value 
    '''
    retMatch = -1
    count = 0
    excCnt = []
    excRef = []
    
    # search through all matches
    for match in matches:        
        if match[0] not in excCnt and match[1] not in excRef:
            excCnt.append(match[0])
            excRef.append(match[1])
            count += 1
            
            if retMatch == -1:
                retMatch = match[2]
            else:
                retMatch += match[2]
    
    if retMatch != -1 and count > 0:
        retMatch /= count;
        
    return retMatch
        
    