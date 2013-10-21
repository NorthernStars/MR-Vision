'''
Created on 21.10.2013

@author: northernstars
'''
from gui.GuiLoader import GuiLoader
from core.imageprocessing import findChessBoardPatternSize, imageToPixmap

from thread import start_new_thread
from PyQt4.QtGui import QGraphicsScene

class Distortion(object):
    '''
    classdocs
    '''
    __gui = GuiLoader()
    __pattern = (3,3)
    __img = None
    __imgCounter = 0
    
    __scene = None
    __gview = None


    def __init__(self, gui=None):
        '''
        Constructor
        '''        
        if gui != None:
            self.__gui = gui
            self.__initGui()
        
    def __initGui(self):
        '''
        Initiates gui
        '''
        # initiate scene
        self.__gview = self.__gui.getObj("imgDistortion")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        # create listeners
        self.__gui.connect( "cmdFindPattern", "clicked()", self.findChessBoardPattern )
        self.__gui.connect( "cmdCalibrateDistortion", "clicked()", self.calibrateCamera )        
        
        
    def setImg(self, img=None):
        '''
        Sets current image
        '''
        self.__img = img
        self.__imgCounter += 1
    
    def findChessBoardPattern(self):
        '''
        Finds maximum chessboard pattern
        '''        
        # show message
        self.__scene.clear()
        self.__scene.addSimpleText("Searching pattern...\nThis will take a while")
        self.__gview.show()
        
        # start search
        start_new_thread( self.__searchChessBoardPattern, () )
        
    def __searchChessBoardPattern(self):
        '''
        Searches for chessboard pattern
        (start in background)
        '''
        txt = "No pattern found"
        
        # get start and max values
        xStart = int( str( self.__gui.getObj("txtPatternXMin").text() ) )
        yStart =  int( str( self.__gui.getObj("txtPatternYMin").text() ) )
        xMax =  int( str( self.__gui.getObj("txtPatternXMax").text() ) )
        yMax =  int( str( self.__gui.getObj("txtPatternYMax").text() ) )
        
        # find pattern
        if self.__img != None:
            pattern = findChessBoardPatternSize(self.__img, xMax, yMax, xStart, yStart)
        
            print "pattern", pattern
        
            if pattern != None and len(pattern) > 0:
                self.__pattern = pattern[-1]
                
                # set pattern
                if len(self.__pattern) == 2:
                    self.__gui.getObj("txtPatternX").setText( str(self.__pattern[0]) )
                    self.__gui.getObj("txtPatternY").setText( str(self.__pattern[1]) )
                    txt = "Found: (" + str(self.__pattern[0]) + "," + str(self.__pattern[1]) + ")"
                else:
                    self.__pattern = (3,3)
        
        # show result
        self.__scene.clear()
        self.__scene.addSimpleText(txt)
        self.__gview.show()
    
    def calibrateCamera(self):
        '''
        Calibrates camera
        '''
        pass
    
    def undistortImage(self):
        '''
        Undistorts image
        @return: Image
        '''
        pass