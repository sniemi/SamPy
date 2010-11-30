'''
DESCRIPTION:
Calculates statistics from a file that lists
Zernike polynomials. Can be used to derive best
suitable fixed Zernike values for WFC3 measurements.

Generates histograms from the data and plots the 
mean values and Gaussian fits.

USAGE:
python FocusInValuesWfc3.py

HISTORY:
Created on Nov 1, 2009

@author: Sami-Matias Niemi (niemi@stsci.edu)
'''

import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.use('PDF')
matplotlib.rcParams['legend.fontsize'] = 9
import numpy as N
import pylab as P
import math

__author__ = 'Sami-Matias Niemi'
__version__ = '0.9'

def FitGaussian(xdata, ydata, initials):
    import scipy.optimize 
    
    fitfunc = lambda p, x: p[0]*N.exp(-((x - p[1])/p[2])**2)
    errfunc = lambda p, x, y: p[0]*N.exp(-((x - p[1])/p[2])**2) - y
    
    p1, success = scipy.optimize.leastsq(errfunc, initials, args=(xdata, ydata))
    # compute the best fit function from the best fit parameters
    corrfit = fitfunc(p1, xdata)
    return corrfit

file = '/grp/hst/OTA/focus/WFC3/WFC3parameterFixing'

file = open(file, 'r').readlines()

wave, came, focu, xcom, ycom, xast = [], [], [], [], [], []
yast, sphe, xclo, yclo, xspa, yspa = [], [], [], [], [], []
xash, yash, fift, star, sxti, syti = [], [], [], [], [], []
spid, blur, = [], []

dict = {      'Focus' : focu,
              'X-coma': xcom,
              'Y-coma': ycom,
              'X-astigmatism': xast,
              'Y-astigmatism': yast,
              'Spherical': sphe,
              'X-clover': xclo,
              'Y-clover': yclo,
              #'X-spherical astigmatism': xspa,
              #'Y-spherical astigmatism': yspa,
              'X-ashtray': xash,
              'Y-Ashtray': yash,
              #'Fifth order spherical': fift,
              'Star  1 Background': star,
              'Star  1 X-tilt': sxti,
              'Star  1 Y-tilt': syti,
              'Blur': blur}

for line in file:
    for key in dict:
        if key in line:
            sta = 37
            sto = line.find('from')
            num = line[sta:sto].strip()
            dict[key].append(float(num))

#calculate stats
print '                           Property       average         median           std'
for key in dict:
    av = N.mean(dict[key])
    me = N.median(dict[key])
    st = N.std(dict[key])
    print '%35s%15.8f%15.8f%15.8f' % (key, av, me, st)

#make histogram plots
for key in dict:
    nm = key
    mean = N.mean(dict[key])
    
    P.figure()
    P.title(nm)
    a, b, c = P.hist(dict[key], bins = 40, histtype = 'bar', rwidth = 0.9, hatch = '/')
    fitted = FitGaussian(b[:-1], a, [1.0, me, st])
    P.plot(b[:-1], fitted, label = 'Gaussian Fit')
    P.axvline(mean, label = 'Mean', color = 'red')
    P.annotate('%10.6f' % mean,
               xy = (1.15*mean, 0.8*max(a)), 
               horizontalalignment='center',
               verticalalignment='center',
               style = 'italic', size = 'small',
               color='red', rotation = 90)
    P.legend(fancybox = True, shadow = True, numpoints  = 1)
    P.savefig(nm + '.pdf')
    P.close()