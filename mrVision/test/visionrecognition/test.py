from pylab import *
from Pycluster import *
from PIL import Image

a = array([2,3,4,5,6])
b = array([1,0,1,0,1])

# file = 'C:\\4punkte_demo.png'

file = 'C:\\spielfeld.png'

im = Image.open(file)

im = im.convert("1")


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

figure()
white = zeros([100,100])
imshow(white,cmap='binary', origin='upper')

for i in arange(4):
    plot(center[i,1],center[i,0],'kx')

axis('off')

show()
print ho
