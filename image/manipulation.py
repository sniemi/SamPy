'''
Basic image manipulation algorithms such as Gaussian smoothing

:requires: NumPy
:requires: SciPy

:author: Sami-Matias Niemi
'''
import numpy as np
import scipy.signal as s


def gaussianKernel(size, sizey=None):
    '''
    Returns a normalized 2D gauss kernel array for convolutions.
    '''
    size = int(size)
    if not sizey:
        sizey = size
    else:
        sizey = int(sizey)
    x, y = np.mgrid[-size:size + 1, -sizey:sizey + 1]
    g = np.exp(-(x ** 2 / float(size) + y ** 2 / float(sizey)))
    return g / g.sum()


def blurImage(im, n, ny=None):
    '''
    blurs the image by convolving with a gaussian kernel of typical
    size n. The optional keyword argument ny allows for a different
    size in the y direction.
    '''
    g = gaussianKernel(n, sizey=ny)
    improc = s.convolve(im, g, mode='valid')
    return improc
