'''
Created on 22.10.2013

@author: northernstars
'''
from core.visionModul import visionModule

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer
from thread import start_new_thread

from cv2 import cvtColor, COLOR_RGB2GRAY, THRESH_BINARY, medianBlur, threshold, HoughCircles, circle, line
from cv2.cv import CV_HOUGH_GRADIENT
from numpy import array, around, argsort, int16
from numpy.linalg import solve

from cPickle import dump, load
from copy import copy

class Transformation(visionModule):
    '''
    classdocs
    '''    
    __imgScene = None
    __imgSceneTh = None
    
    __calibrated = False
    __calibrating = False
    
    __basisMatrix = array([[1,0],[0,1]])
    __offset = array([0,0])

    def __init__(self, gui=None, imageGrabber=None):
        '''
        Constructor
        '''        
        super(Transformation, self).__init__(gui=gui, imageGrabber=imageGrabber)
        self.__calibrated = False
        self.__calibrating = False
        self.__basisMatrix = array([[1,0],[0,1]])
        self.__offset = array([0,0])
        
        if self._gui != None:
            self.__initGui()
        
    def __initGui(self):
        '''
        Initiates gui
        '''
        # initiate scene
        self.__gview = self._gui.getObj("imgTransformation")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        self.__gviewTh = self._gui.getObj("imgTransformationThreshold")
        self.__sceneTh = QGraphicsScene()
        self.__gviewTh.setScene(self.__sceneTh)
        
        # create listeners
        self._gui.connect( "cmdCalibrateTransformation", "clicked()", self.__calibrateTransformation )
        self._gui.connect( "cmdSaveTransformation", "clicked()", self.saveSettings )
        self._gui.connect( "cmdLoadTransformation", "clicked()", self.loadSetting )
        
        # start timer
        self.__sceneImgTimer = QTimer()
        self.__sceneImgTimer.timeout.connect( self._showImage )
        self.__sceneImgTimer.start(100)  
    
    def saveSettings(self):
        '''
        Save Settings
        '''
        # stop video        
        options = copy(self._gui.dialogOptionsDef)
        options['type'] = self._gui.dialogTypes['FileSave']
        options['title'] = "Save configuration"
        options['filetypes'] = "Configuration (*cfg *mr)"
        src = str( self._gui.dialog(options) )
        
        if len(src) > 0:
            # check path
            if not src.endswith(".cfg"):
                src += ".cfg"
            
            # save data to file     
            data = {'basismatrix': self.__basisMatrix,
                    'offset': self.__offset,
                    'calibrated': self.__calibrated}
                        
            dump( data, open(src, "wb") )            
            self._gui.status("Configuration saved to: " + src)
    
    def loadSetting(self):
        '''
        Load Settings
        '''
        # get path
        options = copy(self._gui.dialogOptionsDef)
        options['filetypes'] = "config file (*cfg)"
        src = str( self._gui.dialog(options) )
        
        if len(src) > 0:           
            # load file
            data = load( open(src, "rb") )
            
            if 'basismatrix' in data:
                self.__basisMatrix = data['basismatrix']
            if 'offset' in data:
                self.__offset = data['offset']
            if 'calibrated' in data:
                self.__calibrated = data['calibrated']
            
            self._gui.status("Configuration loaded.")
        
    def isCalibrated(self):
        '''
        @return: True if image is calibrated
        '''
        return self.__calibrated
    
    def isCalibrating(self):
        '''
        @return: True if calibration is in progress
        '''
        return self.__calibrating
        
    def startCalibration(self):
        '''
        Starts calibration of transformation
        '''
        if  not self.isCalibrating():
            start_new_thread(self.__calibrateTransformation, ())
        
    def __calibrateTransformation(self):
        '''
        Calculates transformation values
        '''
        if self._img == None:
            return                
        
        self._gui.status("Calibrating transformation...")
        self.__calibrating = True
        img = self._img

        '''
        Preprocessing image:
        '''
        try:             
            # get data
            th = self._gui.getObj("sliderThesholdCircles").value()
            cannyUp = self._gui.getObj("sliderCirclesCannyUp").value()
            thCircles = self._gui.getObj("sliderThesholdCircles2").value()
            minRadius = (float( str(self._gui.getObj("txtCirclesRadiusMin").text()) )/100.0) * img.shape[0]
            maxRadius = (float( str(self._gui.getObj("txtCirclesRadiusMax").text()) )/100.0) * img.shape[0]
            minDist = (float( str(self._gui.getObj("txtCirclesDistanceMin").text()) )/100.0) *img.shape[0]
            blur = 5
                        
            # blur image for better result
            gimg = cvtColor(img, COLOR_RGB2GRAY)
            gimg = medianBlur( gimg, blur )
            
            # create binary image
            gimg = threshold( gimg, th, 255, THRESH_BINARY)[1]
            self.__imgSceneTh = gimg
            
            '''
            Searching for circles by using Hough-Transformation:
            '''
            circles = HoughCircles( gimg, CV_HOUGH_GRADIENT, 1, int(minDist), param1=cannyUp, param2=thCircles, minRadius=int(minRadius), maxRadius=int(maxRadius) )
            circles = around(circles).astype(int16)
            centers = circles[0][:,:3]
            
            '''
            Identifying corners of playing field by evaluating centers of circles:
            Existence of 4 points are mandatory!
            '''
            vlnr = argsort(centers[:,0],)
            
            pts_left = centers[vlnr[:2],:]
            pts_right = centers[vlnr[2:],:]
            
            # defining points for coordinate system
            # left:
            p00 = pts_left[argsort(pts_left[:,1])[0],:]
            p01 = pts_left[argsort(pts_left[:,1])[1],:]
            # right:
            p10 = pts_right[argsort(pts_right[:,0])[0],:]
            p11 = pts_right[argsort(pts_right[:,0])[1],:]
            
            
            # correcting axes with aritmethic mean. p00 and p11 are set
            # vertical:
            a_v1 = p01-p00
            a_v2 = p11-p10            
            a_v = (a_v1 + a_v2)/2
            # horizontal:
            a_h1 = p10-p00
            a_h2 = p11-p01
            a_h = (a_h1 + a_h2)/2
            
            # correcting other corners   
            p10c = p00 + a_h
            p01c = p11 - a_h
            
            # paint lines and circles
            circle(img,(p00[0],p00[1]),p00[2],(255,0,0),2)        
            circle(img,(p11[0],p11[1]),p11[2],(255,0,0),2)
            circle(img,(p10[0],p10[1]),p10[2],(255,0,0),2)
            circle(img,(p01[0],p01[1]),p01[2],(255,0,0),2)
            
            line(img,(p00[0],p00[1]),(p01c[0],p01c[1]),(0,255,0),2)
            line(img,(p00[0],p00[1]),(p10c[0],p10c[1]),(0,255,0),2)   
            line(img,(p10c[0],p10c[1]),(p11[0],p11[1]),(0,255,0),2)
            line(img,(p01c[0],p01c[1]),(p11[0],p11[1]),(0,255,0),2)
            
            self.__imgScene = img
            
            '''
            Setting Offset and Basismatrix
            '''
            self.__offset = array([p00[0],p00[1]])
            self.__basisMatrix = array([[a_v[0],a_h[0]],[a_v[1],a_h[1]]])
            
        except:            
            self._gui.status("Error while calibrating transformation")
            
        self.__calibrating = False
        self._gui.status("Calibration finished.")
        
        pass
    
    def transformatePoint(self, point=array([0,0])):
        '''
        Transformates a point into local coordinates space
        @param point: Tuple (x,y) of points coordinates to transform
        @return: Tuple (x,y) of transformed coordinates
        '''
        
        A = self.__basisMatrix
        O = self.__offset
        
        # Creating reference to origin of coordinates space 
        b = point - O
        transformation = solve(A,b)
        
        return transformation
    
    def transformObjects(self, objs=[]):
        '''
        Transforms a list of vision objects
        @param objs: List of vision objects
        @return: List of transformed vision objects
        '''
        for obj in objs:
            obj['center'] = self.transformatePoint( array(obj['center']) )
        
    def _showImage(self):
        '''
        Shows image
        '''
        self._updateScene(self.__gview, self.__scene, self.__imgScene, convert=False, keepRatio=True)
        self._updateScene(self.__gviewTh, self.__sceneTh, self.__imgSceneTh, convert=True, keepRatio=True)
        