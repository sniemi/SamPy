# Plot azmuthially averaged radial profile for M51 image
from pylab import *
from numpy import *
import pyfits

im = pyfits.getdata('pix.fits')
# start by determining radii of all pixels from center
y, x = indices((512,512))
r = sqrt((x-257)**2 + (y-258.)**2)

# sort by increasing radii
ind = argsort(r.flat) # indicies ordered such that radii are monotonic
sr = r.flat[ind] # sorted radii
sim = im.flat[ind] # sorted image values
ri = sr.astype(int16) # integer part of radii

# bin and summing
deltar = ri[1:] - ri[:-1] # radius difference between sorted points
                          # assumes all radii represented
rind = where(deltar)[0] # locations of where radii changes
nr = rind[1:] - rind[:-1] # number of points in radius bin
sim = sim*1. # use floats to avoid integer overflow
csim = sim.cumsum() # cumulative sum
tbin = csim[rind[1:]] - csim[rind[:-1]] # sum in radius bin
radialprofile = tbin/nr # the average
semilogy(radialprofile) # plot it!
