#! /usr/bin/env python

import pylab as P
import numpy as N
import glob as g

def readBreathing(file, c2 = 5):
    jul = []
    flat = []
    for line in open(file).readlines():
        if 'Julian' in line: continue
        else:
            t = line.strip().split()
            jul.append(float(t[0]))
            flat.append(float(t[c2]))
                
    return N.array(jul), N.array(flat)

bfiles = g.glob('*/breathing.txt')

c1data = N.loadtxt('FocusWFC3Chip1.txt', skiprows = 1, usecols = (3,4,5))
c2data = N.loadtxt('FocusWFC3Chip2.txt', skiprows = 1, usecols = (3,4,5))

P.errorbar(c1data[:,0], c1data[:,1], yerr = c1data[:,2], label = 'WFC3 UVIS1 focus')
P.errorbar(c2data[:,0], c2data[:,1], yerr = c2data[:,2], label = 'WFC3 UVIS2 focus')

for x in bfiles:
    print x
    jul, flat = readBreathing('./' + x, c2 = 5)
    P.plot(jul, flat)

#P.xlim(55351.5, 55351.6)
P.xlim(55326.7, 55326.8)
#P.xlim(55292.0, 55292.2)

P.ylim(-10, 5)

P.legend()
P.show()
