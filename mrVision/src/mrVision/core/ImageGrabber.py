'''
Created on 21.10.2013

@author: northernstars
'''
from gui.GuiLoader import GuiLoader
from sources.AbstractSourceGrabber import AbstractSourceGrabber
from sources.CamGrabber import CamGrabber
from sources.FileGrabber import FileGrabber
from core.imageprocessing import imageToPixmap

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer
from cv2 import cvtColor, COLOR_BGR2RGB, COLOR_GRAY2RGB, COLOR_HLS2RGB, COLOR_YUV2RGB  # @UnusedImport
from numpy import ndarray


class ImageGrabber(object):
    '''
    classdocs
    '''
    __gui = GuiLoader()
    __sources = []
    __grabTimer = QTimer()
    __img = None
    
    __scene = None
    __gview = None
    

    def __init__(self, gui=None):
        '''
        Constructor
        '''
        self.__gui = GuiLoader()
        
        if gui != None:
            self.__gui = gui
            self.__initGui()
            
            

            
    def __initGui(self):
        '''
        Initiates gui listeners
        '''
        # initiate scene
        self.__gview = self.__gui.getObj("imgVideo")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        # add combobox items
        cmb = self.__gui.getObj("cmbConversion")
        cmb.addItem("None")
        cmb.addItem("COLOR_BGR2RGB")
        cmb.addItem("COLOR_GRAY2RGB")
        cmb.addItem("COLOR_YUV2RGB")
        cmb.addItem("COLOR_HLS2RGB")
        
        # add listeners
        self.__gui.connect( "cmdStartVideo", "clicked()", self.startVideo )
        self.__gui.connect( "cmdStopVideo", "clicked()", self.stopVideo )
        self.__gui.connect( "cmdAddSource", "clicked()", self.__addCamSource )
        
    def startVideo(self):
        '''
        Starts grabbing images
        '''
        self.__grabTimer = QTimer()
        self.__grabTimer.timeout.connect( self.__grabImage )
        self.__grabTimer.start(0)
    
    def stopVideo(self):
        '''
        Stops grabbing video
        '''
        self.__grabTimer.stop()
        self.__scene.clear()
        self.__gview.show()
    
    def getImage(self):
        '''
        Returns the last grabbed image
        @return: Image
        '''
        return self.__img
    
    def __grabImage(self):
        '''
        Graps image from sources
        '''        
        images = []
        
        # grab all images
        for src in self.__sources:
            assert isinstance(src, AbstractSourceGrabber)
            images.append( src.getImg() )
        
        # join and convert images
        img = self.__joinImages(images)
        
        # convert image
        convert = eval( str(self.__gui.getObj("cmbConversion").currentText()) )
        if convert != None:
            try:
                img = cvtColor(img, convert)
            except:
                img = None
        
        # clear scene
        self.__scene.clear()
        
        if type(img) == ndarray:
            # add image as new image
            self.__img = img           
            
            # show image
            self.__scene.addPixmap( imageToPixmap(img) )
            self.__gview.show()
            
        else:
            # show message
            self.__scene.addText("NO VIDEO")
        
            
    
    def __joinImages(self, images=[]):
        '''
        Joins images
        '''
        # TO-DO: Joining images
        if len(images) > 0:
            return images[0]
        return False 
    
    def __addCamSource(self):
        '''
        Adds camera as source
        '''
        obj = self.__gui.getObj("txtSource")
        source = int( obj.text() )
        
        cam = CamGrabber(source)
        self.__sources.append( cam )
    
    def __addFileSource(self):
        '''
        Adds file as source
        '''
        obj = self.__gui.getObj("txtSource")
        source = str( obj.text() )
        
        self.__sources.append( FileGrabber(source) )