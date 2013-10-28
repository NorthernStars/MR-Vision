'''
Created on 11.09.2013

@author: hannes
'''
from mrLib.config.mrConfigParser import mrConfigParser
from mrLib.networking.mrSocketManager import mrSocketManager
from mrLib.networking.data import mrVisionData
from mrLib.networking.data import mrDataTags
from mrLib.logging import mrLogger

from time import time, sleep
from thread import start_new_thread
from subprocess import call
from gui.GuiLoader import GuiLoader
from core.ImageGrabber import ImageGrabber
from core.Distortion import Distortion
from core.Transformation import Transformation
from core.Recognition import Recognition




class mrVisionModule(object):
    '''
    classdocs
    '''
    __visionConfig = mrConfigParser()
    __visionHostName = "vision"
    __visionCalibImg = "img/calibration.jpg"
    __gui = GuiLoader()
    
    __imageGrabber = ImageGrabber()
    __distortion = Distortion()
    __transformation = Transformation()
    __recognition = Recognition()
    
    __socketManager = None
    __mode = mrVisionData.VISION_MODE_CALIBRATE_DIST
    __connectionTimeout = 30.0

    def __init__(self, config=None, guiloader=None):
        '''
        Constructor
        '''
        
        # check for config
        if type(config) == mrConfigParser:
            self.__visionConfig = config
            self.__visionHostName = config.getConfigValue("PROTOCOl", "visionHostname")
            self.__visionCalibImg = config.getConfigValue("GENERAL", "calibrationImg")
            self.__connectionTimeout = config.getConfigValueFloat("NETWORK", "timeout")
        else:
            mrLogger.log( "No configuration specified", mrLogger.LOG_LEVEL['info'] ) 
        
        # load network interface
        #ret = self.__initNetworkInterface()
        ret = True
        
        # start image processing
        if ret:
            start_new_thread( self.__processImage, () )
            pass
        
        # start gui
        if guiloader != None:
            self.__gui = guiloader 
            self.__imageGrabber = ImageGrabber(self.__gui)
            self.__distortion = Distortion(self.__gui, self.__imageGrabber)
            self.__transformation = Transformation(self.__gui, self.__imageGrabber)
            self.__recognition = Recognition(self.__gui, self.__imageGrabber)
            
            self.__initGui()
            
    def __initGui(self):
        '''
        Initiates gui
        '''
        self.__gui.connect( "cmdCoriander", "clicked()", self.__startCoriander )
        
    def __initNetworkInterface(self):
        '''
        Initiates network interface
        '''
        host = self.__visionConfig.getConfigValue("NETWORK", "serverIP")
        port = self.__visionConfig.getConfigValueInt("NETWORK", "serverPort")
        self.__socketManager = mrSocketManager(host, port)
        self.__socketManager.addOnDataRecievedListener( self.__dataRecieved )
        
        mrLogger.log( "vision module trying to connect to gameserver", mrLogger.LOG_LEVEL['info'] )
        
        # wait for connection
        t1 = time()
        while (time()-t1) < self.__connectionTimeout and not self.__socketManager.isConnected():
            pass
        
        if self.__socketManager.isConnected():
            # send request data
            data = self.__createProtocolData()
            data.addDataItem( mrDataTags.PROTOCOL_VERSION_TAG, self.__visionConfig.getConfigValueInt("PROTOCOL", "protocolVersion") )
            self.__socketManager.sendData(data)
            
            mrLogger.log( "vision module started", mrLogger.LOG_LEVEL['info'] )
            
        else:
            msg = "Vision module could not connect to game server " + str(host)
            msg += " on port " + str(port)
            mrLogger.log( msg, mrLogger.LOG_LEVEL['error'] )
            return False
        
        return True
    
    def __startCoriander(self):
        '''
        Starts external program coriander
        '''
        self.__imageGrabber.stopVideo()
        start_new_thread(call, ("coriander",))          
        
        
    def __dataRecieved(self, socket, data):
        '''
        Data recieved listener
        '''
        mode = data.getDataItem( self.__visionModeTag )
        if mode != None:
            self.__mode = mode
            mrLogger.log( "vision module new mode: " + str(mode), mrLogger.LOG_LEVEL['debug'] )
    
            
    def __sendVisionData(self, visionObjects=[[],[]]):
        '''
        Sends list of recognized objects
        @param visionObjects: Twoi dimensional list with
        visionObjects[0] as list of bots
        visionObjects[1] as list of objects  
        '''
        if self.__socketManager.isConnected() and len(visionObjects) == 2:
            # send bots
            for bot in visionObjects[0]:
#                 data = self.__createProtocolData(mrProtocol.PROTOCOL_TYPE_VISIONBOTS)
                print bot
            
            # send objects
            for obj in visionObjects[1]:
#                 data = self.__createProtocolData(mrProtocol.PROTOCOL_TYPE_VISIONOBJECTS)
                print obj
                
                
                
    def __processImage(self):
        '''
        processes image recognision
        '''
        
        
        mrLogger.log( "image processing started", mrLogger.LOG_LEVEL['info'] )
        while self.__mode != mrVisionData.VISION_MODE_TERMINATE:
            
            # get image
            img = self.__imageGrabber.getImage()
            
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
                # TO-DO: image processing
                if self.__imageGrabber.isActive():
                    objs = self.__recognition.getVisionObjects()
                    print "objects:", objs
            
            # CALIBRATE CHESSBOARD
            elif self.__mode == mrVisionData.VISION_MODE_CALIBRATE_DIST:
                if not self.__distortion.isCalibrating():                              
                    self.__distortion.calibrateCamera()                   
                    while self.__distortion.isCalibrating():
                        pass
                    
                self.__mode = mrVisionData.VISION_MODE_NONE
            
            # CALIBRATE TRANSFORMATIONEN
            elif self.__mode == mrVisionData.VISION_MODE_CALIBRATE_TRANSF:
                # To-DO: calibration of transformation
                if not self.__transformation.isCalibrating():
                    self.__transformation.startCalibration()
                while self.__transformation.isCalibrating():
                    pass
                
                self.__mode = mrVisionData.VISION_MODE_NONE
                
            sleep(0.5)
            
        # exit program
        mrLogger.log( "image processing stopped", mrLogger.LOG_LEVEL['info'] )
        self.__socketManager.stopSocket()
        exit()