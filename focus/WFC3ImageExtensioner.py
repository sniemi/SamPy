#! /usr/bin/env python
'''
Created on Apr 15, 2010

@author: Sami-Matias Niemi (niemi@stsci.edu)
@version: 0.1
'''

import pyfits as PF
import numpy as N
import glob as g

#try to open the template, will exit if not possible
#TODO change this, actually don't need the data, just the shape...
template = '/grp/hst/OTA/focus/Data/prop11877/visit09-jan2010/ibcy09usq_flt.fits'
try:
    tempdata = PF.open(template)[1].data
    tempdata = N.zeros(tempdata.shape)
except:
    print 'Cannot open template file %s' % template
    import sys
    sys.exit('Will exit now')

#find all suitable wfc3 files
wfc3files = g.glob('i*_flt.fits')

#array holders
uvis1 = []
uvis2 = []

#make full frame data file
for file in wfc3files:
    print 'processing file %s' % file
    #open file handler and read data and headers
    fh = PF.open(file, 'update')
    data = fh[1].data
    hd0 = fh[0].header
    hd = fh[1].header
    
    xstart = hd['LTV1'] #offset in X to subsection start
    ystart = hd['LTV2'] #offset in Y to subsection start
    apert = hd0['APERTURE'] #UVIS1 / 2
    
    #make integers
    xstart = int(round(xstart))
    ystart = int(round(ystart))
    
    #check out the shape of the subarray
    y, x = data.shape
    
    #assign the data to the temp array to a right place
    tempdata[-ystart: y - ystart, -xstart: x - xstart] = data
    fh[1].data = tempdata
    
    #check which chip was used
    if 'UVIS1' in apert:
        uvis1.append(file)
        hdu = PF.ImageHDU(data = tempdata, header = hd, name='SCI')
        fh.append(hdu)
    elif 'UVIS2' in apert:
        uvis2.append(file)
    else: print 'Error with file %s' % file
    
    #fh.writeto(file[:-5] + '_mod.fits') 
    fh.close()
    print 'file %s has been updated' % file
    #print 'New file %s created' % (file[:-5] + '_mod.fits')
 
#create file lists
fh1 = open('WFC3UVIS1', 'w')
fh2 = open('WFC3UVIS2', 'w')
#for x in uvis1: fh1.write(x[:-5] + '_mod\n')
#for x in uvis2: fh2.write(x[:-5] + '_mod\n')
for x in uvis1: fh1.write(x[:-5] + '\n')
for x in uvis2: fh2.write(x[:-5] + '\n')
fh1.close()
fh2.close()
