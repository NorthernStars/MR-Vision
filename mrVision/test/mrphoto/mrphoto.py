'''
Created on 04.09.2013

@author: hannes
'''

import cv2 as cv
import Image


def getListOfVideoDevices(deviceMaxNum=20):
    '''
    Returns list of available video devices
    '''
    videoList = []
    for i in range(deviceMaxNum):
        videocap = cv.VideoCapture(i)
        if videocap.isOpened():
            videoList.append(i)
        videocap.release()
    return videoList


def getVideoCaputreFromDevice(device, frameWidth=320.0, frameHeight=240.0):
    '''
    Return image from device
    '''
    videocap = cv.VideoCapture(device)
    videocap.set( cv.cv.CV_CAP_PROP_FRAME_WIDTH, frameWidth )
    videocap.set( cv.cv.CV_CAP_PROP_FRAME_HEIGHT, frameHeight )  
    
    if videocap.isOpened():
        return videocap
    return None


def updateImageWindow(windowTitle, image, color=cv.COLOR_BGR2BGRA):
    '''
    Updates a image in a window
    '''
    image = cv.resize( image, (320, 240) )
    
    h = str(image.shape[0])
    w = str(image.shape[1])
    txtColor = (255, 255, 255)     # bgr-color
    txtPos = (10, 15)
    txtFont = cv.FONT_HERSHEY_PLAIN
    txtScale = 1.0
    
    cv.putText( img=image,
                text=w+"x"+h,
                org=txtPos,
                fontFace=txtFont,
                fontScale=txtScale,
                color=txtColor,
                thickness=1 )
    image = cv.cvtColor(image, color)
    cv.imshow( windowTitle, image ) 

def showVideoWindow(videoCapture):
    '''
    Shows a video from VideoCapture() in a window
    Exit with any key
    '''
    windowColorTitle = "Video Color"
    windowGreyTitle = "Video Grey"
    
    cv.namedWindow( windowColorTitle )
    cv.namedWindow( windowGreyTitle )
    cv.moveWindow( windowColorTitle, 50, 50 )
    cv.moveWindow( windowGreyTitle, 50+325, 50 )
    
    while cv.waitKey(1) == -1:
        retval, image = videoCapture.read()      
        if retval:
            updateImageWindow( windowColorTitle, image )
            updateImageWindow( windowGreyTitle, image, cv.COLOR_BGR2GRAY )
    cv.destroyAllWindows()
            
def getPILFromCV(image, greyscale=False):
    '''
    Returns opencv image as PIL Image
    '''
    image = cv.cvtColor( image, cv.COLOR_BGR2RGB )
    if greyscale:
        image = cv.cvtColor( image, cv.COLOR_BGR2GRAY )
    return Image.fromarray( image )
        
    
'''
MAIN FUNCTION

Show video in greyscale and color from fist video device
Also converts first frame to pil image and shows it
'''    
if __name__ == '__main__':
    videocap = getVideoCaputreFromDevice(-1)    # get videocapture device
    
    if videocap != None:
        _, img= videocap.read()                     # get frame
        getPILFromCV( img, False ).show()           # convert to pil and show
    
        showVideoWindow(videocap)                   # show videos
    else:
        print "NO VIDEO DEVICE FOUND"