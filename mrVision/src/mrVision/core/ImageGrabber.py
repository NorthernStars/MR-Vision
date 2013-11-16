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
from cv2 import cvtColor, COLOR_BGR2RGB, COLOR_GRAY2RGB, COLOR_HLS2RGB, COLOR_YUV2RGB, imwrite  # @UnusedImport
from numpy import ndarray
from copy import copy


class ImageGrabber(object):
    '''
    classdocs
    '''
    _gui = GuiLoader()
    _img = None
    __sources = []
    __grabTimer = QTimer()
    
    __scene = None
    __gview = None
    

    def __init__(self, gui=None):
        '''
        Constructor
        '''
        self._gui = GuiLoader()
        
        if gui != None:
            self._gui = gui
            self.__initGui()
            
    def __initGui(self):
        '''
        Initiates gui listeners
        '''
        # initiate scene
        self.__gview = self._gui.getObj("imgVideo")
        self.__scene = QGraphicsScene()
        self.__gview.setScene(self.__scene)
        
        # add image size combobox items
        cmb = self._gui.getObj("cmbImgSize")
        cmb.addItem("320x240")
        cmb.addItem("640x480")
        cmb.addItem("800x600")
        cmb.addItem("1024x768")
        #cmb.addItem("1280x960")        # not working with libdc1394 and avt stringray 125c
        
        # add conversion combobox items
        cmb = self._gui.getObj("cmbConversion")
        cmb.addItem("None")
        cmb.addItem("COLOR_BGR2RGB")
        cmb.addItem("COLOR_GRAY2RGB")
        cmb.addItem("COLOR_YUV2RGB")
        cmb.addItem("COLOR_HLS2RGB")
        
        # add listeners
        self._gui.connect( "cmdStartVideo", "clicked()", self.startVideo )
        self._gui.connect( "cmdStopVideo", "clicked()", self.stopVideo )
        self._gui.connect( "cmdAddSource", "clicked()", self.__addCamSource )
        self._gui.connect( "cmdAddFile", "clicked()", self.__addFileSource )
        self._gui.connect( "cmdDelSource", "clicked()", self.__removeSourceFromList )
        self._gui.connect( "cmbImgSize", "currentIndexChanged(QString)", self.__imageSizeChanged )
        self._gui.connect( "cmdSaveImg", "clicked()", self.saveImg )
        
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
        self._gui.status("Video started")
    
    def stopVideo(self):
        '''
        Stops grabbing video
        '''
        if self.__grabTimer.isActive():
            self.__grabTimer.stop()
            self.__scene.clear()
            self.__gview.show()
            self._gui.status("Video stopped")
    
    def getImage(self):
        '''
        Returns the last grabbed image
        @return: Image
        '''
        return self._img
    
    def saveImg(self):
        '''
        Saves image
        '''
        if self._img != None:
            img = self._img
            
            # stop video
            active = self.isActive()
            self.stopVideo()
            
            # open file dialog
            options = copy(self._gui.dialogOptionsDef)
            options['type'] = self._gui.dialogTypes['FileSave']
            options['filetypes'] = "JPG (*.jpg)"
            options['title'] = "Save current frame as"
            src = str( self._gui.dialog(options) )
            
            # check filepath and save
            if len(src) > 0:
                if not src.endswith(".jpg"):
                    src = src+".jpg"
                self._gui.status( "write to " + src )
                cvtColor(img, COLOR_BGR2RGB)
                imwrite(src, img)
            
            # reset video streaming
            if active:
                self.startVideo()
        
    
    def __showImage(self):
        '''
        Shows image on graphics view
        '''
        if self._img != None:
            self.__scene.clear()
            self.__scene.addPixmap( imageToPixmap(self._img) )
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
        convert = eval( str(self._gui.getObj("cmbConversion").currentText()) )
        if convert != None:
            try:
                img = cvtColor(img, convert)
            except:
                img = None

        # show results
        if type(img) == ndarray:
            # add image as new image
            self._img = img
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
                self._gui.getObj("lstSources").addItem(txt)
                
    def __removeSourceFromList(self):
        '''
        Removes selected source from list
        '''
        for item in self._gui.getObj("lstSources").selectedItems():
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
                item = self._gui.getObj("lstSources").takeItem( self._gui.getObj("lstSources").currentRow() )
                item = None
                        
            
    
    def __addCamSource(self):
        '''
        Adds camera as source
        '''
        obj = self._gui.getObj("txtSource")
        source = int( obj.text() )
        
        grabber = CamGrabber(source)
        if grabber.isOpened():
            self.__addSourceToList(grabber)
            self._gui.status( "Added camera source ["+str(source)+"]" )
        else:
            self._gui.status( "Could not add camera source ["+str(source)+"]", self._gui.msgTypes['ERROR'] )
    
    def __addFileSource(self):
        '''
        Adds file as source
        '''
        self.stopVideo()
        options = copy(self._gui.dialogOptionsDef)
        options['filetypes'] = "Images (*.jpg *jpeg *gif *png *bmp *tif)"
        source = str(self._gui.dialog(options))
        
        if len(source) > 0:
            grabber = FileGrabber(source)
            self.__addSourceToList(grabber)
            
            self._gui.status( "Added file source ["+str(source)+"]" )