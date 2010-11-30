#! /sw/bin/python
'''
Created on Jul 24, 2009

@author: Sami-Matias Niemi
'''

import glob as G
import pyfits as PF

fl = G.glob('*_x1d.fits')
sfl = G.glob('*_x1dsum.fits')

str = ''

for file in fl:
    try:
        fh = PF.open(file)
        hdr0 = fh[0].header
        fh.close()
    except:
        print 'Cannot open file %s...' % file

    if hdr0['DETECTOR'].strip() == 'FUV':
    
        if hdr0['SEGMENT'].strip() != 'BOTH':
            print 'ERROR: File %s has SEGMENT value:' % file
            print hdr0['SEGMENT']
        else:
            print 'File %s, SEGMENT value: %s' % (file, hdr0['SEGMENT'])
            
        if hdr0.has_key('WAVECALS'):
            print 'File %s, WAVECALS value: %s' % (file, hdr0['WAVECALS'])
        str = str + file[:8] + ', '

print 'Following x1d related data sets were tested:', str[:-2]

str = ''

for sfile in sfl:
    try:
        fhs = PF.open(sfile)
        hdrs0 = fhs[0].header
        fhs.close()
    except:
        print 'Cannot open file %s...' % sfile

    if hdr0['DETECTOR'].strip() == 'FUV':
        
        if hdrs0.has_key('SEGMENT'):
            print 'ERROR: File %s has SEGMENT value: %s' % (sfile, hdrs0['SEGMENT'])     
        else:
            print 'File %s does not have SEGMENT keyword in the primary header (as should be)' % sfile
    
        if hdrs0.has_key('WAVECALS'):
            print 'File %s has WAVECALS value: %s' % (sfile, hdrs0['WAVECALS'])     
        else:
            print 'File %s does not have WAVECALS keyword in the primary header (as should be)' % sfile
        str = str + sfile[:8] + ', '

print 'Following x1dsum related data sets were tested:', str[:-2]
