# linear interpolation for an array of ordinates
from numpy import *
import numpy.random as ra


# x, y represent the sampled function
x = arange(10.)*2
y = x**2

xx = ra.uniform(0., 18., size=100) # 100 random numbers between 0 and 18
xind = searchsorted(x, xx)-1 # find matching x index
xfract = (xx - x[xind])/(x[xind+1]-x[xind]) # fractional distance
yy = y[xind] + xfract*(y[xind+1]-y[xind]) # interpolated value



