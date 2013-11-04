from cv2 import *
from copy import copy
import numpy as np
from markerreg import regMarker, minMax, getContours
from math import sqrt
from operator import itemgetter

contourAreaMin = 0.001
contourAreaMax = 0.1
contourPadding = 2
contourThreshold = 0.5

refRange = 5
testfile = "test2.jpg"




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

# read image
img = imread(testfile)
img = cvtColor(img, COLOR_BGR2RGB)

# convert to gray and blur
gray = cvtColor(img, COLOR_RGB2GRAY)   
gray = medianBlur(gray,1)
imshow("blur", gray)
            
# create binary image
gray = threshold( gray, 30, 255, THRESH_BINARY )[1]
imshow("threshold", gray)

# canny edge detector
gray = Canny(gray, 100, 100, apertureSize=3)
imshow("canny", gray)
    

contourImg = copy(gray)
contours = getContours( img=contourImg, epsilon=0.05 )

# draw contours
dst = copy(img)
drawContours(dst, contours, -1, (0,0,255))
imshow("contours", dst)

imgArea = gray.shape[0]*gray.shape[1]
print "image size:", gray.shape, "area:", imgArea
print "found:", len(contours), "contours"

drawApproxCnts = []
drawHulls = []

for cnt in contours:
    
    if len( cnt ) == 4:
        
        # get area of contour and arc length
        cntArea = contourArea( cnt )
        cntArc = arcLength( cnt, True )
        cntBounding = boundingRect(cnt)
        
        # check if contour area is big enough
        if cntArea > imgArea*contourAreaMin and cntArea < imgArea*contourAreaMax:
            # print contour data
            print "\n----------------"
            print "\tarea", cntArea
            print "\tarclength:", cntArc
            
            # slice image
            minX, maxX, minY, maxY = minMax(cnt)
            slice = gray[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
            slice2 = img[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
            slice = resize( slice, (100,100) )
            slice2 = resize( slice2, (100,100) )
            
            # find contours on marker
            sContours = getContours( img=slice, epsilon=0.02 )
            
            # get ID
            found = False
            idList = []
            for key in idContours:
                set = copy(idContours[key])
                matches = []
                
                # search a reference for every contour
                y = 0
                for c in sContours:
                    i = 0
                    match = None                    
                    
                    while i < len(set):   
                        refCnt = set[i]
                        
                        if len(refCnt) <= len(c):         
                            # get shape matches          
                            match = matchShapes( c, refCnt, cv.CV_CONTOURS_MATCH_I3, 0 )
                            
                            print "\nmatch", key, ":(", i, ",", y, ") =",  match
                            dst = copy(slice2)
                            drawContours(dst, [c], -1, (255,0,0))                
                            drawContours(dst, [refCnt], -1, (0,0,255))
                            imshow("match", dst)
                            waitKey(0)
                            
                        # check if contours match            
                        if match != None and match < contourThreshold:
                            # remove shape                            
                            del set[i]
                            
                            # calculate distance between shapes
                            mC = moments(c)
                            mRef = moments(refCnt)
                            centerC = ( int(mC['m10']/mC['m00']), int(mC['m01']/mC['m00']) )
                            centerRef = ( int(mRef['m10']/mRef['m00']), int(mRef['m01']/mRef['m00']) )
                            dst = (centerC[0]-centerRef[0], centerC[1]-centerRef[1])
                            dst = sqrt( dst[0]*dst[0] + dst[1]*dst[1] )
                            print "distance", dst
                            
                            # add shape to list                            
                            matches.append( [match, dst] ) 
                            print "\tmatched"
                            break;
                        else:
                            i += 1
                    y += 1
                
                # check if a reference for all contours could be found
                if len(matches) > 0:
                    # calculate overall match
                    match = 0
                    for m in matches:
                        match += m[0]*m[1]
                    idList.append( [key, match, 1.0/len(matches)] )
                
            
            # sort list
            idList = sorted(idList, key=itemgetter(2, 1))
            print "\nlist", idList
            
waitKey(0)