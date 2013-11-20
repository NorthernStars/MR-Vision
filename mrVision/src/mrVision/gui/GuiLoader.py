# -*- coding: utf-8 -*-
'''
Created on 08.10.2012

@author: Hannes Eilers
@organization: Rexxon GmbH - Kiel
@copyright: Rexxon GmbH 2012
'''
import os

from PyQt4.QtCore import QObject, SIGNAL, QTimer
from PyQt4.QtGui import QMainWindow, QWidget, QFileDialog
from visionGui import Ui_frmMain

class GuiLoader(QMainWindow):
    '''
    Class for loading gui
    '''
    msgTypes = {
                'INFO':0,
                'ERROR':1,
                'WARNING':2
                } 
    
    dialogTypes = {
                   'FileOpen': 0,
                   'FileSave': 1
                   }
    
    dialogOptionsDef = {
                        'type':dialogTypes['FileOpen'],
                        'filetypes':'JS Config Files (*.JS *.js)',
                        'title':'Open File',
                        'path':os.getcwd()
                        }
    ui = None
    
    eDefinitions = {
                    'status': ['lblStatus']
                    }
    
    __statusTimer = QTimer()
    __statusMsg = []


    def __init__(self, parent=None):
        '''
        Constructor
        @param parent: Not needed yet
        '''
        self.__statusMsg = []
        # create gui
        if parent != None:
            self.ui = Ui_frmMain()
            self.showInterface()
    
    
    
    def showInterface(self, parent=None):
        '''
        Displays athe graphical interface.
        @param parent: Not needed yet
        '''
        
        # create gui
        super(GuiLoader, self).__init__()
        widget = QWidget(self)
        self.ui.setupUi(widget)
        self.setCentralWidget(widget)
        
        # start status timer
        self.__statusTimer = QTimer()
        self.__statusTimer.timeout.connect( self.__status )
        self.__statusTimer.start(100)
        
    
    def callFunction(self, obj, function, args=[]):
        '''
        Calls a function of an ui object
        
        @param obj: Name of the object
        @param function: Name of the function to call
        @param args: Array of arguments to pass to the function (optional)
        
        @return: returned value of the called function
        '''
        
        # generate function call
        cmd = "self.ui." + str(obj) + "." + str(function) + "("
        
        # add arguments to function call
        for arg in args:
            # check if value is a string
            if type(arg) == str:
                arg = "'" + arg + "'"
            cmd += str(arg) + ","
            
        # remove last comma
        if cmd[ len(cmd)-1 ] == ",": 
            cmd = cmd[0 : len(cmd)-1]
        cmd += ")"
        
        # call fucntion and return returned value
        try:
            return eval( cmd )
        except:
            print "error by evaluating command:\n" + cmd
            return None
    
    def getObj(self, obj):
        '''
        Returns a pyqt object
        
        @param obj: Name of the object
        @return: PyQT Object or None if not found
        '''
        cmd = "self.ui." + str(obj)
        return eval(cmd) 
    
    def connect(self, obj=None, event='', callback=None):
        '''
        Connects a event of an object to a callback function
        
        @param obj: Name of the object
        @param event: Name of the event
        @param callback: Function to call on event
        '''
        obj = 'self.ui.' + str(obj)
        try:
            obj = eval(obj)
            QObject.connect(obj, SIGNAL(str(event)), callback)
        except:
            print "ERROR: Could not connect object " + str(obj)
            
    def disconnect(self, obj=None, event='', callback=None):
        '''
        Disconnects all callbacks from object
        
        @param obj: Name of the object
        @param event: Name of the event
        @param callback: Function to call on event
        '''
        obj = 'self.ui.' + str(obj)
        try:
            obj = eval(obj)
            QObject.disconnect(obj, SIGNAL(str(event)), callback)
        except:
            print "ERROR: Could not disconnect signals from object " + str(obj)
    
    def __status(self):
        '''
        Displays a message at the status labels
        
        @param msg: Message to display
        @param msgType: Type of msgTypes[] value for message-type (optional, default= msgTypes['INFO'])
        '''
        start = '<span>'
        end = '</span>'
        sTyp = "INFO"
        
        for msg in self.__statusMsg:
            # check for message type
            if msg[1] == self.msgTypes['ERROR']:
                start = '<span style="color: red">'
                sTyp = "ERROR" 
            elif msg[1] == self.msgTypes['WARNING']:
                start = '<span style="color: orange">'
                sTyp = "WARNING"
            
            # set status labels
            for obj in self.eDefinitions['status']:
                value = start + str(msg[0]) + end
                self.callFunction(obj, 'setText', [str(value)])
            
            # print on console
            if len(self.__statusMsg) >0:
                print sTyp, ":", msg[0]
            
        # remove messages
        self.__statusMsg = []
            
            
    def status(self, msg='', msgType=msgTypes['INFO']):
        '''
        Displays a message at the status labels
        
        @param msg: Message to display
        @param msgType: Type of msgTypes[] value for message-type (optional, default= msgTypes['INFO'])
        '''      
        self.__statusMsg.append( [msg, msgType] )
        
    def dialog(self, options=dialogOptionsDef):
        '''
        Opens a dialog and returns its value        
        
        @param options: Dictionary of options for the dialog (optional, see dialogOptionsDef for example)
        @return: value returned by the dialog
        '''
        ret = None
        
        if options['type'] == self.dialogTypes['FileOpen']:
            ret = QFileDialog.getOpenFileName(None, options['title'], options['path'], options['filetypes'])
        elif options['type'] == self.dialogTypes['FileSave']:
            ret = QFileDialog.getSaveFileName(None, options['title'], options['path'], options['filetypes'])
        
        return ret