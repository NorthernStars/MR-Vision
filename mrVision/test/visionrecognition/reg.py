from cv2 import *
from copy import copy
import numpy as np
from markerreg import regMarker, minMax, getContours, sortContour, getMatch
from math import sqrt, acos, degrees, ceil
from operator import itemgetter

contourAreaMin = 0.001
contourAreaMax = 0.1
contourPadding = 0
contourThreshold = 0.4

th1 = 100
th2 = 255
blur = 3

refRange = 2
testfile = "test2.jpg"

epsilon1 = 0.05
epsilon2 = 0.02

usecam = False


# load id 1 contours
idContours = {}

for i in range(refRange):
    fName = "id" + str(i) + ".jpg"
    idContours[str(i)] = regMarker(fName)

# create windows
namedWindow("blur")
namedWindow("threshold")
namedWindow("canny")
namedWindow("contours")

moveWindow("blur", 50, 50)
moveWindow("threshold", 400, 50)
moveWindow("canny", 750, 50)
moveWindow("contours", 50, 350)


if not usecam:
    # read image
    img = imread(testfile)
    img = cvtColor(img, COLOR_BGR2RGB)
else:
    # read image from cam
    cam = VideoCapture(0)
    retval = False
    while not retval:
        retval, img = cam.read()    
    
k = 0
#while waitKey(1) < 0:
while k == 0:
    k = 1
    #retval, img = cam.read()
    retval = True
    
    if retval:
        # convert to gray and blur
        gray = cvtColor(img, COLOR_RGB2GRAY)   
        gray = medianBlur(gray,blur)
        imshow("blur", gray)
                    
        # create binary image
        gray = threshold( gray, th1, th2, THRESH_BINARY )[1]
        imshow("threshold", gray)
        
        # canny edge detector
        gray = Canny(gray, 100, 100, apertureSize=3)
        imshow("canny", gray)    
        
        contourImg = copy(gray)
        contours = getContours( img=contourImg, epsilon=epsilon1 )
        
        # draw contours
        dstC = copy(img)
        
        imgArea = gray.shape[0]*gray.shape[1]
        print "image size:", gray.shape, "area:", imgArea
        print "found:", len(contours), "contours"
        
        drawApproxCnts = []
        drawHulls = []
        
        # search through found contours
        for markerCnt in contours:
            
            if len( markerCnt ) == 4:
                # get area of contour
                cntArea = contourArea( markerCnt )        
                
                # check if contour area is big enough
                if cntArea > imgArea*contourAreaMin and cntArea < imgArea*contourAreaMax:
                    # show contour data
                    print "\n----------------\nMARKER"
                    print "\tarea:", cntArea
                    print "\tcontour:\n", markerCnt
                    
                    # get contour points in clockwise order
                    markerCnt, vec = sortContour(markerCnt)
        
                    # draw contour
                    drawContours(dstC, [markerCnt], -1, (0,0,255))
                    
                    
                    # slice image
                    minX, maxX, minY, maxY = minMax(markerCnt)
                    
                    if None in [minX, maxX, minY, maxY]:
                        continue
                    
                    slice = gray[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
                    slice = resize( slice, (100,100) )
                    
                    slice2 = img[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
                    slice2 = resize( slice2, (100,100) )
                    
                    # rotate image
                    v0 = (vec[0][0], vec[0][1])
                    v1 = (vec[1][0], vec[1][1])
                    v = (v1[0]-v0[0], v1[1]-v0[1])
                    angle = 90-degrees( acos( v[1]/sqrt(v[0]*v[0] + v[1]*v[1]) ) )
                    
                    m = moments(markerCnt)
                    center = ( slice.shape[1]*0.5, slice.shape[0]*0.5 )
                    
                    rot = getRotationMatrix2D(center, angle, 1.0)
                    slice = warpAffine(slice, rot, slice.shape)
                    slice2 = warpAffine(slice2, rot, slice.shape)
                    
                    line(dstC, v0, v1, (0,255,0), 2)
                    line(dstC, (0,0), (0,100), (0,255,0), 2)
                    
                    imshow("contours", dstC)
                    
                    
                    # find contours on marker
                    markerIdContours = getContours( img=slice, epsilon=epsilon2, retr=RETR_LIST )
                    
                    # get ID
                    idList = []
                    
                    # search through all available markers
                    for idKey in idContours:
                        rotationSet = copy( idContours[idKey] )
                        rotationMatch = -1
                        
                        print "------------------------"
                        print "MARKER ID", idKey
                        
                        # search through all available rotations
                        for i in range(len(rotationSet)):
                            set = copy( rotationSet[i] )
                            
                            print "------------------------"
                            print "ROTATION", i*90
                            
                            # get and add match
                            match = getMatch(markerIdContours, set)                            
                            if (match < rotationMatch or rotationMatch == -1) and match >= 0:
                                rotationMatch = match
                                
                        # add best match to list
                        if rotationMatch >= 0:
                            idList.append( [idKey, match, i*90] )
                    
                    # sort idList
                    idList = sorted(idList, key=itemgetter(1))
                    print "\nidList:"
                    for e in idList:
                        e[2] += angle
                        print e
                        
                        
                    
                    
#                     for key in idContours:
#                         rotSet = copy(idContours[key])
#                         rotMatches = []
#                         
#                         # iterate over all rotations of marker id
#                         for s in rotSet: 
#                             set = copy(s)
#                             matches = [] 
#                             print "set length", len(s)
#                             
#                             getMatch()
#                             
#                             # check if a reference for all contours could be found
#                             print "lmatch", len(matches), "lset", len(set)
#                             if len(matches) > 0 and len(set) == 0:
#                                 # calculate overall match
#                                 match = 0
#                                 for m in matches:
#                                     match += m[0]*m[1]
#                                     match *= 1.0/len(matches)
#                                 idList.append( [key, match, 1.0/len(matches)] )
#                         
#                     
#                     # sort list of recognized marker ids
#                     if len(idList) > 0 and len(cnt) == 4:
#                         idList = sorted(idList, key=itemgetter(1, 2))
#                         cnt = convexHull(cnt, clockwise=True)
#                         
#                         if len(cnt) == 4:                        
#                             # get vectors
#                             v0 = cnt[0][0]
#                             v1 = cnt[1][0]
#                             v3 = cnt[3][0]
#                                         
#                         print "\n-------------------------"
#                         print "marker list", idList
#                         print "Detected marker", idList[0]
#                         print "marker-contour\nv0", v0, "v1", v1, "v3", v3