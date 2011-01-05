'''
Created on Jan 20, 2010

@author: Sami-Matias Niemi
'''

import math as m
from numpy.fft import fft2, ifft2

def Convolve(image1, image2, MinPad=True, pad=True):
    '''
    Convolves image1 with image2.
    '''
    #The size of the images:
    r1, c1 = image1.shape
    r2, c2 = image2.shape

    if MinPad:
        r = r1 + r2
        c = c1 + c2
    else:
        r = 2*max(r1,r2)
        c = 2*max(c1,c2)
    
    #or in power of two
    if pad:
        pr2 = int(m.log(r)/m.log(2.) + 1.)
        pc2 = int(m.log(c)/m.log(2.) + 1.)
        rOrig = r
        cOrig = c
        r = 2**pr2
        c = 2**pc2
    
    fftimage = fft2(image1, s=(r,c))*fft2(image2[::-1,::-1],s=(r,c))

    if pad:
        return (ifft2(fftimage))[:rOrig,:cOrig].real
    else:
        return (ifft2(fftimage)).real
    
if __name__ == '__main__':
    import sys
    import pylab as P
    import pyfits as PF
    
    iname1 = sys.argv[1]
    iname2 = sys.argv[2]
    
    #assume fits files
    im1 = PF.open(iname1)[1].data[500:1001,500:1001]
    im2 = PF.open(iname2)[1].data[500:1001,500:1001]
    
    #convolves
    conv = Convolve(im1, im2)
    
    #plots
    P.imshow(im1, origin = 'lower', interpolation = None)
    P.show()

    P.imshow(im2, origin = 'lower', interpolation = None)
    P.show()

    P.imshow(conv, origin = 'lower', interpolation = None)
    P.show()
    