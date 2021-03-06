'''
Created on 11.09.2013

@author: hannes
'''
from mrLib.config.mrConfigParser import mrConfigParser
from mrLib.networking.mrSocketManager import mrSocketManager
from mrLib.networking.data import mrVisionData
from mrLib.networking.data.positiondata import positionDataPackage, positionObjectBot
from mrLib.networking.data.changevisionmodedata import CreateFromDocument, changeVisionMode
from mrLib.logging import mrLogger

from time import time, sleep
from thread import start_new_thread
from subprocess import call

from gui.GuiLoader import GuiLoader
from core.modules.ImageGrabber import ImageGrabber
from core.modules.Distortion import Distortion
from core.modules.Transformation import Transformation
from core.modules.Recognition import Recognition
from mrLib.networking.data.mrVisionData import VISION_MODE_STREAM_BOTS, VISION_MODE_STREAM_OBJ, VISION_MODE_STREAM_ALL


class mrVisionModule(object):
    '''
    classdocs
    '''
    __visionConfig = mrConfigParser()
    __visionHostName = "vision"
    __visionCalibImg = "img/calibration.jpg"
    _gui = GuiLoader()
    
    __serverName = None
    __serverNameAck = False
    
    _imageGrabber = ImageGrabber()
    __distortion = Distortion()
    __transformation = Transformation()
    __recognition = Recognition()
    
    __socketManager = None
    __mode = mrVisionData.VISION_MODE_NONE
    __connectionTimeout = 30.0
    __moduleName = None

    def __init__(self, config=None, guiloader=None):
        '''
        Constructor
        '''
        self._gui = GuiLoader()
        
        # check for config
        if type(config) == mrConfigParser:
            self.__visionConfig = config
            self.__visionHostName = self.__visionConfig.getConfigValue("PROTOCOl", "visionHostname")
            self.__visionCalibImg = self.__visionConfig.getConfigValue("GENERAL", "calibrationImg")
            self.__moduleName = self.__visionConfig.getConfigValue("GENERAL", "moduleName")
            self.__connectionTimeout = self.__visionConfig.getConfigValueFloat("NETWORK", "timeout")
        else:
            mrLogger.log( "No configuration specified", mrLogger.LOG_LEVEL['info'] ) 
        
        # load network interface
        self.__initNetworkInterface()
        
        # start image processing
        start_new_thread( self.__processImage, () )
        
        # start gui
        if guiloader != None:
            self._gui = guiloader 
            self._imageGrabber = ImageGrabber(self._gui, self.__visionConfig)
            self.__distortion = Distortion(self._gui, self._imageGrabber, self.__visionConfig)
            self.__transformation = Transformation(self._gui, self._imageGrabber, self.__visionConfig)
            self.__recognition = Recognition(self._gui, self._imageGrabber, self.__visionConfig)
            
            self.__initGui()
            
    def __initGui(self):
        '''
        Initiates gui
        '''
        self._gui.connect( "cmdCoriander", "clicked()", self.__startCoriander )
        
    def __initNetworkInterface(self):
        '''
        Initiates network interface
        '''
        host = self.__visionConfig.getConfigValue("NETWORK", "serverIP")
        port = self.__visionConfig.getConfigValueInt("NETWORK", "serverPort")
        self.__socketManager = mrSocketManager(host=host, port=port, server=True, udpOn=True, useHandshake=True, name=str(self.__moduleName))
        self.__socketManager.addOnDataRecievedListener( self.__dataRecieved )
        self.__socketManager.addOnClientAddedListener( self.__clientAdded )
        
        mrLogger.log( "Vision module trying to connect to gameserver", mrLogger.LOG_LEVEL['info'] )
        
        # wait for connection
        t1 = time()
        while (time()-t1) < self.__connectionTimeout and not self.__socketManager.isConnected():
            pass
        
        if self.__socketManager.isConnected():
            mrLogger.log( "Vision module started", mrLogger.LOG_LEVEL['info'] )
            
        else:
            msg = "Vision module could not establish connection to server at " + str(host)
            msg += " on port " + str(port)
            mrLogger.log( msg, mrLogger.LOG_LEVEL['error'] )
            return False
        
        return True
    
    def __startCoriander(self):
        '''
        Starts external program coriander
        '''
        self._imageGrabber.stopVideo()
        start_new_thread(call, ("coriander",))          
        
    def __clientAdded(self, servername, clientdata):
        '''
        Client added listener
        '''
        msg = "Client " + servername + " " + str(clientdata)
        msg += " added"
        mrLogger.log( msg, mrLogger.LOG_LEVEL['info'] )
        
    def __dataRecieved(self, socket, addr, data):
        '''
        Data recieved listener
        '''
        try:
            print "recieved:", data
            dom = CreateFromDocument(data)
            print "type:", type(dom)
            if type(dom) == changeVisionMode:
                assert isinstance(dom, changeVisionMode)
                self.__mode = str(dom.visionmode)
                
                mode = changeVisionMode()
                mode.visionmode = self.__mode
                self.__socketManager.sendData( mode.toxml("utf-8", element_name="changevisionmode") )
                self._gui.status( "Vision mode set to " + str(self.__mode) )
                mrLogger.logDebug( "Vision mode set to: " + str(self.__mode) )
                
        except:
            pass
                     
    
            
    def __sendVisionData(self, visionObjects={'bots': [], 'rectangles': []}):
        '''
        Sends list of recognized objects
        @param visionObjects: Twoi dimensional list with
        visionObjects['bots'] as list of bots
        visionObjects['rectangles'] as list of objects  
        '''
        if self.__socketManager.isConnected() and len(visionObjects) == 2:
            # create data package
            data = positionDataPackage()
            data.visionmode = self.__mode
            
            # add bots to datapackage
            if self.__mode == VISION_MODE_STREAM_BOTS or self.__mode in VISION_MODE_STREAM_ALL:
                for bot in visionObjects['bots']:
                    b = positionObjectBot()
                    b.id = bot['id']
                    print "-----------------"
                    print "bot:", bot
                    bot['center'] = ( 1-bot['center'][0], bot['center'][1] )
                    b.location.append( bot['center'][0] )
                    b.location.append( bot['center'][1] )
                    b.angle = bot['angle']
                    data.append(b)
                    print "botsend:", bot
            
            # add rectangles to datapackage
            if self.__mode == VISION_MODE_STREAM_OBJ or self.__mode in VISION_MODE_STREAM_ALL:
                for obj in visionObjects['rectangles']:
                    print obj
                    
            # send datapackage
            self.__socketManager.sendData( data.toxml("utf-8", element_name="positiondatapackage") )
                
    def __setMode(self, mode=mrVisionData.VISION_MODE_NONE):
        '''
        Sets vision mode
        @param mode: mrVisionData mode
        '''
        self.__mode = mode
                
    def __processImage(self):
        '''
        processes image recognision
        '''       
        mrLogger.logInfo( "Main loop started in mode " + str(self.__mode) )
        
        while self.__mode != mrVisionData.VISION_MODE_TERMINATE:
            #print "mode:", self.__mode
            # get image
            img = self._imageGrabber.getImage()
            
            # sets image to distortion module
            self.__distortion.setImg(img)
            
            # undistort and crop image 
            if self.__distortion.isCalibrated():
                img = self.__distortion.undistortImage(img)
                img = self.__distortion.cropImage(img)
                
            # sets image to transformation and recognition module
            self.__transformation.setImg(img)
            self.__recognition.setImg(img)
           
            
            
            # STREAM IMAGES
            if self.__mode in mrVisionData.VISION_STREAMING_MODES:
                if self._imageGrabber.isActive():
                    # recognize objects
                    self.__recognition.recognize()
                    
                    # get bots and rectangles
                    try:
                        obj = {'bots': self.__recognition.getBots(),
                           'rectangles': self.__recognition.getRectangles()}
                    except:
                        pass
                    
                    # transformate objects
                    self.__transformation.transformObjects( obj['bots'] )
                    
                    # send vision objects
                    self.__sendVisionData(obj)
            
            # CALIBRATE CHESSBOARD
            elif self.__mode == mrVisionData.VISION_MODE_CALIBRATE_DIST:
                if not self.__distortion.isCalibrating():                              
                    self.__distortion.calibrateCamera()                   
                    while self.__distortion.isCalibrating():
                        pass
                    
                self.__setMode(mrVisionData.VISION_MODE_NONE)
            
            # CALIBRATE TRANSFORMATIONEN
            elif self.__mode == mrVisionData.VISION_MODE_CALIBRATE_TRANSF:
                # To-DO: calibration of transformation
                if not self.__transformation.isCalibrating():
                    self.__transformation.startCalibration()
                while self.__transformation.isCalibrating():
                    pass
                
                self.__setMode(mrVisionData.VISION_MODE_NONE)
                
#             sleep(0.01)
            
        # exit program
        mrLogger.logInfo( "Main loop stopped" )
        self.__socketManager.stopSocket()