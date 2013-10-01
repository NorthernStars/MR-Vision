'''
Created on 11.09.2013

Mixed-Reality Vision module

@author: hannes
'''

from mrLib.config.mrConfigParser import mrConfigParser
from mrLib.logging import mrLogger
from core import mrVisionModule


if __name__ == '__main__':
    
    
    config = mrConfigParser("../config.ini")
    
    logLevel = config.getConfigValue("GENERAL", "logLevel")
    mrLogger.logClear()
    try:
        mrLogger.LOGGER_LOG_LEVEL = mrLogger.LOG_LEVEL[logLevel]
    except:
        pass
    
    visionModule = mrVisionModule.mrVisionModule( config )