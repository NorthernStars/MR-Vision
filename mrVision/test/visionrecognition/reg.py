from cv2 import *
from copy import copy
import numpy as np
from markerreg import regMarker, minMax, getContours, sortContour, getMatch
from math import sqrt, acos, degrees, ceil
from operator import itemgetter

contourAreaMin = 0.001
contourAreaMax = 0.05
contourPadding = 0

markerSize = (100,100)

th1 = 120
th2 = 255
blur = 1

cannyDown = 1
cannyUp = 255
apertureSize = 1

refRange = 20
testfile = "test.jpg"

epsilon1 = 0.05
epsilon2 = 0.001

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
# while waitKey(1) < 0:
while k == 0:
    k = 1
#     retval, img = cam.read()
    retval = True
    
    if retval:
        # convert to gray and blur
        gray = cvtColor(img, COLOR_RGB2GRAY)   
        gray1 = medianBlur(gray,blur)
        imshow("blur", gray1)
                    
        # create binary image
        gray1 = threshold( gray1, th1, 255, THRESH_BINARY )[1]
        imshow("threshold", gray1)
        
        # canny edge detector
        gray1 = Canny(gray1, cannyDown, cannyUp, apertureSize)
        imshow("canny", gray1)
        
        contourImg = copy(gray1)
        contours = getContours( img=contourImg, epsilon=epsilon1 )
        
        # draw contours
        dstC = copy(img)
        
        imgArea = gray1.shape[0]*gray1.shape[1]
        print "--------------------------"
        print "image size:", gray.shape, "area:", imgArea
        print "found:", len(contours), "contours"
        waitKey(0)
        
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
#                     print "\n----------------\nMARKER"
#                     print "\tarea:", cntArea
                    
                    # get contour points in clockwise order
                    markerCnt, vec = sortContour(markerCnt)
        
                    # draw contour
                    drawContours(dstC, [markerCnt], -1, (0,0,255))
                    
                    
                    # slice image
                    minX, maxX, minY, maxY = minMax(markerCnt)
                    
                    if None in [minX, maxX, minY, maxY]:
                        continue
                    
                    slice = gray[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
                    slice = resize( slice, markerSize )
                    
                    slice2 = img[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
                    slice2 = resize( slice2, markerSize )
                    
                    # rotate image
                    v0 = (vec[0][0], vec[0][1])
                    v1 = (vec[1][0], vec[1][1])
                    v = (v1[0]-v0[0], v1[1]-v0[1])
                    angle = 90-degrees( acos( v[1]/sqrt(v[0]*v[0] + v[1]*v[1]) ) )
                    
                    center = ( slice.shape[1]*0.5, slice.shape[0]*0.5 )
                    
                    rot = getRotationMatrix2D(center, angle, 1.0)
                    slice = warpAffine(slice, rot, slice.shape)
                    slice2 = warpAffine(slice2, rot, slice.shape)
                    
                    # draw rotation axis 
                    line(dstC, v0, v1, (0,255,0), 1)
                    line(dstC, (0,0), (0,100), (0,255,0), 1)
                    
#                     print "\tangle:", angle
                    sliceg = threshold( slice, 75, 255, THRESH_BINARY )[1]
                    sliceg = Canny(sliceg, cannyDown, cannyUp, apertureSize)
                    imshow("sliced", slice)
                    imshow("slicedg", sliceg)
                    imshow("contours", dstC)
                    waitKey(0)
                    
                    
                    # find contours on marker
                    markerIdContours = getContours( img=slice, epsilon=epsilon2, retr=RETR_EXTERNAL )
#                     drawContours(slice2, markerIdContours, -1, (0,255,0))
#                     imshow("match", slice2)
#                     waitKey(0)
                     
                    # get ID
                    idList = []
                    
                    # search through all available markers
                    for idKey in idContours:
                        rotationSet = copy( idContours[idKey] )
                        rotationMatch = -1
                        rotationAngle = 0
                        
#                         print "------------------------"
#                         print "MARKER ID", idKey
                        
                        # search through all available rotations
                        for i in range(len(rotationSet)):
                            set = copy( rotationSet[i] )
                            
#                             print "------------------------"
#                             print "ROTATION", i*90
                            
                            # get and add match
                            match = getMatch(markerIdContours, set, slice2)                        
                            if (match < rotationMatch or rotationMatch == -1) and match >= 0:
                                rotationMatch = match
                                rotationAngle = i*90-180
                                
                        # add best match to list
                        if rotationMatch >= 0:
                            idList.append( [int(idKey), rotationMatch, rotationAngle] )
                    
                    # sort idList
                    idList = sorted(idList, key=itemgetter(1, 0))
                    
                    #
#                     print "\nidList:"
#                     for e in idList:
#                         e[2] += angle
#                         print e
                        
                    # get marker
                    if len(idList) > 0:
                        marker = idList[0]
                        center = ( minX+(maxX-minX)*0.5, minY+(maxY-minY)*0.5 )
                        marker.append( center )    
                        print "marker:", marker                    
                        
                    
#     waitKey(0)