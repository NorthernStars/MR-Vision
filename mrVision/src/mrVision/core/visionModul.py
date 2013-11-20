'''
Created on 16.11.2013

@author: northernstars
'''
from gui.GuiLoader import GuiLoader
from core.modules.ImageGrabber import ImageGrabber
from imageLibs.imageprocessing import imageToPixmap

from mrLib.config.mrConfigParser import mrConfigParser

from cv2 import cvtColor, COLOR_GRAY2RGB
from PyQt4.QtCore import Qt

from copy import copy

class visionModule(object):
    '''
    classdocs
    '''    
    _config = mrConfigParser()
    _gui = GuiLoader()
    _imageGrabber = ImageGrabber()
    _img = None
    _imgCounter = 0


    def __init__(self, gui=None, imageGrabber=None, config=None):
        '''
        Constructor
        '''
        self._img = None
        self._imgCounter = 0
        
        self._gui = gui
        self._config = config
        self._imageGrabber = imageGrabber
    
    def setImg(self, img=None):
        '''
        Sets current image
        '''
        if img != None:
            self._img = img
            self._imgCounter += 1
    
    def _showImage(self):
        '''
        Shows image
        '''
        pass
            
    def _updateScene(self, gview, scene, img, convert=False, keepRatio=True):
        '''
        Updates scene
        '''
        img = copy(img)
        if img != None and scene != None and gview != None:
            # convert image to rgb
            if convert:
                img = cvtColor( img, COLOR_GRAY2RGB)
            
            # clear scene and add image pixmap
            scene.clear()
            scene.addPixmap( imageToPixmap(img) )
            
            # fit image into scene
            if keepRatio:
                gview.fitInView( scene.sceneRect(), Qt.KeepAspectRatio )
            else:
                gview.fitInView( scene.sceneRect() )
                
            # show scene
            gview.show()