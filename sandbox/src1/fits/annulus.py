
import pyfits
import numdisplay
from numpy import *

filename = "file"
xcentre = 500
ycentre = 500
radlimit = 50

imdata = pyfits.getdata(filename)

y, x = indices(imdata.shape, dtype=float32)

x = x - xcentre
y = y - ycentre

radius = sqrt(x**2 + y**2)

mask = radius < radlimit

flux = (mask*im).sum()

numdisplay.display(mask*im)

