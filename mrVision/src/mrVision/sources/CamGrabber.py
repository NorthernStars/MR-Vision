'''
Created on 16.10.2013

@author: northernstars
'''
from AbstractSourceGrabber import AbstractSourceGrabber
from imageLibs.imageprocessing import openCam, getImgFromCam, setCamImgSize
from cv2 import resize
from cv2.cv import CV_CAP_PROP_FRAME_WIDTH, CV_CAP_PROP_FRAME_HEIGHT

class CamGrabber(AbstractSourceGrabber):
    '''
    Calss for grabbing image from camera (USB/Firewire)
    '''
    __cam = None


    def __init__(self, source=0, w=320, h=240):
        '''
        Constructor
        @param source: Video source number
        '''
        super(CamGrabber, self).__init__(source)
        self.__cam = openCam(self._source)
        setCamImgSize(self.__cam, w, h)

    def close(self):
        '''
        Closes camera device
        '''
        if self.__cam != None and self.__cam.isOpened():
            self.__cam.release()
            self.__cam = None
            
    def isOpened(self):
        '''
        Returns True if camera is opened
        '''
        if self.__cam != None:
            return self.__cam.isOpened()
        return False
    
    def getImg(self):
        '''
        Returns image from camera
        '''
        if self.__cam != None:
            img = getImgFromCam(self.__cam, self._gray)
            if img != None:            
                # resize image
                if self._resize != None:
                    img = resize(img, self._resize)
                
                return img
        
        return False
    
    def setImgSize(self, w=320, h=240):
        '''
        Sets camera image size
        @param w: Image width
        @param h: Image height
        '''
        self.close()
        self.__init__(self._source, w, h)
    
    def setParameter(self, srcW=None, srcH=None, gray=None, imgW=None, imgH=None):
        '''
        Sets parameter of source
        @param srcW: Width of source image
        @param srcH: Height of source image
        @param gray: If True the image will, be converted to gray
        @param imgW: Width of image (resize)
        @param imgH: Height of image (resize)
        '''
        super(CamGrabber, self).setParameter(imgW, imgH, gray)
        
        # set source image size
        if self.__cam != None and self.__cam.isOpened():
            if srcW != None:
                self.__cam.set(CV_CAP_PROP_FRAME_WIDTH, srcW)
            if srcH != None:
                self.__cam.set(CV_CAP_PROP_FRAME_HEIGHT, srcH)
            
        