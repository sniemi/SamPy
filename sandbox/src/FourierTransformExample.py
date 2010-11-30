'''
Created on Mar 4, 2010

@author: niemi
'''

from scipy import fftpack
import pyfits, math
import numpy as np
import pylab as py
import radialProfile

def drawCircle(pupil, radius, x, y, value = 1):
    rad = np.sqrt(x**2 + y**2)
    mask = rad < radius
    pupil[mask] = value
    return pupil

def drawRectangle(pupil, xc0, yc0, dx0, dy0, value = 0):
    '''
    Draw an antialiased rectangle into image
    xc0, yc0 define the center of the rectangle (in normalize pupil coords)
    dx0, dy0 are the half-widths of the rectangles (normalized pupil coords)
    '''
    print np.shape(pupil)
    nx = np.shape(pupil)[1]
    ny = np.shape(pupil)[0]
    
    left = (xc0 - dx0/2) > -nx/2
    leftpixel = np.min(left)
    right = (xc0 + dx0/2) < ny/2
    rightpixel = np.max(right)
    bottom = (yc0 - dy0/2) > -nx/2
    bottompixel = np.min(bottom)
    top = (yc0 + dy0/2) < ny/2
    toppixel = np.max(top)

    
	
    return pupil


def drawWFC3UVIS():
    size = 1000
    rad = 490
    SpiderRadius = size * 0.011
    
    pupil = np.zeros((size, size))
    cx, cy = np.shape(pupil)[1]/2, np.shape(pupil)[0]/2
    y, x = np.indices(pupil.shape)
    xc = x - cx
    yc = y - cy
    
    pupil = drawCircle(pupil, rad, xc, yc)
    #secondary obsc.
    pupil = drawCircle(pupil, rad*0.33, xc, yc, value = 0)
    #OTA mirror pads
    pupil = drawCircle(pupil, rad*0.065, xc, yc-0.8921*cy, value = 0)
    pupil = drawCircle(pupil, rad*0.065, xc+0.7555*cx, yc+0.4615*cy, value = 0)
    pupil = drawCircle(pupil, rad*0.065, xc-0.7606*cx, yc+0.4564*cy, value = 0)
    #Spiders
    pupil = drawRectangle(pupil, xc, yc, SpiderRadius*rad, 2.1*rad)
    pupil = drawRectangle(pupil, xc, yc, 2.1*rad, SpiderRadius*rad)
    return pupil

image = drawWFC3UVIS()
#image = pyfits.getdata('/grp/hst/OTA/focus/Data/prop11877/visit10-feb2010/ibcy10bkq_flt_dat.fits')

# Take the fourier transform of the image.
F1 = fftpack.fft2(image)

# Now shift the quadrants around so that low spatial frequencies are in
# the center of the 2D fourier transformed image.
F2 = fftpack.fftshift(F1)

# Calculate a 2D power spectrum
psd2D = np.abs(F2)**2

# Calculate the azimuthally averaged 1D power spectrum
psd1D = radialProfile.azimuthalAverage(psd2D)

# plot
py.figure(1)
py.clf()
py.imshow(image, cmap=py.cm.gray)

py.figure(2)
py.clf()
py.imshow(np.log10(psd2D))

py.figure(3)
py.clf()
py.semilogy(psd1D)
py.xlabel('Spatial Frequency')
py.ylabel('Power Spectrum')

py.show()

