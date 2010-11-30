#! /usr/bin/env python
'''
Created on Jul 22, 2009

@author: Sami-Matias Niemi
'''

import pyfits as PF
import sys
import glob as G

filelist = G.glob(sys.argv[1])

omitlist = ['FLATCORR',                  
            'DEADCORR',                
            'DQICORR',
            'DOPPCORR',
            'HELCORR',
            'X1DCORR',
            'BACKCORR',
            'FLUXCORR',
            'BRSTCORR',
            'TDSCORR',
            'PHOTCORR']

#for STIS:
#BLEVCORR= 'PERFORM '           / subtract bias level computed from overscan img 
#BIASCORR= 'PERFORM '           / Subtract bias image                            
#CRCORR  = 'PERFORM '           / combine observations to reject cosmic rays     
#EXPSCORR= 'PERFORM '           / process individual observations after cr-reject
#DARKCORR= 'PERFORM '           / Subtract dark image                       
#DISPCORR= 'PERFORM '           / apply 2-dimensional dispersion solutions
#CTECORR = 'PERFORM '           / correction for CCD charge transfer inefficiency
#X2DCORR = 'PERFORM '           / rectify 2-D spectral image     

performlist = ['WAVECORR']

for file in filelist:
    fd = PF.open(file, mode='update')
    phdr = fd[0].header
    hdr = fd[1].header

    for omit in omitlist:
        phdr.update(omit, 'OMIT')
    for per in performlist:
        phdr.update(per, 'PERFORM')
    fd.close()
    print 'Keywords of file %s have been modified...' % file
    
print 'Script ends...'

