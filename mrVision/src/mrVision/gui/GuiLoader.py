# -*- coding: utf-8 -*-
'''
Created on 08.10.2012

@author: Hannes Eilers
@organization: Rexxon GmbH - Kiel
@copyright: Rexxon GmbH 2012
'''
import os

from PyQt4 import QtCore, QtGui
from src.mrVision.gui.gui import Ui_frmMain

class GuiLoader(QtGui.QMainWindow):
    '''
    classdocs
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
    ui = Ui_frmMain()
    eDefinitions = {
                      'status': ['lblAccessVarStatus', 'lblUsrStatus_2', 'lblSettingsStatus'],
                      'lang': ['cmbLangAct1', 'cmbLangAct', 'cmbLangAct2', 'cmbLangAct_2']
                      }


    def __init__(self, parent=None):
        '''
        Constructor
        @param parent: Not needed yet
        '''
        # create gui
        if parent == None:
            self.showInterface(parent)
    
    
    
    def showInterface(self, parent=None):
        '''
        Displays athe graphical interface.
        @param parent: Not needed yet
        '''
        
        # create gui
        QtGui.QWidget.__init__(self, parent)
        self.ui.setupUi(self)
        
    
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
            QtCore.QObject.connect(obj, QtCore.SIGNAL(str(event)), callback)
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
            QtCore.QObject.disconnect(obj, QtCore.SIGNAL(str(event)), callback)
        except:
            print "ERROR: Could not disconnect signals from object " + str(obj)
    
    def status(self, msg='', msgType=msgTypes['INFO']):
        '''
        Displays a message at the status labels
        
        @param msg: Message to display
        @param msgType: Type of msgTypes[] value for message-type (optional, default= msgTypes['INFO'])
        '''
        start = '<span>'
        end = '</span>'
        
        # check for message type
        if msgType == self.msgTypes['ERROR']:
            start = '<span style="color: red">'
        elif msgType == self.msgTypes['WARNING']:
            start = '<span style="color: orange">'
        
        # set status labels
        for obj in self.eDefinitions['status']:
            value = start + str(msg) + end
            self.callFunction(obj, 'setText', [str(value)])      
        
        
    def dialog(self, options=dialogOptionsDef):
        '''
        Opens a dialog and returns its value        
        
        @param options: Dictionary of options for the dialog (optional, see dialogOptionsDef for example)
        @return: value returned by the dialog
        '''
        ret = None
        
        if options['type'] == self.dialogTypes['FileOpen']:
            ret = QtGui.QFileDialog.getOpenFileName(self.ui.chkAccessVarEditable, options['title'], options['path'], options['filetypes'])
        elif options['type'] == self.dialogTypes['FileSave']:
            ret = QtGui.QFileDialog.getSaveFileName(self.ui.chkAccessVarEditable, options['title'], options['path'], options['filetypes'])
        
        return ret