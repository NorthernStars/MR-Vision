'''
Created on 22.10.2013

@author: northernstars
'''
from core.visionModul import visionModule

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer

from markerrecognition import getReferenceMarker, getContours, minMax, getBoundingRect, getAngleOfVector
from markerrecognition import rotateVector, getTranslateVector, detectMarkerID

from cv2 import COLOR_RGB2GRAY, COLOR_GRAY2RGB, THRESH_BINARY, ADAPTIVE_THRESH_MEAN_C, RETR_LIST, THRESH_BINARY_INV
from cv2 import cvtColor, threshold, Canny, drawContours, contourArea, resize, getRotationMatrix2D
from cv2 import warpAffine, adaptiveThreshold,medianBlur

from copy import copy
from time import time


class Recognition(visionModule):
    '''
    classdocs
    '''
    __imgArea = None
    __imgAreaDetails = None
    __imgID = None
    __imgIDDetails = None
    
    __sceneArea = None
    __sceneAreaDetails = None
    __sceneID = None
    __sceneIDDetails = None
    
    __referenceMarker = None
    __markers = []
    __markerSize = (100, 100)
    __bots = []
    __rectangles = []
    
    __isRecognizing = False
    
    __sceneImgTimer = QTimer()

    def __init__(self, gui=None, imageGrabber=None):
        '''
        Constructor
        '''        
        super(Recognition, self).__init__(gui=gui, imageGrabber=imageGrabber)
        self.__isRecognizing = False   
        self.__imgArea = None 
        self.__imgAreaDetails = None
        self.__imgID = None
        self.__imgIDDetails = None 
        
        self.__sceneArea = None
        self.__sceneAreaDetails = None
        self.__sceneID = None
        self.__sceneIDDetails = None   
        
        self.__referenceMarker = {}
        self.__markers = []
        self.__markerSize = (100, 100)
        self.__bots = []
        self.__rectangles = []
        
        if self._gui != None:
            self.__initGui()
        
    def __initGui(self):
        '''
        Initiates gui
        '''
        # initiate scene
        self.__gviewArea = self._gui.getObj("imgRecognitionArea")
        self.__sceneArea = QGraphicsScene()
        self.__gviewArea.setScene(self.__sceneArea)
        
        self.__gviewID = self._gui.getObj("imgRecognitionID")
        self.__sceneID = QGraphicsScene()
        self.__gviewID.setScene(self.__sceneID)
        
        self.__gviewAreaDetails = self._gui.getObj("imgRecognitionArea2")
        self.__sceneAreaDetails = QGraphicsScene()
        self.__gviewAreaDetails.setScene(self.__sceneAreaDetails)
        
        self.__gviewIDDetails = self._gui.getObj("imgRecognitionID2")
        self.__sceneIDDetails = QGraphicsScene()
        self.__gviewIDDetails.setScene(self.__sceneIDDetails)
        
        # create listeners
        self._gui.connect( "cmdAnalyseReferenceMarker", "clicked()", self.__analyseReferenceMarker )
        self._gui.connect( "cmdRecognitionMarkerArea", "clicked()", self.__recognizeMarkerAreas )
        self._gui.connect( "cmdRecognitionMarkerID", "clicked()", self.__recognizeMarkerIDs )
        self._gui.connect( "cmdCalibrateMarkerIDN", "clicked()", self.__calibrateMarkerN )

        
        # start timer
        self.__sceneImgTimer = QTimer()
        self.__sceneImgTimer.timeout.connect( self._showImage )
        self.__sceneImgTimer.start(250)
        
    def isRecognizing(self):
        '''
        @return: True if module is currently recognizing images
        '''
        return self.__isRecognizing
    
    def __analyseReferenceMarker(self):
        '''
        Analyses reference markers
        '''
        path = str( self._gui.getObj("txtReferenceMarkerPath").text() )
        self.__referenceMarker = getReferenceMarker(path)
        self._gui.status( "Analysed all reference markers" )
        
    def __calibrateMarkerN(self):
        '''
        Calibrates one specific marker
        '''
        n = int( str(self._gui.getObj("txtCalibrateMarkerIDN").text()) )
        
        # check dimension of n
        if n > len(self.__markers)-1:
            n = len(self.__markers)-1
        elif n < 0:
            n = 0
            
        # check if there are markers
        if len(self.__markers) > 0 and self._img != None:
            
            # get data
            inc = self._gui.getObj("chkCalibrateMarkerNInc").isChecked()
            th = self._gui.getObj("sliderThesholdMarkerID").value()
            th2 = self._gui.getObj("sliderThesholdMarkerIDGray").value()
            cannyDown = 30
            cannyUp = 255
            epsilon = float( str(self._gui.getObj("txtMarkerIDEpsilon").text()) )
            contourPadding = int( str(self._gui.getObj("txtMarkerIDContourPadding").text()) )
            
            # get current image and convert
            gray = copy( self._img )
            gray = cvtColor(gray, COLOR_RGB2GRAY)
                
            # calibrate marker
            marker = self.__markers[n]
            drawContours( self.__imgAreaDetails, [marker], -1, (255,0,255), -1 )
            marker = self.__recorgnizeMarker(gray, marker, contourPadding, th, th2, epsilon, cannyDown, cannyUp)
            if marker != None:
                self._gui.status( "Found marker: "+str(marker['id'])+" @ "+str(marker['angle'])+"degree"  )
            
            # increase n
            if inc:
                if n < len(self.__markers)-1:
                    n += 1
                else:
                    n = 0
                
            # set new marker number
            self._gui.getObj("txtCalibrateMarkerIDN").setText( str(n) )
        
    def __recognizeMarkerAreas(self):
        '''
        Recognizes marker area
        '''
        self.__markers = []
        if self._img == None:
            self._gui.status( "No image!" )
            return
        
        # get data
        self.__markers = []
        blocksize = int( str(self._gui.getObj("txtMarkerAreaBlockSize").text()) )
        epsilon = float( str(self._gui.getObj("txtMarkerAreaEpsilon").text()) )
        areaMin = float( str(self._gui.getObj("txtMarkerAreaMin").text()) )/100.0
        areaMax = float( str(self._gui.getObj("txtMarkerAreaMax").text()) )/100.0
        blur = int( str(self._gui.getObj("txtMarkerAreaBlur").text()) )
        
        # check correct blocksize
        if blocksize%2 == 0:
            blocksize -= 1
                
        # get current image and convert
        gray = copy(self._img)        
        gray = cvtColor(gray, COLOR_RGB2GRAY)
        imgArea = gray.shape[0]*gray.shape[1]
        
        # threshold and canny
        gray = medianBlur( gray, blur )
        gray = adaptiveThreshold( gray, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, blocksize, 0 )
        colorImg = cvtColor(gray, COLOR_GRAY2RGB)
        colorImg2 = cvtColor(gray, COLOR_GRAY2RGB)
        
        # get contours
        contours = getContours( gray, epsilon, retr=RETR_LIST, enConvexHull=False)
        
        # add contours with correct area size
        for cnt in contours:
            cntArea = contourArea( cnt )
            cnt = getBoundingRect(cnt)
            
#             if len(cnt) == 4 and cntArea > imgArea*areaMin and cntArea < imgArea*areaMax:
            if cntArea > imgArea*areaMin and cntArea < imgArea*areaMax:
                self.__markers.append( cnt )
                drawContours( colorImg2, [cnt], -1, (0,255,0), -1 )
                
        self._gui.getObj("lblFoundMarker").setText( "Found marker: " + str(len(self.__markers)) )
        
        # draw contours
        drawContours( colorImg, self.__markers, -1, (255,0,0), -1 )
        self.__imgArea = colorImg        
        self.__imgAreaDetails = colorImg2
        
        
    def __recognizeMarkerIDs(self):
        '''
        Recognizes marker ID
        '''
        self.__bots = []
        bots = []
        
        if self._img == None or self.__referenceMarker == None or len( self.__markers ) == 0:
            self._gui.status( "No image or marker contours!" )
            return

        # get data
        th = self._gui.getObj("sliderThesholdMarkerID").value()
        th2 = self._gui.getObj("sliderThesholdMarkerIDGray").value()
        cannyDown = 30
        cannyUp = 255
        epsilon = float( str(self._gui.getObj("txtMarkerIDEpsilon").text()) )
        contourPadding = int( str(self._gui.getObj("txtMarkerIDContourPadding").text()) )
        
        # get current image and convert
        gray = self._img 
        gray = cvtColor(gray, COLOR_RGB2GRAY)
        
        # touch every marker
        t = time()
        for marker in self.__markers:
            markerID = self.__recorgnizeMarker(gray, marker, contourPadding, th, th2, epsilon, cannyDown, cannyUp)
            if markerID != None and markerID['id'] != -1:
                bots.append(markerID)
           
        print time() - t
        self.__bots = bots
        print "found bots"
        for b in bots:
            print "\t,", b
            
    def __recorgnizeMarker(self, gray, marker, contourPadding=0, th=30, th2=128, epsilon=0.01, cannyDown=30, cannyUp=255):
        '''
        recognize one marker
        '''
        # get minmax of marker and calculate center4
        minX, maxX, minY, maxY = minMax(marker)
        markerCenter = ( minX+(maxX-minX), minY+(maxY-minY) )
        
        # slice and resize marker
        sliceImg = gray[minY:maxY, minX:maxX]
        sliceImg = resize( sliceImg, self.__markerSize )
        
        # threshold and canny
        imgTh = threshold( sliceImg, th, 255, THRESH_BINARY_INV )[1]                
        canny = Canny( imgTh, cannyDown, cannyUp )
        
        # set threshold image
#         self.__imgID = imgTh
        
        # get contours again
        contours = getContours( canny, epsilon, enConvexHull=False)
        
        self.__imgID = cvtColor(imgTh, COLOR_GRAY2RGB)
        drawContours(self.__imgID, contours, -1, (255,0,0))
        
        # get first big contour
        imgArea = sliceImg.shape[0]*sliceImg.shape[1]*0.1
        contour = None
        for cnt in contours:
            cntArea = contourArea(cnt)
            if cntArea > imgArea:
                contour = cnt
                break;
                
        if contour == None:
#             print "\tno contour found"
            return None
        
        # get bounding rectangle
        bb = getBoundingRect(contour)
    
        # get marker vectors
        v0 = bb[0]
        v3 = bb[3]
        v = (v3[0]-v0[0], v3[1]-v0[1])
        
        if v[0] == 0 and v[1] == 0:
            print "\tzero devision"
            return None
        
        # get marker rotation
        angle = round( getAngleOfVector(v), 2 )  
        center = ( imgTh.shape[1]*0.5, imgTh.shape[0]*0.5 )
        
        # transformate bounding box to center of image
        bb[0] = getTranslateVector(bb[0], center)
        bb[1] = getTranslateVector(bb[1], center)
        bb[2] = getTranslateVector(bb[2], center)
        bb[3] = getTranslateVector(bb[3], center)
        
        # rotate marker
        rot = getRotationMatrix2D( center, angle, 1.0 )
        sliceImg = warpAffine( imgTh, rot, sliceImg.shape, borderValue=0 )
        
        # rotate bounding box
        angle *= -1
        bb[0] = rotateVector(bb[0], getAngleOfVector(bb[0])+angle)
        bb[1] = rotateVector(bb[1], getAngleOfVector(bb[1])+angle)
        bb[2] = rotateVector(bb[2], getAngleOfVector(bb[2])+angle)
        bb[3] = rotateVector(bb[3], getAngleOfVector(bb[3])+angle)
        
        # transformate bounding box to origin of image
        bb[0] = getTranslateVector(center, bb[0], False)
        bb[1] = getTranslateVector(center, bb[1], False)
        bb[2] = getTranslateVector(center, bb[2], False)
        bb[3] = getTranslateVector(center, bb[3], False)
        
        # get marker id
        minX, maxX, minY, maxY = minMax(bb)
        sliceImg = sliceImg[minY:maxY, minX:maxX]
        markerID = detectMarkerID(sliceImg, minMax(bb), th2, self.__referenceMarker)
        
        # set angle and center of morker
        angle *= -1
        markerID['center'] = markerCenter
        markerID['angle'] += angle
        
        # set image
        sliceImg = cvtColor(sliceImg, COLOR_GRAY2RGB)
#         drawContours( sliceImg, [bb], -1, (0,255,0) )
        self.__imgIDDetails = sliceImg
        
        return markerID
            
        
    def getBots(self):
        '''
        @return: List of found bots
        '''
        return self.__bots
    
    def getRectangles(self):
        '''
        @return: List of found rectangles
        '''
        return self.__rectangles
    
    
    def recognize(self):
        '''
        Recognizes objects in current image
        '''
        if not self.__isRecognizing:
            self.__isRecognizing = True
            # get marker areas
            self.__recognizeMarkerAreas()
            
            # get marker ids
            self.__recognizeMarkerIDs()

            self.__isRecognizing = False
    
        
    def _showImage(self):
        '''
        Shows image
        '''
        self._updateScene( self.__gviewArea, self.__sceneArea, self.__imgArea )
        self._updateScene( self.__gviewAreaDetails, self.__sceneAreaDetails, self.__imgAreaDetails )
        self._updateScene( self.__gviewID, self.__sceneID, self.__imgID, convert=False )
        self._updateScene( self.__gviewIDDetails, self.__sceneIDDetails, self.__imgIDDetails )
        