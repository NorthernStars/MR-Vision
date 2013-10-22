'''
Created on 16.10.2013

@author: northernstars
'''

class AbstractSourceGrabber(object):
    '''
    Abstract class for generating new image grabbers
    '''
    _source = None
    _resize = None
    _gray = False


    def __init__(self, source):
        '''
        Constructor
        '''
        self._source = source
        
    def close(self):
        '''
        Closes source
        '''
        pass
    
    def getImg(self):
        '''
        Returns image from source
        '''
        pass
    
    def getSource(self):
        '''
        Returns source
        '''
        return self._source
    
    def setParameter(self, srcW=None, srcH=None, gray=None):
        '''
        Sets parameter of source
        @param srcW: Width of source image
        @param srcH: Height of source image
        @param gray: If True the image will, be converted to gray
        '''
        if srcW != None and srcH != None:
            # resize image
            self.__resize = (srcW, srcH)
        elif srcW == None and srcH == None:
            self.__resize = None
            
        if gray != None:
            self.__gray = gray