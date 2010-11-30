#! /usr/bin/env python
'''
DESCRIPTION:
This short script pulls out COS data from a fits file
and outputs the data to two ascii files. The first file
contains two columns; pixels and counts, while the other
file has columns; wavelength and counts.

Dispersion solutions are given in the beginning of the script
and should be changed if necessary. Dispersion solutions are 
given for G130M and G160M, for both segments separately.

USAGE:
For example:
python COSFocusOutputs.py "*1dx*.fits"

HISTORY:
Created on Aug 21, 2009

@author: Sami-Matias Niemi
'''

import pyfits as PF
import sys
import glob as G
import matplotlib
matplotlib.rc('text', usetex = True)
import pylab as P
try:
    import scipy.stsci.convolve as C
except:
    import convolve as C

######################################################
#CHANGE THESE IF REQUIRED!
######################################################
#Dispersion coeffs
#G160M/1600/Seg A:
G160MAa0 = 1586.40
G160MAa1 = 0.0122397
#G160M/1600/Seg B:
G160MBa0 = 1398.06
G160MBa1 = 0.0122369
#G130M/1309/Seg A:
G130MAa0 = 1297.67
G130MAa1 = 0.00996572
#G130M/1309/Seg B:
G130MBa0 = 1144.38
G130MBa1 = 0.00996337
######################################################

filelist = G.glob(sys.argv[1])

smoothing = (50,)

for file in filelist:
    fulldata = PF.getdata(file)
    hdr0 = PF.open(file)[0].header
    
    #ydata = data.field('Y')
    ydata = fulldata[0][1]
    xdata = fulldata[0][0]

    #output
    fh = open(file[:-5] + '_pix.dat', 'w')
    fh.write(';pixels counts\n')
    for x,y in zip(xdata, ydata):
        tmp = str(x) + ' ' + str(y) + '\n'
        fh.write(tmp)
    fh.close()

    fh = open(file[:-5] + '_wave.dat', 'w')
    fh.write(';wavelength counts\n')
    #manipulats data
    if hdr0['SEGMENT'] == 'FUVA':
        if hdr0['OPT_ELEM'].strip() == 'G130M':
            wave = G130MAa0 + G130MAa1*xdata
        if hdr0['OPT_ELEM'].strip() == 'G160M':
            wave = G160MAa0 + G160MAa1*xdata
    if hdr0['SEGMENT'] == 'FUVB':
        if hdr0['OPT_ELEM'].strip() == 'G130M':
            wave = G130MBa0 + G130MBa1*xdata
        if hdr0['OPT_ELEM'].strip() == 'G160M':
            wave = G160MBa0 + G160MBa1*xdata

    for wav, y in zip(wave, ydata):
        tmp = str(wav) + ' ' + str(y) + '\n'
        fh.write(tmp)
    fh.close()

    #lets make a plot too
    #smooth = C.boxcar(ydata, smoothing)
    #P.title(file)
    #P.plot(xdata, ydata, label = 'Spectrum')
    #P.plot(xdata, smooth, label = 'Boxcar Smoothed')
    #P.xlabel('Pixels')
    #P.ylabel('Counts')
    #P.savefig(file[:-5] + '_counts.pdf')
    #P.close()

    #P.title(file)
    #P.plot(wave, ydata, label = 'Spectrum')
    #P.plot(wave, smooth, label = 'Boxcar Smoothed')
    #P.xlabel('Wavelength (\AA)')
    #P.ylabel('Counts')
    #P.savefig(file[:-5] + '_wavelength.pdf')

print 'Script ends...'
