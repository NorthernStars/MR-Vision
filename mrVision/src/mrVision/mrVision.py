'''
Created on 11.09.2013

Mixed-Reality Vision module

@author: hannes
'''

from mrLib.config.mrConfigParser import mrConfigParser
from mrLib.logging import mrLogger
from core.mrVisionModule import mrVisionModule
from gui.GuiLoader import GuiLoader

from PyQt4 import QtGui
import os, sys


if __name__ == '__main__':
    
    ''' set current working path '''
    path = os.path.dirname(sys.argv[0])
    if not path:
        path = str(os.getcwd())
        sys.argv[0] = path + "/" + str(sys.argv[0])        
    os.chdir(path)
    
    # read config
    config = mrConfigParser("../config.ini")
    
    logLevel = config.getConfigValue("GENERAL", "logLevel")
    mrLogger.logClear()
    try:
        mrLogger.LOGGER_LOG_LEVEL = mrLogger.LOG_LEVEL[logLevel]
    except:
        pass
    
    # create gui app
    app = QtGui.QApplication(sys.argv)
    guiloader = GuiLoader(True)
    guiloader.show()
    
    # create vision module
    visionModule = mrVisionModule( config, guiloader )
    
    # show gui
    app.exec_()