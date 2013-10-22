'''
Created on 22.10.2013

@author: northernstars
'''
from gui.GuiLoader import GuiLoader

from core.imageprocessing import imageToPixmap

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer, Qt
from thread import start_new_thread

class Transformation(object):
    '''
    classdocs
    '''
    __gui = GuiLoader()
    __img = None
    __imgScene = None
    __imgCounter = 0
    
    __calibrated = False
    __calibrating = False

    def __init__(self, gui=None):
        '''
        Constructor
        '''        
        self.__gui = GuiLoader()        
        self.__calibrated = False
        self.__calibrating = False
        
        if gui != None:
            self.__gui = gui
            self.__initGui()
        
    def __initGui(self):
        '''
        Initiates gui
        '''
        # initiate scene
        self.__gview = self.__gui.getObj("imgTransformation")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
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
        self.__imgScene = img
        
    def startCalibration(self):
        '''
        Starts calibration of transformation
        '''
        start_new_thread(self.__calibrateTransformation, ())
        
    def __calibrateTransformation(self):
        '''
        Calculates transformation values
        '''
        self.__gui.status("Calibrating transformation...")
        
        '''
        ------------------------------------------------------------
                        PUT ALGORITHM HERE
        ------------------------------------------------------------
        '''
        
        self.__gui.status("Calibration finished.")
        pass
    
    def transformatePoint(self, point=(0,0)):
        '''
        Transformates a point into local coordinates space
        @param point: Tuple (x,y) of points coordinates to transform
        @return: Tuple (x,y) of transformed coordinates
        '''
        pass
    
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
        