'''
Created on 13.11.2013

@author: northernstars
'''
from os import listdir, getcwd
from os.path import isfile
from math import sqrt, atan2
from copy import copy
from operator import itemgetter

from cv2 import imread, cvtColor, threshold, getRotationMatrix2D, warpAffine, findContours, contourArea
from cv2 import arcLength, approxPolyDP, matchShapes, convexHull
from cv2 import COLOR_RGB2GRAY, THRESH_BINARY, RETR_TREE, CHAIN_APPROX_SIMPLE, RETR_EXTERNAL
from cv2.cv import CV_CONTOURS_MATCH_I3

def getReferenceMarker(path=None):
    '''
    Returns list of reference markers
    '''
    # check path
    if path == None:
        path = getcwd()
    
    if not path.endswith("/"):
        path += "/"
    
    # analyse marker files
    markerList = {}
    for e in listdir(path):
        if isfile(path+e) and str(e).startswith("id") and str(e).endswith(".jpg"):
            vID = e.replace("id", "").replace(".jpg", "")
            marker = analyseMarkerFromFile(path+e)
            
            # add marker to list
            markerList[str(vID)] = marker
            
    return markerList

            
def analyseMarkerFromFile(fName=""):
    '''
    Recognizes marker contours
    @param fName: Filepath of marker file (needs to be binary)
    @return: List of contour of the marker and center of contours
             [ <list contours>, <list center 0>, <list center 90>, <list center 180>, <list center 270> ]
    '''
    
    # check if file exsits
    if not isfile(fName):
        return []
       
    # read image
    img = imread(fName)
    
    shapeList = {'contours': [], 'd0': [], 'd90': [], 'd180': [], 'd270': [] }
                     
    # convert to gray and blur
    gray = cvtColor(img, COLOR_RGB2GRAY) 
                
    # create binary image
    gray = threshold( gray, 128, 255, THRESH_BINARY )[1]
    center = (gray.shape[1]*0.5, gray.shape[0]*0.5)
    
    for i in range(4):
        grayCopy = copy(gray)
        angle = i*90
        rot = getRotationMatrix2D(center, angle, 1.0)
        grayCopy = warpAffine(grayCopy, rot, gray.shape) 
    
        # find contours
        contours, hirachy = findContours( grayCopy, RETR_TREE, CHAIN_APPROX_SIMPLE )
        
        imgArea = gray.shape[0]*gray.shape[1]    
        for y in range( len(contours) ):
            cnt = contours[y]
            
            if len( cnt ) > 3:            
                # get area of contour and arc length
                cntArea = contourArea( cnt )
                
                # calc center of contour
                centerCnt = getCenterOfContour(cnt)
                
                # check if contour area is big enough
                if cntArea < 0.9*imgArea:
                    
                    # on first run append contours
                    if i == 0:               
                        shapeList['contours'].append( cnt )
                    
                    # add center of contours
                    shapeList[ "d"+str(i*90) ].append( centerCnt )
                    
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
        contours, hirachy = findContours( img, retr, CHAIN_APPROX_SIMPLE )     
        
        # approximate contours
        for cnt in contours:
            cntArc = arcLength( cnt, True )
            approx = approxPolyDP( cnt, epsilon*cntArc, True )
            
            # sort contour points clockwise by using convex hull
            if enConvexHull:
                approx = convexHull( approx, clockwise=True )
            retContours.append(approx)
    
    return retContours


def sortContour(contour=[]):
    '''
    Sorts contour clockwise
    @param contour: Contour with 4 points
    @return: Contour and list of vectors with clockwise sorted vectors
    '''
    if len(contour) != 4:
        return contour, []
    
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
    minX = tuple(contour[contour[:,:,0].argmin()][0])[0]
    maxX = tuple(contour[contour[:,:,0].argmax()][0])[0]
    minY = tuple(contour[contour[:,:,1].argmin()][0])[1]
    maxY = tuple(contour[contour[:,:,1].argmax()][0])[1]
        
    return minX, maxX, minY, maxY


def getMatch(contour, refSet):
    # search a reference for every contour
    y = 0
    matches = []
    
    # search for best reference contour
    # for every contour touch every reference
    # contour and calculate match
    for i in range( len(contour) ):        
        cnt = contour[i]
        
        
        for y in range( len(refSet) ):
            refCnt = refSet[y]
            
            # check number of points
            # must be more than 3 points
            if len(cnt) > 3 and len(refCnt) > 3:
                
                # get match
                match = matchShapes( cnt, refCnt, CV_CONTOURS_MATCH_I3, 0 )
                if match > 0:
                    matches.append( {'nContour': i, 'nRefContour': y, 'match': match} )
        

    # sort matches    
    matches = sorted(matches, key=itemgetter('match'))
        
    # return best match
#     print "matches", matches
#     for m in matches:
#         print "\t", m

    if len(matches) == 0:
        return matches
    
    return calcMatch( matches, len(refSet) )


def calcMatch(matches, nRefContours):
    '''
    Calculates complete match
    @param matches: List of matches
    @return: Match value 
    '''
    count = 0
    exceptCnt = []
    exceptRef = []
    retMatches = []
    
    # search through all matches
    for match in matches:     
        if match['nContour'] not in exceptCnt and match['nRefContour'] not in exceptRef:
#             print "\ttake", match[0], ",", match[1]
            exceptCnt.append(match['nContour'])
            exceptRef.append(match['nRefContour'])
            retMatches.append(match)
            count += 1
        
#     print "\tfound", count, "from", len(getIdsFromMatches(matches))
#     
#     lIDs = len( getIdsFromMatches(retMatches) )
#     lRefIDs = len( getIdsFromMatches(matches, 1) )
    
    if count == nRefContours:
#         print "\tchoose", retMatches
        return retMatches
    
    return None

def calcDistanceMatch(matchSet, contour, distanceSet):
    '''
    Calculates distance match of contours
    '''
    match = 0
    distance = -1
    for m in matchSet:
        cntN = m['nContour']
        refN = m['nRefContour']        
        centerCnt = getCenterOfContour( contour[cntN] )
        centerRef = distanceSet[refN]
        
        distance = ( abs(centerCnt[0]-centerRef[0]), abs(centerCnt[1]-centerRef[1]) )
        distance = sqrt( distance[0]*distance[0] + distance[1]*distance[1] )
        match += m['match']*distance
        
    return match
        


def detectMarker(contour, referenceMarkers, markerSize):
    '''
    Detects markers from contours
    '''
    idList = []
    
    # search through all available markers
    for idKey in referenceMarkers:
        rotationSet = referenceMarkers[idKey]
        
        # search through all available rotations
        cntSet = rotationSet['contours']
        
        # get matches
        matchSet = getMatch( contour, cntSet )
        if matchSet == None:
            continue 
         
        # calc match distances
        d0 = calcDistanceMatch( matchSet, contour, rotationSet['d0'] )
        d90 = calcDistanceMatch( matchSet, contour, rotationSet['d90'] )
        d180 = calcDistanceMatch( matchSet, contour, rotationSet['d180'] )
        d270 = calcDistanceMatch( matchSet, contour, rotationSet['d270'] )
        
        # find best angle
        i = 1
        angle = 0
        match = d0
        for d in [d90, d180, d270]:
            if match < 0 or (match > 0 and d >= 0 and d < match):
                match = d
                angle = i*90
            i += 1

        angle -= 180
        
        # add to list
        idList.append( {'id': idKey, 'match': match, 'angle': angle, 'center': (-1, -1)} )
        
            
        
#         print "angle:", i*90, "match:", match              
#         if (match < rotationMatch or rotationMatch == -1) and match >= 0:
#             rotationMatch = match
#             rotationAngle = i*90-180
#                 
#         # add best match to list
#         if rotationMatch >= 0:
#             idList.append( [int(idKey), rotationMatch, rotationAngle] )
      
    # sort idList
    idList = sorted(idList, key=itemgetter('match', 'id'))
    
    # get marker
    if len(idList) > 0:
        return idList[0]
    
    return None


# def getIdsFromMatches(matches=[], idx=0):
#     '''
#     Returns Ids for different contours from matches
#     @param matches: List of matches
#     @param idx: Index number of match entries to search in
#     @return: List of different contour IDs
#     '''
#     ids = []
#     for m in matches:
#         if m[idx] not in ids:
#             ids.append(m[idx])
#             
#     return ids