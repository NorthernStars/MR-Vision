'''
Created on 21.10.2013

@author: northernstars
'''
from gui.GuiLoader import GuiLoader
from sources.AbstractSourceGrabber import AbstractSourceGrabber
from sources.CamGrabber import CamGrabber
from sources.FileGrabber import FileGrabber
from core.imageprocessing import imageToPixmap

from PyQt4.QtGui import QGraphicsScene
from PyQt4.QtCore import QTimer, Qt
from cv2 import cvtColor, COLOR_BGR2RGB, COLOR_GRAY2RGB, COLOR_HLS2RGB, COLOR_YUV2RGB  # @UnusedImport
from numpy import ndarray
from copy import copy


class ImageGrabber(object):
    '''
    classdocs
    '''
    __gui = GuiLoader()
    __sources = []
    __grabTimer = QTimer()
    __img = None
    
    __scene = None
    __gview = None
    

    def __init__(self, gui=None):
        '''
        Constructor
        '''
        self.__gui = GuiLoader()
        
        if gui != None:
            self.__gui = gui
            self.__initGui()
            
    def __initGui(self):
        '''
        Initiates gui listeners
        '''
        # initiate scene
        self.__gview = self.__gui.getObj("imgVideo")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        # add image size combobox items
        cmb = self.__gui.getObj("cmbImgSize")
        cmb.addItem("320x240")
        cmb.addItem("640x768")
        cmb.addItem("800x600")
        cmb.addItem("1024x768")
        cmb.addItem("1280x920")
        
        # add conversion combobox items
        cmb = self.__gui.getObj("cmbConversion")
        cmb.addItem("None")
        cmb.addItem("COLOR_BGR2RGB")
        cmb.addItem("COLOR_GRAY2RGB")
        cmb.addItem("COLOR_YUV2RGB")
        cmb.addItem("COLOR_HLS2RGB")
        
        # add listeners
        self.__gui.connect( "cmdStartVideo", "clicked()", self.startVideo )
        self.__gui.connect( "cmdStopVideo", "clicked()", self.stopVideo )
        self.__gui.connect( "cmdAddSource", "clicked()", self.__addCamSource )
        self.__gui.connect( "cmdAddFile", "clicked()", self.__addFileSource )
        self.__gui.connect( "cmdDelSource", "clicked()", self.__removeSourceFromList )
        self.__gui.connect( "cmbImgSize", "currentIndexChanged(QString)", self.__imageSizeChanged )
        
    def isActive(self):
        '''
        @return: True if image grabbing is active
        '''
        return self.__grabTimer.isActive()
        
    def startVideo(self):
        '''
        Starts grabbing images
        '''
        if self.__grabTimer.isActive():
            self.__grabTimer.stop()
        
        self.__grabTimer = QTimer()
        self.__grabTimer.timeout.connect( self.__grabImage )
        self.__grabTimer.start(0)
        self.__gui.status("Video started")
    
    def stopVideo(self):
        '''
        Stops grabbing video
        '''
        if self.__grabTimer.isActive():
            self.__grabTimer.stop()
            self.__scene.clear()
            self.__gview.show()
            self.__gui.status("Video stopped")
    
    def getImage(self):
        '''
        Returns the last grabbed image
        @return: Image
        '''
        return self.__img
    
    def __showImage(self):
        '''
        Shows image on graphics view
        '''
        if self.__img != None:
            self.__scene.clear()
            self.__scene.addPixmap( imageToPixmap(self.__img) )
            self.__gview.fitInView( self.__scene.sceneRect(), Qt.KeepAspectRatio )
            self.__gview.show()
    
    def __grabImage(self):
        '''
        Graps image from sources
        '''        
        images = []
        
        # grab all images
        for src in self.__sources:
            assert isinstance(src, AbstractSourceGrabber)
            images.append( src.getImg() )
        
        # join and convert images
        img = self.__joinImages(images)
        
        # convert image
        convert = eval( str(self.__gui.getObj("cmbConversion").currentText()) )
        if convert != None:
            try:
                img = cvtColor(img, convert)
            except:
                img = None

        # show results
        if type(img) == ndarray:
            # add image as new image
            self.__img = img
            self.__showImage()
            
        else:
            # show message
            self.__scene.clear()
            self.__scene.addText("NO VIDEO")
        
            
    
    def __joinImages(self, images=[]):
        '''
        Joins images
        '''
        # TO-DO: Joining images
        if len(images) > 0:
            return images[0]
        return False
    
    def __imageSizeChanged(self, size="640x480"):
        '''
        Changes image size
        '''
        size = str(size).split("x")
        w = int(size[0])
        h = int(size[1])
        
        # set size
        for cam in self.__sources:
            if type(cam) == CamGrabber:
                assert isinstance(cam, CamGrabber)
                cam.setImgSize(w, h)
        
    
    def __addSourceToList(self, grabber=None):
        '''
        Adds source to source list
        '''
        assert isinstance(grabber, AbstractSourceGrabber)
        
        if grabber != None:
            # add grabber to list
            self.__sources.append( grabber )
            txt = None
            
            # get type of grabber
            if type(grabber) == CamGrabber:
                txt = "cam [" + str(grabber.getSource()) + "]"
            elif type(grabber) == FileGrabber:
                txt = "file [" + str(grabber.getSource()) + "]"
                
            # add text string to gui list
            if txt != None:
                self.__gui.getObj("lstSources").addItem(txt)
                
    def __removeSourceFromList(self):
        '''
        Removes selected source from list
        '''
        for item in self.__gui.getObj("lstSources").selectedItems():
            # get item informationen
            txt = str( item.text() )
            if "[" in txt and "]" in txt:
                data = txt.split("[")
                iType = data[0].strip()
                iSource = data[1].replace(']', '')
                
                # search for grabber
                for grabber in self.__sources:
                    assert isinstance(grabber, AbstractSourceGrabber)
                    
                    if str(grabber.getSource()) == iSource:
                        if type(grabber) == CamGrabber and iType == "cam":
                            self.__sources.remove(grabber)
                            break
                        elif type(grabber) == FileGrabber and iType == "file":
                            self.__sources.remove(grabber)
                            break
                
                # remove source from gui list
                item = self.__gui.getObj("lstSources").takeItem( self.__gui.getObj("lstSources").currentRow() )
                item = None
                        
            
    
    def __addCamSource(self):
        '''
        Adds camera as source
        '''
        obj = self.__gui.getObj("txtSource")
        source = int( obj.text() )
        
        grabber = CamGrabber(source)
        if grabber.isOpened():
            self.__addSourceToList(grabber)
            self.__gui.status( "Added camera source ["+str(source)+"]" )
        else:
            self.__gui.status( "Could not add camera source ["+str(source)+"]", self.__gui.msgTypes['ERROR'] )
    
    def __addFileSource(self):
        '''
        Adds file as source
        '''
        self.stopVideo()
        options = copy(self.__gui.dialogOptionsDef)
        options['filetypes'] = "Images (*.jpg *jpeg *gif *png *bmp *tif)"
        source = str(self.__gui.dialog(options))
        
        if len(source) > 0:
            grabber = FileGrabber(source)
            self.__addSourceToList(grabber)
            
            self.__gui.status( "Added file source ["+str(source)+"]" )