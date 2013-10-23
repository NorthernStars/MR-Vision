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
from mrLib.networking.data import mrVisionData

class Recognition(object):
    '''
    classdocs
    '''
    __gui = GuiLoader()
    __imageGrabber = ImageGrabber()
    
    __img = None
    __imgScene = None
    __imgCounter = 0
    
    __isRecognizing = False
    __objs = []
    
    __sceneImgTimer = QTimer()

    def __init__(self, gui=None, imageGrabber=None):
        '''
        Constructor
        '''        
        self.__gui = GuiLoader()
        self.__imageGrabber = ImageGrabber()
        self.__isRecognizing = False        
        
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
        self.__gview = self.__gui.getObj("imgRecognition")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        # create listeners
        self.__gui.connect( "cmdStartRecognition", "clicked()", self.startRecognition )
        self.__gui.connect( "cmdStopRecognition", "clicked()", self.stopRecognition )
        
        # start timer
        self.__sceneImgTimer = QTimer()
        self.__sceneImgTimer.timeout.connect( self.__showImage )
        self.__sceneImgTimer.start(100)
        
        
    def setImg(self, img=None):
        '''
        Sets current image
        '''
        self.__img = img
        self.__imgCounter += 1
        self.__imgScene = img
        
    def startRecognition(self):
        '''
        Starts image recognition   
        '''
        self.__isRecognizing = True
        start_new_thread( self.__recognize, () )
    
    def stopRecognition(self):
        '''
        Starts image recognition   
        '''
        self.__isRecognizing = False
        
    def isRecognizing(self):
        '''
        @return: True if module is currently recognizing images
        '''
        return self.__isRecognizing
    
    def getVisionObjects(self):
        '''
        @return: List of recognized vision objects
        '''
        return self.__objs
    
    def recognize(self, img=None, mode=mrVisionData.VISION_MODE_STREAM_ALL):
        '''
        Recognizes objects in image
        @param img: Image to analyse
        @param mode: Mode of recognition (what kind of objects)
        @return: list of recognized vision objects
        '''
        retObjs = []
        
        if img != None:
            pass
        
        return retObjs
    
    
    def __recognize(self):
        '''
        Recognizes objects in current image
        Run in background
        '''
        lastImg = self.__imgCounter
        while self.__isRecognizing:
            if self.__imgCounter != lastImg:
                self.__isRecognizing = True
                img = self.__img
                
                '''
                ------------------------------------------------------------
                                PUT ALGORITHM HERE
                ------------------------------------------------------------
                '''
                print "recognizing..."
                
                self.__isRecognizing = False
    
        
    def __showImage(self):
        '''
        Shows image
        '''
        if self.__imgScene != None:
            self.__scene.clear()
            self.__scene.addPixmap( imageToPixmap(self.__imgScene) )
            self.__gview.fitInView( self.__scene.sceneRect(), Qt.KeepAspectRatio )
            self.__gview.show()
        