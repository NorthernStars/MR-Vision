'''
Created on 22.10.2013

@author: northernstars
'''
from gui.GuiLoader import GuiLoader
from core.ImageGrabber import ImageGrabber
from core.imageprocessing import imageToPixmap

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer, Qt
from thread import start_new_thread

from cv2 import cvtColor, COLOR_RGB2GRAY, THRESH_BINARY, medianBlur, threshold, imshow, waitKey, destroyAllWindows, HoughCircles, circle, line
from cv2.cv import CV_HOUGH_GRADIENT
from numpy import array, around, argsort, int16, size, mean
from numpy.linalg import solve

class Transformation(object):
    '''
    classdocs
    '''
    __gui = GuiLoader()
    __imageGrabber = ImageGrabber()
    
    __img = None
    __imgScene = None
    __imgCounter = 0
    
    __calibrated = False
    __calibrating = False
    
    __basisMatrix = array([[1,0],[0,1]])
    __offset = array([0,0])

    def __init__(self, gui=None, imageGrabber=None):
        '''
        Constructor
        '''        
        self.__gui = GuiLoader()
        self.__imageGrabber = ImageGrabber()        
        self.__calibrated = False
        self.__calibrating = False
        self.__basisMatrix = array([[1,0],[0,1]])
        self.__offset = array([0,0])
        
        if gui != None:
            self.__gui = gui
            self.__initGui()
            
        if imageGrabber != None:
            self.__imageGrabber = imageGrabber
        
    def __initGui(self):
        '''
        Initiates gui
        '''
        # initiate scene
        self.__gview = self.__gui.getObj("imgTransformation")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        # create listeners
        self.__gui.connect( "cmdCalibrateTransformation", "clicked()", self.__calibrateTransformation )
        
        # start timer
        self.__sceneImgTimer = QTimer()
        self.__sceneImgTimer.timeout.connect( self.__showImage )
        self.__sceneImgTimer.start(100)  
        
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
        
        
    def setImg(self, img=None):
        '''
        Sets current image
        '''
        self.__img = img
        self.__imgCounter += 1
        
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
        if self.__img == None:
            return
        
        self.__gui.status("Calibrating transformation...")
        self.__calibrating = True
        img = self.__img
        
        '''
        ------------------------------------------------------------
                        PUT ALGORITHM HERE
        ------------------------------------------------------------
        '''
        '''
        Preprocessing image: 
        '''
        # blur image for better result
        gimg = cvtColor(img, COLOR_RGB2GRAY)
        gimg = medianBlur(gimg,5)
        
        # create binary image
        gimg = threshold(gimg,115,255,THRESH_BINARY)[1]
        
        '''
        Searching for circles by using Hough-Transformation:
        Parameters used here are chosen arbitrarily!
        '''
        circles = HoughCircles(gimg, CV_HOUGH_GRADIENT, 1, 10, param1=100, param2=12, minRadius=9, maxRadius=35)
        circles = around(circles).astype(int16)
        centers = circles[0][:,:3]
        
        '''
        Identifying corners of playing field by evaluating centers of circles:
        Existence of 4 points are mandatory!
        '''
        vlnr = argsort(centers[:,0],)
        
        pts_links = centers[vlnr[:2],:]
        pts_rechts = centers[vlnr[2:],:]
        
        # defining points for coordinate system
        # left:
        p00 = pts_links[argsort(pts_links[:,1])[0],:]
        p01 = pts_links[argsort(pts_links[:,1])[1],:]
        # right:
        p10 = pts_rechts[argsort(pts_rechts[:,0])[0],:]
        p11 = pts_rechts[argsort(pts_rechts[:,0])[1],:]
        
        
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
        
        self.__calibrating = False
        self.__gui.status("Calibration finished.")
        
        pass
    
    def transformatePoint(self, point=array([0,0])):
        '''
        Transformates a point into local coordinates space
        @param point: Tuple (x,y) of points coordinates to transform
        @return: Tuple (x,y) of transformed coordinates
        '''
        
        A = self.__basisMatrix
        O = self.__offset
        
        # Bilde Referenz zum Ursprung des Koordinatensystems
        b = point - O
        transformation = solve(A,b)
        
        return transformation
    
    def transformObjects(self, objs=[]):
        '''
        Transforms a list of vision objects
        @param objs: List of vision objects
        @return: List of transformed vision objects
        '''
        retObjs = []
        for obj in objs:
            print obj
            
        return retObjs
        
    def __showImage(self):
        '''
        Shows image
        '''
        if self.__imgScene != None:
            self.__scene.clear()
            self.__scene.addPixmap( imageToPixmap(self.__imgScene) )
            self.__gview.fitInView( self.__scene.sceneRect(), Qt.KeepAspectRatio )
            self.__gview.show()
        