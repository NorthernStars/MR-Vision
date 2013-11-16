'''
Created on 22.10.2013

@author: northernstars
'''
from core.visionModul import visionModule

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer

from markerrecognition import getReferenceMarker, getContours, sortContour, minMax, detectMarker

from cv2 import COLOR_RGB2GRAY, COLOR_GRAY2RGB, THRESH_BINARY
from cv2 import cvtColor, threshold, Canny, drawContours, contourArea, resize, getRotationMatrix2D, warpAffine

from copy import copy
from math import degrees, acos, sqrt


class Recognition(visionModule):
    '''
    classdocs
    '''
    __imgThArea = None
    __imgCannyArea = None
    __imgThID = None
    __imgCannyID = None
    
    __sceneThArea = None
    __sceneCannyArea = None
    __sceneThID = None
    __sceneCannyID = None
    
    __referenceMarker = {}
    __markerContours = []
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
        self.__imgThArea = None 
        self.__imgCannyArea = None
        self.__imgThID = None
        self.__imgCannyID = None 
        
        self.__sceneThArea = None
        self.__sceneCannyArea = None
        self.__sceneThID = None
        self.__sceneCannyID = None   
        
        self.__referenceMarker = {}
        self.__markerContours = []
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
        self.__gviewThArea = self._gui.getObj("imgRecognitionThArea")
        self.__sceneThArea = QGraphicsScene()
        self.__gviewThArea.setScene(self.__sceneThArea)
        
        self.__gviewThID = self._gui.getObj("imgRecognitionThID")
        self.__sceneThID = QGraphicsScene()
        self.__gviewThID.setScene(self.__sceneThID)
        
        self.__gviewCannyArea = self._gui.getObj("imgRecognitionCannyArea")
        self.__sceneCannyArea = QGraphicsScene()
        self.__gviewCannyArea.setScene(self.__sceneCannyArea)
        
        self.__gviewCannyID = self._gui.getObj("imgRecognitionCannyID")
        self.__sceneCannyID = QGraphicsScene()
        self.__gviewCannyID.setScene(self.__sceneCannyID)
        
        # create listeners
        self._gui.connect( "cmdAnalyseReferenceMarker", "clicked()", self.__analyseReferenceMarker )
        self._gui.connect( "cmdRecognitionMarkerArea", "clicked()", self.__recognizeMarkerAreas )
        self._gui.connect( "cmdRecognitionMarkerID", "clicked()", self.__recognizeMarkerIDs )

        
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
        
    def __recognizeMarkerAreas(self):
        '''
        Recognizes marker area
        '''
        self.__markerContours = []
        if self._img == None:
            self._gui.status( "No image!" )
            return
        
        # get data
        self.__markerContours = []
        th = self._gui.getObj("sliderThesholdMarkerArea").value()
        cannyDown = self._gui.getObj("sliderMarkerAreaCannyDown").value()
        cannyUp = self._gui.getObj("sliderMarkerAreaCannyUp").value()
        epsilon = float( str(self._gui.getObj("txtMarkerAreaEpsilon").text()) )
        areaMin = float( str(self._gui.getObj("txtMarkerAreaMin").text()) )/100.0
        areaMax = float( str(self._gui.getObj("txtMarkerAreaMax").text()) )/100.0
                
        # get current image and convert
        gray = copy(self._img)        
        gray = cvtColor(gray, COLOR_RGB2GRAY)
        imgArea = gray.shape[0]*gray.shape[1]
        
        # threshold and canny
        gray = threshold( gray, th, 255, THRESH_BINARY )[1]
        
        self.__imgThArea = copy( gray )
        gray = Canny( gray, cannyDown, cannyUp )
        
        # get contours
        contours = getContours( copy(gray), epsilon, enConvexHull=False)
        
        # add contours with correct area size
        for cnt in contours:
            cntArea = contourArea( cnt )
            
            if len(cnt) == 4 and cntArea > imgArea*areaMin and cntArea < imgArea*areaMax:
                self.__markerContours.append( cnt )
        
        # draw contours
        canny = cvtColor(gray, COLOR_GRAY2RGB)
        drawContours( canny, self.__markerContours, -1, (255,0,0), -1 )
        self.__imgCannyArea = canny
        
        
    def __recognizeMarkerIDs(self):
        '''
        Recognizes marker ID
        '''
        self.__bots = []
        
        if self._img == None or len( self.__markerContours ) == 0:
            self._gui.status( "No image or marker contours!" )
            return

        # get data
        th = self._gui.getObj("sliderThesholdMarkerID").value()
        cannyDown = self._gui.getObj("sliderMarkerIDCannyDown").value()
        cannyUp = self._gui.getObj("sliderMarkerIDCannyUp").value()
        epsilon = float( str(self._gui.getObj("txtMarkerIDEpsilon").text()) )
        contourPadding = int( str(self._gui.getObj("txtMarkerIDContourPadding").text()) )
        
        # get current image and convert
        gray = copy( self._img )
        gray = cvtColor(gray, COLOR_RGB2GRAY)
        
        # touch every marker
        for marker in self.__markerContours:
            # sort marker and get vectors
            marker, vec = sortContour(marker)
            
            # sliceImg marker
            minX, maxX, minY, maxY = minMax(marker)    
            if None in [minX, maxX, minY, maxY]:
                continue
            markerCenter = (maxX-minX, maxY-minY)
            
            sliceImg = gray[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
            sliceImg = resize( sliceImg, self.__markerSize )
            
            # rotate marker
            v0 = (vec[0][0], vec[0][1])
            v1 = (vec[1][0], vec[1][1])
            v = (v1[0]-v0[0], v1[1]-v0[1])
            angle = round( 90-degrees( acos( v[1]/sqrt(v[0]*v[0] + v[1]*v[1]) ) ), 1)
            
            center = ( sliceImg.shape[1]*0.5, sliceImg.shape[0]*0.5 )
            
            rot = getRotationMatrix2D( center, angle, 1.0 )
            sliceImg = warpAffine( sliceImg, rot, sliceImg.shape, borderValue=255 )
            
            # threshold and canny
            sliceImg = threshold( sliceImg, th, 255, THRESH_BINARY )[1]            
            self.__imgThID = sliceImg            
            sliceImg = Canny( sliceImg, cannyDown, cannyUp )
            
            
            # get marker contour again
            if angle > 2.5:
                marker = getContours( copy(sliceImg), epsilon, enConvexHull=False)
                newMarker = None
                imgArea = sliceImg.shape[0]*sliceImg.shape[1]*0.25
                for cnt in marker:
                    if contourArea(cnt) > imgArea:
                        newMarker = cnt
                        break
                
                # check if marker was rotated
                if newMarker != None:
                    # sliceImg and resize marker
                    minX, maxX, minY, maxY = minMax(newMarker)    
                    if None in [minX, maxX, minY, maxY]:
                        continue
                    
                    sliceImg = sliceImg[minY+contourPadding:maxY-contourPadding, minX+contourPadding:maxX-contourPadding]
                    sliceImg = resize( sliceImg, self.__markerSize )
                
            # detect marker ID
            contour = getContours( copy(sliceImg), epsilon, enConvexHull=False)
            marker = detectMarker( contour, self.__referenceMarker, self.__markerSize )
            if marker == None:
                continue
            else:
                marker['center'] = markerCenter
                self.__bots.append(marker)
            
            # show contours
            sliceImg = cvtColor(sliceImg, COLOR_GRAY2RGB)            
            drawContours(sliceImg, contour, -1, (255,0,0))
            
            
            self.__imgCannyID = sliceImg
        
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
            
            # get rectangles

            self.__isRecognizing = False
    
        
    def _showImage(self):
        '''
        Shows image
        '''
        self._updateScene( self.__gviewThArea, self.__sceneThArea, self.__imgThArea, convert=True )
        self._updateScene( self.__gviewCannyArea, self.__sceneCannyArea, self.__imgCannyArea )
        self._updateScene( self.__gviewThID, self.__sceneThID, self.__imgThID, convert=True )
        self._updateScene( self.__gviewCannyID, self.__sceneCannyID, self.__imgCannyID, convert=False )
        