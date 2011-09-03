#! /usr/bin/env python
import pylab as P
import pyfits as PF
import sys
import smnIO.sextutils as su
import numpy as N
from matplotlib import cm
from matplotlib.patches import Circle


if __name__ == '__main__':
    #command line arguments
    fits = sys.argv[1]
    cat = sys.argv[2]

    rad = 5
    log = True

    #fits file data
    data = PF.getdata(fits)

    #sextractor catalogue data
    cat_data = su.se_catalog(cat)

    #min and max
    min = N.min(data)
    max = N.max(data)

    #make plot
    P.figure(figsize=(12, 12))
    ax = P.subplot(111)
    bb = P.gca()

    if log:
        ax.imshow(N.log10(data), origin='lower',
                  interpolation=None,
                  vmin=min * 1.05,
                  vmax=N.log10(max) * .9,
                  cmap=cm.binary)
    else:
        ax.imshow(data, origin='lower', interpolation=None)

    for a, b in zip(cat_data.x_image, cat_data.y_image):
        cir = Circle((a, b), radius=rad, fc='none', ec='r')
        bb.add_patch(cir)

    P.show()
