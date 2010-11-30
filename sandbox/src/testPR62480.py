#! /sw/bin/python
'''
Created on Jul 24, 2009

@author: Sami-Matias Niemi
'''

import glob as G
import pyfits as PF

fl = G.glob('*.fits')
filelist = [x for x in fl if x.find('_spt.fits') == -1 and x.find('_jnk.fits') == -1]
datasets = G.glob('*rawtag_a.fits')

for file in filelist:
    print 'Prosessing file %s' % file
    try:
        fh = PF.open(file)
        hdr0 = fh[0].header
        hdr1 = fh[1].header
        fh.close()
    except:
        print 'Cannot open file %s...' % file

    if hdr0['DETECTOR'].strip() != 'FUV':
         print 'File %s has not been taken with FUV side... ' % file
        
    notFound = True
    for key in hdr1.ascardlist().keys():
        if 'SP_LOC_C' in key:
            print key, hdr1[key]
            notFound = False
        if 'SP_SLP_C' in key:
            print key, hdr1[key]
            notFound = False
        if 'B_BKG1_C' in key:
            print key, hdr1[key]
            notFound = False
        if 'B_BKG2_C' in key:
            print key, hdr1[key]
            notFound = False
        if 'B_HGT1_C' in key:
            print key, hdr1[key]
            notFound = False
        if 'B_HGT2_C' in key:
            print key, hdr1[key]
            notFound = False
    
    if notFound == False:
        print 'PROBLEM FOUND FROM FILE %s' % file

print 'Following datasets were tested:'
for d in datasets:
    print d[:8]
        