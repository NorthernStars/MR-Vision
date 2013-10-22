'''
Created on 21.10.2013

@author: northernstars
'''
from gui.GuiLoader import GuiLoader
from core.imageprocessing import findChessBoardPatternSize, imageToPixmap, getChessBoardCorners
from core.imageprocessing import getCalibrationData, undistortImg, getImageSizeFromCorners

from numpy import float32, zeros, indices, prod
from cv2 import drawChessboardCorners, cvtColor, COLOR_BGR2RGB

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer, Qt
from thread import start_new_thread




class Distortion(object):
    '''
    classdocs
    '''
    __gui = GuiLoader()
    __img = None
    __imgScene = None
    __imgCounter = 0
    
    __scene = None
    __gview = None
    __sceneImgTimer = None
    
    __camera_matrix = None
    __dist_coefs = None
    __corners = None
    
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
        self.__gview = self.__gui.getObj("imgDistortion")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        # create listeners
        self.__gui.connect( "cmdFindPattern", "clicked()", self.findChessBoardPattern )
        self.__gui.connect( "cmdCalibrateDistortion", "clicked()", self.calibrateCamera )  
        
        # start timer
        self.__sceneImgTimer = QTimer()
        self.__sceneImgTimer.timeout.connect( self.__showImage )
        self.__sceneImgTimer.start(200)  


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
    
    def findChessBoardPattern(self):
        '''
        Finds maximum chessboard pattern
        '''        
        # show message
        self.__imgScene = None
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
        
        # get start and max values
        xStart = int( str( self.__gui.getObj("txtPatternXMin").text() ) )
        yStart =  int( str( self.__gui.getObj("txtPatternYMin").text() ) )
        xMax =  int( str( self.__gui.getObj("txtPatternXMax").text() ) )
        yMax =  int( str( self.__gui.getObj("txtPatternYMax").text() ) )
        
        # find pattern
        if self.__img != None:
            pattern = findChessBoardPatternSize(self.__img, xMax, yMax, xStart, yStart)
        
            if pattern != None and len(pattern) > 0:                
                # set pattern
                if len(pattern) == 2:
                    self.__gui.getObj("txtPatternX").setText( str(pattern[0]) )
                    self.__gui.getObj("txtPatternY").setText( str(pattern[1]) )
    
    def calibrateCamera(self):
        '''
        Calibrates camera
        '''
        start_new_thread(self.__calibrate, ())
        
        
    def __calibrate(self):
        '''
        Calibrates camera
        (run in background)
        '''
        # check for correct image        
        if self.__img != None:
            self.__calibrating = True
            self.__gui.status("Calibrating ...")
                  
            # get values
            x = int(str( self.__gui.getObj("txtPatternX").text() ))
            y = int(str( self.__gui.getObj("txtPatternY").text() ))
            n = int(str( self.__gui.getObj("txtCalibrationFrames").text() ))
            square_size = float(str( self.__gui.getObj("txtCalibrationSquareSize").text() ))
            
            # calculate distortion
            pattern_size = (x, y)
            ret = self.__calibrateCorners(pattern_size, n, square_size)
            
            if ret != None:
                camera_matrix, dist_coefs = ret
                self.__camera_matrix, self.__dist_coefs = camera_matrix, dist_coefs
            
            # undistort image
            img = self.undistortImage(self.__img)
            self.__imgScene = img
            
            self.__gui.status("Searching for boders to crop image ...")
            
            # get corners
            if ret != None:
                found = False
                frames = 0;
                tries = 0;
                while not found and frames < n and tries < 10:
                    img = self.undistortImage(self.__img)
                    found, corners = getChessBoardCorners( img, pattern_size )
                    if found:
                        frames += 1
                    tries += 1
                
                # crop image
                if found:
                    self.__corners = getImageSizeFromCorners(corners)        
                    self.__imgScene = self.cropImage(img)
                    
                self.__calibrated = True    
            
        # set calibration flag
        self.__gui.status("Calibration finished.")
                   
        
        self.__calibrating = False 
        
        
    def __calibrateCorners(self, pattern_size, n, square_size):
        '''
        Calibrates corners of chessboard
        @return: camera_matrix, dist_coefs
        '''
        pattern_points = zeros( (prod(pattern_size), 3), float32 )
        pattern_points[:,:2] = indices(pattern_size).T.reshape(-1, 2)
        pattern_points *= square_size

        obj_points = []
        img_points = []        
        frames = 0;
        tries = 0
        lastCount = self.__imgCounter;
        
        # detect pattern
        while frames < n and tries < 10:
            img = self.__img
            
            if lastCount != self.__imgCounter:
                # get corners                
                found, corners = getChessBoardCorners( img, pattern_size )
                
                # check if corners found
                if found:
                    frames += 1
                    
                    # get more detailed points and add them to list
                    img_points.append( corners.reshape(-1, 2) )
                    obj_points.append( pattern_points )
                    
                    # draw corners
                    drawChessboardCorners( img, pattern_size, corners, found )
                    self.__imgScene = img
                    tries = 0
                tries += 1
                    
        # get cmera values
        if img != None and len(obj_points) > 0 and len(img_points) > 0:
            return getCalibrationData(img, obj_points, img_points )
    
    def cropImage(self, img=None):
        '''
        Crops image if corners available
        @return: croped Image
        '''
        borders = int(str( self.__gui.getObj("txtCalibrationBorders").text() )) / 100.0
        
        if self.__corners != None and img != None and self.__gui.getObj("chkCropImg").isChecked():
            xmin = int(self.__corners[0][0])
            xmax = int(self.__corners[0][1])
            ymin = int(self.__corners[1][0])
            ymax = int(self.__corners[1][1])
            
            borderX = int(img.shape[1] * borders)
            borderY = int(img.shape[0] * borders)
            
            # check new borders
            if xmin-borderX > 0:
                xmin = xmin-borderX
            else:
                xmin = 0    
                             
            if ymin-borderY > 0:
                ymin = ymin-borderY
            else:
                ymin = 0    
                             
            if xmax+borderX <= img.shape[1]:
                xmax = xmax+borderX
            else:
                xmax = img.shape[1]-1 
                                
            if ymax+borderY <= img.shape[0]:
                ymax = ymax+borderY
            else:
                ymax = img.shape[0]-1
            
            # conversion before
            if self.__gui.getObj("chkCropConvBefore").isChecked():
                img = cvtColor( img, COLOR_BGR2RGB )
                
            # crop image
            img = img[ymin:ymax, xmin:xmax]
            
            # conversion after
            img = cvtColor( img, COLOR_BGR2RGB )
        
        return img
    
    def __showImage(self):
        '''
        Shows image
        '''
        if self.__imgScene != None:
            self.__scene.clear()
            self.__scene.addPixmap( imageToPixmap(self.__imgScene) )
            self.__gview.fitInView( self.__scene.sceneRect(), Qt.KeepAspectRatio )
            self.__gview.show()
    
    def undistortImage(self, img=None):
        '''
        Undistorts image
        @return: Image
        '''
        if self.__camera_matrix != None and self.__dist_coefs != None and img != None:
            return undistortImg( img, self.__camera_matrix, self.__dist_coefs )
        return img
            