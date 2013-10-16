'''
Created on 11.09.2013

@author: hannes
'''
from mrLib.config.mrConfigParser import mrConfigParser
from mrLib.networking.mrSocketManager import mrSocketManager
from mrLib.networking import mrProtocol
from mrLib.networking.data import mrVisionData
from mrLib.networking.data import mrDataTags
from mrLib.logging import mrLogger

from time import time, sleep
from thread import start_new_thread
from gui.GuiLoader import GuiLoader




class mrVisionModule(object):
    '''
    classdocs
    '''
    __visionConfig = mrConfigParser()
    __visionHostName = "vision"
    __visionCalibImg = "img/calibration.jpg"
    __gui = GuiLoader(True)
    
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
        
        # start gui
        if guiloader != None:
            self.__gui = guiloader 
        
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
        
    def __createProtocolData(self, dataType=mrProtocol.PROTOCOL_TYPE_GAMEDATA):
        '''
        Generates protocol data package
        @param dataType: mrProtocol.PROTOCOL_TYPE_* data type
        '''
        return mrProtocol.mrProtocolData( dataType, self.__visionHostName )            
        
        
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
            
            if self.__mode in mrVisionData.VISION_STREAMING_MODES:
                # TO-DO: image processing
                print "objects:"
            
            elif self.__mode == mrVisionData.VISION_MODE_CALIBRATE_DIST:
                # TO-DO: calibration  of distortion
                print "calibration distortion"
            
            elif self.__mode == mrVisionData.VISION_MODE_CALIBRATE_TRANSF:
                # To-DO: calibration of transformation
                print "calibration transformation"
                
            elif self.__mode == mrVisionData.VISION_MODE_CALIBRATE_BG:
                # To-DO: calibration of background
                print "calibration background"
                
            sleep(1.0)
            
        # exit program
        mrLogger.log( "image processing stopped", mrLogger.LOG_LEVEL['info'] )
        self.__socketManager.stopSocket()
        exit()