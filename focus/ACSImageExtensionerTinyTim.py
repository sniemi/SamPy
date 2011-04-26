#! /usr/bin/env python
'''
Created on March 7, 2011

@author: Sami-Matias Niemi (niemi@stsci.edu)
@version: 0.1
'''
import shutil as s
import pyfits as PF
import numpy as N
import glob as g

def parse_parameterfile(file = './complete_results/parameters.txt'):
    out = {}
    #read data
    pdata = open(file).readlines()
    #loop over data
    for line in pdata:
        if 'Chip' in line:
            chip = line.split('|')[1].strip()
            out['CHIP'] = chip
        if 'Position' in line:
            pos = line.split('|')[1].split()
            out['LTV1'] = -float(pos[0])
            out['LTV2'] = -float(pos[1])
        if 'Filter' in line:
            filt = line.split('|')[1].strip()
            out['FILTER'] = filt
        if 'Camera' in line:
            apr = line.split('|')[1].split()[0]
            out['APERTURE'] = apr
    return out

if __name__ == '__main__':

    # file assignment
    file = 'result00.fits'
    output = 'jTinyTimPSF.fits'

    #try to open the template, will exit if not possible
    #TODO change this, actually don't need the data, just the shape...
    template = '/grp/hst/OTA/focus/Data/prop11877/visit09-jan2010/jbcy09urq_flt.fits'
    try:
        tempdata = PF.open(template)[1].data
        yorg, xorg = tempdata.shape
        tempdata = N.zeros(tempdata.shape, dtype=N.float64)
    except:
        print 'Cannot open template file %s' % template
        import sys
        sys.exit('Will exit now')

    #find all suitable wfc3 files
    wfc3file = g.glob('./complete_results/%s' % file)

    #get data from the parameter file
    prms = parse_parameterfile()

    #make full frame data file
    print 'processing file %s' % file
    #open file handler and read data and headers and close the handler
    fh = PF.open(wfc3file[0])
    data = fh[0].data
    hd0 = fh[0].header
    fh.close()

    #check out the shape of the subarray
    y, x = data.shape
    #add the keys
    print prms
    for key in prms:
        if 'CHIP' in key:
            hd0.update('CCDCHIP', prms[key])
        else:
            hd0.update(key, prms[key])
    hd0.update('EXPTIME', '1')
    hd0.update('EXPSTART', 5.55555e4)
    hd0.update('DATE-OBS', '2015-01-01')
    hd0.update('SIZAXIS1', xorg)
    hd0.update('SIZAXIS2', yorg)
    hd0.update('ORIENTAT', 0.0)
    hd0.update('DETECTOR', 'WFC')


    #set the positions
    xstart = prms['LTV1'] #offset in X to subsection start
    ystart = prms['LTV2'] #offset in Y to subsection start
    apert = prms['APERTURE'] + prms['CHIP']

    #make integers
    xstart = int(round(xstart))
    ystart = int(round(ystart))

    #assign the data to the temp array to a right place
    tempdata[-ystart: y - ystart, -xstart: x - xstart] = 1e5*data

    #check which chip was used
    if '1' in apert:
        #is in extension 4!
        #this is so horrible solution... arggggggh
        hdu = PF.PrimaryHDU(header = hd0)
        hdu1 = PF.ImageHDU(data = N.zeros((1,1), dtype = N.float64), header = hd0, name='SCI')
        hdu2 = PF.ImageHDU(data = N.zeros((1,1), dtype = N.float64), header = hd0, name='SCI')
        hdu3 = PF.ImageHDU(data = N.zeros((1,1), dtype = N.float64), header = hd0, name='SCI')
        hdu4 = PF.ImageHDU(data = tempdata, header = hd0, name='SCI')
        thdulist = PF.HDUList([hdu, hdu1, hdu2, hdu3, hdu4])
    elif '2' in apert:
        hdu = PF.PrimaryHDU(header = hd0)
        hdu1 = PF.ImageHDU(data = tempdata, header = hd0, name='SCI')
        thdulist = PF.HDUList([hdu, hdu1])
    else: print 'Error with file %s' % file

    #write the output
    thdulist.writeto(output)

    print 'All done'
     