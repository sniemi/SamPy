#! /usr/bin/env python
'''
Created on Dec 2, 2009

@author: niemi
'''
import glob as G
import pylab as P
import pyfits as PF
import numpy as N

smn = './out/'
ralph = './IDLoutput/'

files = G.glob(ralph + 'p*.fits')
final = G.glob(ralph + 'coadd*.fits')

for file in files:
    s = PF.open(smn + file[len(ralph):])[1].data
    r = PF.open(file)[1].data
    
    im = P.imshow(s/r, origin = 'bottom', interpolation = None, vmin = 0.99, vmax=1.01)
    cb = P.colorbar(im, orientation='vertical')
    cb.set_label('Python / IDL')

    P.annotate('STDEV of the ratio %f' % N.std(s/r), xy = (0.5, 0.02), xycoords='figure fraction', ha='center')
    
    P.title(file[len(ralph):])
    P.savefig('./out/' + file[len(ralph):-5] + 'Comp.pdf')
    P.close()
    
for file in final:
    s = PF.open(smn + file[len(ralph):])[1].data
    r = PF.open(file)[1].data
    
    im = P.imshow(s/r, origin = 'bottom', interpolation = None, vmin = 0.99, vmax=1.01)
    cb = P.colorbar(im, orientation='vertical')
    cb.set_label('Python / IDL')

    P.annotate('STDEV of the ratio %f' % N.std(s/r), xy = (0.5, 0.02), xycoords='figure fraction', ha='center')
    
    P.title(file[len(ralph):])
    P.savefig('./out/' + file[len(ralph):-5] + 'Comp.pdf')
    P.close()    