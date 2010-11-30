# -*- coding: utf-8 -*- 
""" 
Created on Thu Nov 26 22:00:20 2009 

Author: josef-pktd and scipy mailinglist example 
""" 

import numpy as np 
from scipy import interpolate 
import matplotlib.pyplot as plt 

# from mailing list - Peter Combs 
def makeLSQspline(xl, yl, xr, yr): 
  """docstring for makespline""" 

  xmin = xr.min()-1 
  xmax = xr.max()+1 
  ymin = yr.min()-1 
  ymax = yr.max()+1 
  n = len(xl) 

  print "xrange: ", xmin, xmax, '\t', "yrange: ", ymin, ymax 
  s = 1.1 
  yknots, xknots = np.mgrid[ymin+s:ymax-s:10j, xmin+s:xmax-s:10j]   # Makes an 11x11 regular grid of knot locations 
  yknots = np.linspace(ymin+s,ymax-s,10) 
  xknots = np.linspace(xmin+s,xmax-s,10) 

  xspline = interpolate.LSQBivariateSpline(xr, yr, xl, xknots.flat, yknots.flat) 
  yspline = interpolate.LSQBivariateSpline(xr, yr, yl, xknots.flat, yknots.flat) 

  def mapping(xr, yr): 
      xl = xspline.ev(xr, yr) 
      yl = yspline.ev(xr, yr) 
      return xl, yl 
  return mapping, xspline, yspline 

xr = np.arange(20) 
yr = np.arange(20) 
s=0 
xr, yr = np.mgrid[0+s:20-s:30j, 0+s:20-s:30j] 
xr = xr.ravel() 
yr = yr.ravel() 

xl = np.sin(xr) + 0.1*np.random.normal(size=xr.shape) 
yl = yr + 0.1*np.random.normal(size=yr.shape) 

smap, xspline, yspline = makeLSQspline(xl, yl, xr, yr) 
#print smap(xr, yr) 
plt.plot(xl) 
plt.plot(xr) 
#plt.show() 
xsp = interpolate.SmoothBivariateSpline(xr, yr, xl, kx=2,ky=2) 
print xsp.get_knots() 


#example from tests, testfitpack.py 

x = [1,1,1,2,2,2,3,3,3] 
y = [1,2,3,1,2,3,1,2,3] 
z = [3,3,4,4,5,6,3,3,3] 
s = 0.1 
tx = [1+s,3-s] 
ty = [1+s,3-s] 
lut = interpolate.LSQBivariateSpline(x,y,z,tx,ty,kx=1,ky=1) 


import numpy as np 
from scipy import interpolate 
import matplotlib.pyplot as plt 


#2d spline interpolation example from the tutorial 
#------------------------------------------------- 

# Define function over sparse 20x20 grid 

x,y = np.mgrid[-1:1:20j,-1:1:20j] 
z = (x+y)*np.exp(-6.0*(x*x+y*y)) 

plt.figure() 
plt.pcolor(x,y,z) 
plt.colorbar() 
plt.title("Sparsely sampled function.") 
#plt.show() 

# Interpolate function over new 70x70 grid 

xnew,ynew = np.mgrid[-1:1:70j,-1:1:70j] 
tck = interpolate.bisplrep(x,y,z,s=0) 
znew = interpolate.bisplev(xnew[:,0],ynew[0,:],tck) 

plt.figure() 
plt.pcolor(xnew,ynew,znew) 
plt.colorbar() 
plt.title("Interpolated function - bisplrep") 
#plt.show() 



#Use spline classes instead of original wrapper 
#---------------------------------------------- 

#use same example as before 
### Define function over sparse 20x20 grid 
## 
##x,y = np.mgrid[-1:1:20j,-1:1:20j] 
##z = (x+y)*np.exp(-6.0*(x*x+y*y)) 
## 
##plt.figure() 
##plt.pcolor(x,y,z) 
##plt.colorbar() 
##plt.title("Sparsely sampled function.") 
###plt.show() 

#use SmoothBivariateSpline 
#^^^^^^^^^^^^^^^^^^^^^^^^^ 


xnew,ynew = np.mgrid[-1:1:70j,-1:1:70j] 
#tck = interpolate.bisplrep(x,y,z,s=0) 
intp = interpolate.SmoothBivariateSpline(x.ravel(),y.ravel(),z.ravel(),s=0.01) 
znew = intp.ev(xnew.ravel(),ynew.ravel()).reshape((70,70)) 

plt.figure() 
plt.pcolor(xnew,ynew,znew) 
plt.colorbar() 
plt.title("Interpolated function - SmoothBivariateSpline") 
#plt.show() 

#use LSQBivariateSpline 
#^^^^^^^^^^^^^^^^^^^^^^^^^ 


xnew,ynew = np.mgrid[-1:1:70j,-1:1:70j] 

#get knots from previous example 
tx,ty = intp.get_knots() 
tx = tx[4:-4]  # remove endpoints, 4 in this example 
ty = ty[4:-4] 

intp = interpolate.LSQBivariateSpline(x.ravel(),y.ravel(),z.ravel(), tx, ty) 
znew = intp.ev(xnew.ravel(),ynew.ravel()).reshape((70,70)) 
plt.figure() 
plt.pcolor(xnew,ynew,znew) 
plt.colorbar() 
plt.title("Interpolated function - LSQBivariateSpline") 
#plt.show() 

#use RectBivariateSpline 
#^^^^^^^^^^^^^^^^^^^^^^^^ 

# this seems to cause a crash, for eg. s=0.001 
# or maybe matplotlib related or maybe numpy ABI problems ? 
# or maybe some random crashing ? 
# I think it's matplotlib when closing windows 

intp = interpolate.RectBivariateSpline(x[:,0],y[0,:],z, s=0.001) 
znew = intp.ev(xnew.ravel(),ynew.ravel()).reshape((70,70)) 

plt.figure() 
plt.pcolor(xnew,ynew,znew) 
plt.colorbar() 
plt.title("Interpolated function - RectBivariateSpline") 
plt.show() 

