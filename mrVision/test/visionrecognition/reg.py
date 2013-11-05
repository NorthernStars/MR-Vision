from cv2 import *
from copy import copy
import numpy as np
from markerreg import regMarker, minMax, getContours
from math import sqrt
from operator import itemgetter

contourAreaMin = 0.001
contourAreaMax = 0.1
contourPadding = 0
contourThreshold = 0.4

th1 = 100
th2 = 255
blur = 1

refRange = 10
testfile = "test2.jpg"

epsilon1 = 0.05
epsilon2 = 0.02

usecam = True


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
        if retval:
            imshow("source", img)
    
    

while waitKey(1) < 0:
    retval, img = cam.read()
    
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
        
        for cnt in contours:
            
            if len( cnt ) == 4:
                
                # get area of contour
                cntArea = contourArea( cnt )        
                
                # check if contour area is big enough
                if cntArea > imgArea*contourAreaMin and cntArea < imgArea*contourAreaMax:
                    # show contour data
        #             print "\n----------------\nMARKER"
        #             print "\tarea", cntArea
        
                    # draw contour
                    drawContours(dstC, [cnt], -1, (0,0,255))
                    imshow("contours", dstC)
                    
                    # slice image
                    minX, maxX, minY, maxY = minMax(cnt)
                    
                    if None in [minX, maxX, minY, maxY]:
                        continue
                    
                    slice = gray[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
                    slice = resize( slice, (100,100) )
                    
        #             slice2 = img[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
        #             slice2 = resize( slice2, (100,100) )
                    
                    # find contours on marker
                    sContours = getContours( img=slice, epsilon=epsilon2, retr=RETR_LIST )
                    
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
                            
                            while i < len(set):   
                                refCnt = set[i]   
                                match = None                     
                                    
                                if len(c) > 2 and len(refCnt) > 2:
                                    # get shape matches        
                                    match = matchShapes( c, refCnt, cv.CV_CONTOURS_MATCH_I3, 0 )
                                    
                                    # show match data
        #                             print "\nmatch with key", key, ":(", i, ",", y, ") =",  match
        #                             dst = copy(slice2)
        #                             drawContours(dst, [refCnt], -1, (0,0,255))
        #                             drawContours(dst, [c], -1, (255,0,0))
        #                             imshow("match", dst)
                                    
                                    
                                # check if contours match            
                                if match != None and match < contourThreshold:
                                    # remove shape                            
                                    del set[i]
                                    
                                    # calculate distance between shapes
                                    try:
                                        mC = moments(c)
                                        mRef = moments(refCnt)
                                        centerC = ( int(mC['m10']/mC['m00']), int(mC['m01']/mC['m00']) )
                                        centerRef = ( int(mRef['m10']/mRef['m00']), int(mRef['m01']/mRef['m00']) )
                                        dst = (centerC[0]-centerRef[0], centerC[1]-centerRef[1])
                                        dst = sqrt( dst[0]*dst[0] + dst[1]*dst[1] )
                                        
                                        # add shape to list                            
                                        matches.append( [match, dst] )
                                        
                                        # show additional match data
            #                             print "distance", dst 
            #                             print "\tmatched"
            #                             waitKey(0)
                                        break;
                                    except:
                                        pass
                                else:
                                    i += 1
        
                                
                            y += 1
                        
                        # check if a reference for all contours could be found
                        if len(matches) > 0 and len(set) == 0:
                            # calculate overall match
                            match = 0
                            for m in matches:
                                match += m[0]*m[1]
                                match *= 1.0/len(matches)
                            idList.append( [key, match, 1.0/len(matches)] )
                        
                    
                    # sort list of recognized marker ids
                    if len(idList) > 0 and len(cnt) == 4:
                        idList = sorted(idList, key=itemgetter(1, 2))
                        cnt = convexHull(cnt, clockwise=True)
                        
                        if len(cnt) == 4:                        
                            # get vectors
                            v0 = cnt[0][0]
                            v1 = cnt[1][0]
                            v3 = cnt[3][0]
                                        
                        print "\n-------------------------"
                        print "marker list", idList
                        print "Detected marker", idList[0]
                        print "marker-contour\nv0", v0, "v1", v1, "v3", v3