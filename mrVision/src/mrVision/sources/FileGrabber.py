'''
Created on 16.10.2013

@author: northernstars
'''
from AbstractSourceGrabber import AbstractSourceGrabber
from cv2 import resize
from os.path import isfile
from imageLibs.imageprocessing import getImgFromFile

class FileGrabber(AbstractSourceGrabber):
    '''
    Grabber to read image from file
    '''
    

    def __init__(self, source=""):
        '''
        Constructor
        @param source: Filepath of file to read
        '''
        super(FileGrabber, self).__init__(source)
    
    
    def getImg(self, source=None):
        '''
        Reads image from file
        @param source: Use filepath of source to read image
        '''
        src = self._source
        # check source parameter
        if source != None:
            src = source
            
        # read image from file
        if isfile(src):
            img = getImgFromFile(src, self._gray)
            
            if img != None:
            
                # resize image
                if self._resize != None:
                    img = resize(img, self._resize)
            
                return img
        
        return False
        