'''
Created on 01.10.2013

@author: hannes
'''
from PIL import Image
from pylab import *
from Pycluster import treecluster
import os

TEST_IMAGE = "../../img/spielfeld.png"

class mrVisionRecognition(object):
    '''
    classdocs
    '''
    __camList = []
    __calibData = {"offset": array(), "u": array(), "v": array()}    # [offset, u, v]

    def __init__(self):
        '''
        Constructor
        '''
        self.__camList = []
        self.__calibData = {"offset": array(), "u": array(), "v": array()}
        self.__camList.append( ["camobject", "transformation"] )
    
    
    def addCam(self, camType=None, source=None):
        '''
        Adds camera source to list
        @param camType: Camera type
        @param source: Source of camera
        '''
        pass
    
    def remCam(self, index=0):
        '''
        Removes a camera from camera source list
        @param index: Index of camera source in camera source list
        '''
        pass
    
    
    def getObjects(self):
        '''
        Returns list of objects
        '''
        self.__recogniseObjects( self.__getCamImage() )  
        
        
    def calibrate(self):
        '''
        Calibrates vision
        '''
        self.__calibration( self.__getCamImage() )  
    
    
    def __getCamImage(self):
        '''
        Returns image from cam sources
        '''
        imgList = []
        
        # get images
        for cam in self.__camList:
            # get image from source
            print "loading", os.getcwd(), TEST_IMAGE
            img = Image.open(TEST_IMAGE)
            
            # transform images
            # TO-DO
            
            # add image to list
            imgList.append( img )
            
        # combine images
        # TO-DO
            
        # return image
        if len(imgList) > 0 and imgList[0] != None:
            im = imgList[0].convert("1")
            return im
        
        return None
            
    
    def __recogniseObjects(self, im=None):
        '''
        Returns list of reognised images
        @param im: Image to analyse
        '''
        objList = []
        
        # TO-DO: image recognition
        
        return objList
    
    def __calibration(self, im=None):
        '''
        Calibrates vision module
        '''
        
        # Ermittle Bildgroesse:
        M = im.size[0]
        N = im.size[1]
        
        data = array(im.getdata())
        data = data.reshape(im.size)
        
        px1 = vstack([nonzero(data==0)[0],nonzero(data==0)[1]]).T
        
        tree = treecluster(px1)
        
        ho = tree.cut(4)
        
        # Bestimme Zentren:
        center = zeros([4,2])
        
        for i in arange(4):
            tmp = px1[nonzero(ho==i)[0],:]
            center[i,0]=mean(tmp[:,0])
            center[i,1]=mean(tmp[:,1])
            tmp_ref = tmp-center[i,:]
            max_abs = max(sqrt((tmp_ref**2).sum(axis=1))) #bestimme den maximalen Abstand der zum Cluster zugehoerigen Pixel
            print max_abs
            
        # Plotte die gefundenen Cluster
        figure()
        white = zeros([100,100])
        imshow(white,cmap='binary', origin='upper')
        
        for i in arange(4):
            tmp =px1[nonzero(ho==i)[0],:]
            plot(tmp[:,1],tmp[:,0],'o')
            plot(center[i,1],center[i,0],'kx')
        # xlim([0,100])
        # ylim([0,100])
        axis('off')
        
        # Plotte die Mittelpunkte der Cluster
        figure()
        white = zeros([100,100])
        imshow(white,cmap='binary', origin='upper')
        
        for i in arange(4):
            plot(center[i,1],center[i,0],'kx')
        
        axis('off')
        
        show()
        
        #Suche die zwei linken Cluster und die zwei rechten Cluster:
        vlnr = argsort(center[:,1])
        
        print vlnr
        
        pts_links = center[vlnr[:2],:]
        pts_rechts = center[vlnr[2:],:]
        
        print pts_links
        print pts_rechts
        
        # Definiere die Punkte fuer das Koordinatensystem:
        p00 = pts_links[argsort(pts_links[:,0])[0],:]
        p01 = pts_links[argsort(pts_links[:,0])[1],:]
        
        p10 = pts_rechts[argsort(pts_rechts[:,0])[0],:]
        p11 = pts_rechts[argsort(pts_rechts[:,0])[1],:]
        
        print p00 #Ursprung
        print p01
        print p10
        print p11
        
        p0 = (p00+p01)/2
        p1 = (p10+p11)/2
        
        print p0
        print p1
        
        pz = (p0+p1)/2
        
        d0 = sqrt(((p00-p01)**2).sum())
        
        print "Abstandsvektor links"
        print p01-p00
        print "Abstand links"
        print d0
        
        d1 = sqrt(((p10-p11)**2).sum())
        
        print "Abstandsvektor rechts"
        print p11-p10
        print "Abstand rechts"
        print d1
        
        dz = sqrt(((p0-p1)**2).sum())
        
        print "Abstandsvektor zentral"
        print p1-p0
        print "Abstand zentral"
        print dz
        
        # Hier muessen Reaktionen auf eine falsche Kameraposition erfolgen:
        if dz<d0:
            print "Kamera um 90 Grad drehen!"
        else:
            print "Alles in Ordnung!"
            
        # Plotte die Mittelpunkte der Cluster
        figure()
        imshow(-data,cmap='binary', origin='upper')
        
        plot(p00[1],p00[0],'rx', markersize=15)
        plot(p01[1],p01[0],'rx', markersize=15)
        plot(p10[1],p10[0],'rx', markersize=15)
        plot(p11[1],p11[0],'rx', markersize=15)
        
        plot(p0[1],p0[0],'rx', markersize=15)
        plot(p1[1],p1[0],'rx', markersize=15)
        
        plot(pz[1],pz[0],'rx', markersize=15)
        
        #Linien:
        plot(array([p00[1],p01[1]]),array([p00[0],p01[0]]),'r--')
        plot(array([p10[1],p11[1]]),array([p10[0],p11[0]]),'r--')
        plot(array([p0[1],p1[1]]),array([p0[0],p1[0]]),'r--')
        
        axis('off')
        show()
        
        # Definiere Basisvektoren:
        bv_0 = p01-p00
        bv_1 = p10-p00
        
        # save data
        self.__calibData['u'] = bv_0
        self.__calibData['v'] = bv_1
        self.__calibData['offset'] = p00
        
        # Teste Projektion:
        
        x = array([39.5,54])
        
        print x-p00
        print self.__getCoordinates(x-p00,bv_0,bv_1)
        
        
    def __getCoordinates(self, x,u,v):
        x_u = (x[0]*u[0] + x[1]*u[1])/(u[0]**2 + u[1]**2)
        x_v = (x[0]*v[0] + x[1]*v[1])/(v[0]**2 + v[1]**2)
        return x_u, x_v
        