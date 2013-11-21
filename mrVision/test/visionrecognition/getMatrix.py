import cv2
import numpy as np


filename = "markerbad2.jpg"
thres = 0.4
borderMultiply = 3.0

# get image
img= cv2.imread(filename)
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
gray = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)[1]

# show original image
img = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
cv2.imshow("original", img)
cv2.waitKey(0)

# get matrix
imgWidth = img.shape[1]
imgHeight = img.shape[0]
rows = 7
columns = 7
matrix = np.zeros( (rows, columns), np.bool_ )

# search for pattern
restHeight = imgHeight
for r in range(rows):
    # calculate height of pattern
    drow = restHeight / (rows - r)
    restWidth = imgWidth
    
    for c in range(columns):
        # calculate width and position of pattern        
        dcol = restWidth / (columns - c)
        patternSize = drow * dcol
        
        xStart = imgWidth - restWidth
        yStart = imgHeight - restHeight
        xEnd = xStart + dcol
        yEnd = yStart + drow
        
        # draw pattern
        cv2.rectangle( img, (xStart, yStart), (xEnd, yEnd), (255,0,0) )
        cv2.imshow("pattern", img)
        
        # set matrix element
        val = np.count_nonzero( gray[yStart:yEnd, xStart:xEnd] )
        matrix[r][c] = val
        
        if r == 0 or r == rows-1 or c == 0 or c == columns-1:
            th = patternSize * thres * borderMultiply
        else:
            th = patternSize * thres

        matrix[r][c] = val > th
        
        # set rest width and height
        restWidth -= dcol
        
    # set rest height
    restHeight -= drow
        
# show matrix
print "matrix:\n", matrix
cv2.waitKey(0)
    
    
    